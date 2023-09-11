from typing import Dict, List
from threading import Lock, Event
import signal
import os
import datetime
import logging

from uun_iot import on
from uun_iot.typing import ModuleId
from uun_iot.diagnostic import GeneralDiagnosticEvent, DiagnosticEvent, GatewayDiagnosticEvent
from .Module import Module

logger = logging.getLogger(__name__)

class BaseHealthCheck(Module):
    """ Base class for creating runtime consistency checks and debug diagnostics.

    HealthCheck modules can log incoming events and act correspondingly, ie. a
    HealthCheck module can restart application if the app is not working
    correctly and log more debugging information for further analysis.

    This can be useful for detecting anomalous cases when the app is not
    working correctly due to an unknown bug, typically when the bug occurs at
    weird edge cases in long running apps. At the same time, it allows to
    recover from the case (by restarting) and to collect diagnostic info.

    HealthCheck can monitor multiple modules at the same time. This is done
    using ``@on("tick", "moduleId")`` timers.

    The monitored modules need to explicitly send information to the
    HealthCheck module as this cannot always be automatized.

    Event informations are submitted by monitored modules via :meth:`.notify` method
    in a form of :class:`uun_iot.diagnostic.GeneralDiagnosticEvents`.

    BaseHealthCheck only provides infrastructure for storing these events and
    it is upto app-specific HealthCheck to implement neccessary logic for
    determining malfunctioning app states. Although, some helper functions for
    usual cases are already present in BaseHealthCheck
    (:meth:`._act_if_data_not_sent`).

    BaseHealthCheck can register basic @on methods automatically. This is
    useful, as most of derived HealthCheck modules will need
    `save_all_diagnostics` registered as `@on(stop)` and `_init_module_config`
    registered as `@on(update)` for updating module-specific leeways etc.

    Sample gconfig:

    .. code-block:: json

         {
            "moduleTimers": {
                "healthCheck": {
                    "weatherConditions": 300
                }
            }

            "healthCheck": {
                "diagnosticPath": "diagnostics/",
                "modules": {
                    "weatherConditions": {
                        "leeway": 120
                    }
                }
            }
        }

    Leeways should be sufficiently large (larger than watched module's timers),
    so that the module can do its function well. Only module-level configuration
    is dynamically updateable: leeways, 

    Args:
        gconfig (dict): gateway configuration
        on_stop (bool): default True, assign ``@on("stop")`` decorator
            to :meth:`._save_all_diagnostics`
        on_update (bool): default True, assign `@on("update")` decorator
            to :meth:`._init_module_config`
    """

    _start_date: datetime.datetime
    _leeways: Dict[ModuleId, datetime.timedelta]
    _diagnostic_active: Dict[ModuleId, Event]
    _diagnostic_log: Dict[ModuleId, List]
    _event_dates: Dict[ModuleId, Dict[GeneralDiagnosticEvent, datetime.datetime]]
    _diagnostic_lock: Dict[ModuleId, Lock]
    _diagnostics_save_path: str

    def __init__(self, gconfig: dict, on_stop: bool=True, on_update: bool=True):
        """
        """
        super().__init__(config=gconfig)

        self._diagnostics_save_path = self._c("diagnosticsPath").rstrip("/")

        self._diagnostic_lock = {
                mid: Lock() for mid in self._c("modules") 
            }

        self._diagnostic_active = {
                mid: Event() for mid in self._c("modules")
            }

        self._diagnostic_log = {
                mid: [] for mid in self._c("modules")
            }

        self._event_dates = {
                mid: {} for mid in self._c("modules") 
            }
        # global information about Gateway, Event can be any of GatewayDiagnosticEvent
        self._event_dates["gateway"] = {}
        self.notify("gateway", GatewayDiagnosticEvent.GATEWAY_START)
        # alias for quick access, start time of gateway
        self._start_date = self._event_dates["gateway"][GatewayDiagnosticEvent.GATEWAY_START]

        self._init_module_config()

        self._stop_diagnostic = self.save_diagnostic

        if on_stop:
            on("stop")(self.save_all_diagnostics)
        if on_update:
            on("update")(self._init_module_config)

    def _init_module_config(self):
        """ Initialize module-specific configuration of monitored modules from configuration.
        Ie. everything under `modules.<moduleId>.*` configuration.
        Currently only leeways."""
        self._leeways = {
                mid: datetime.timedelta(seconds=self._c(f"modules/{mid}/leeway")) for mid in self._c("modules")
            }

    def notifier(self, mid: ModuleId):
        """ Return a :meth:`.notify` method with prefilled ``mid`` argument.

        Args:
            mid: module ID
        """
        return lambda *args, **kwargs: self.notify(mid, *args, **kwargs)

    def notify(self, mid: ModuleId, event: GeneralDiagnosticEvent, *args, **kwargs):
        """Notify HealthCheck about watched modules' events.

        Optionally, add more custom data about the event in form of additional
        ``*args`` or ``**kwargs``.

        Args:
            mid: watched module ID
            event: GeneralDiagnosticEvent representing what action was done
            \*args: other positional arguments for logging purposes
            \*\*kwargs: other keyword arguments for logging purposes
        """
        now = datetime.datetime.now()
        if not mid in self._event_dates:
            raise ValueError("Module is not listed in HealthCheck's configuration. Add it there first.")
        if not isinstance(event, GeneralDiagnosticEvent):
            raise ValueError("Event should inherit from uun_iot.diagnostic.GeneralDiagnosticEvents.")

        self._event_dates[mid][event] = now

        if mid in self._diagnostic_active and self._diagnostic_active[mid].is_set():
            entry = (now, event.name, (args, kwargs))
            with self._diagnostic_lock[mid]:
                self._diagnostic_log[mid].append(entry)

    def start_diagnostic(self, mid):
        """ Start logging incoming events for module `mid`. """
        self._event_dates[mid][DiagnosticEvent.DIAGNOSTICS_START] = datetime.datetime.now()
        self._diagnostic_active[mid].set()

    def save_all_diagnostics(self):
        """ Stop all diagnostics and save them to files. """
        for mid in self._c("modules"):
            self.save_diagnostic(mid)

    def save_diagnostic(self, mid):
        """ Stop logging incoming events for `mid` and save them to file. """
        with self._diagnostic_lock[mid]:
            if not self._diagnostic_active[mid].is_set():
                return

            try:
                logger.info(f"Saving diagnostic of module {mid}.")

                dname = self._diagnostics_save_path
                mdname = f"{dname}/{mid}"
                os.makedirs(dname, exist_ok=True)
                os.makedirs(mdname, exist_ok=True)

                stop_d = datetime.datetime.now()
                self._event_dates[mid][DiagnosticEvent.DIAGNOSTICS_STOP] = stop_d

                # weatherConditions_2021-09-26_19-02-56UTC
                # diagnostic file creation
                start_d = self._event_dates[mid][DiagnosticEvent.DIAGNOSTICS_STOP].strftime("%Y-%m-%d_%H-%M-%S%Z")
                extension = "log"
                fname = f"{mid}_diagnostic_{start_d}"

                # find a nonused fname
                i = 0
                while os.path.exists(f"{mdname}/{fname}.{extension}"):
                    i+=1
                    fname = fname.split(".")[0] + f".{i}"
                fname = f"{mdname}/{fname}.{extension}"
                
                dlog = self._diagnostic_log[mid]
                with open(fname, "w") as f:
                    infile_date_format = "%Y-%m-%d %H.%M.%S.%f %Z"
                    start_d = self._event_dates[mid][DiagnosticEvent.DIAGNOSTICS_START].strftime(infile_date_format)
                    stop_d = stop_d.strftime(infile_date_format)
                    f.write(f"Diagnostics of module {mid}\nStarts at: {start_d}\nEnds at:   {stop_d}\n\n")

                    if dlog == []:
                        f.write(f"No data were collected (HealthCheck notifiers were not reached in target code)\n")
                    else:
                        for d in dlog:
                            date = d[0].strftime(infile_date_format)
                            event = d[1]
                            arg = d[2]
                            if arg is None or arg == ((), {}):
                                f.write(f"{date}: {event}\n")
                            else:
                                args = arg[0]
                                kwargs = arg[1]
                                sa = ", ".join(list(map(str, args)))
                                sk = ", ".join([f"{k}={v}" for k,v in kwargs.items()])
                                if sa == "":
                                    f.write(f"{date}: {event} - {sk}\n")
                                else:
                                    f.write(f"{date}: {event} - {sa}; {sk}\n")


                self._diagnostic_log[mid] = []
                self._diagnostic_active[mid].clear()
            except Exception as e:
                print("_diagnostic_log[mid]: ", self._diagnostic_log[mid])
                print("_diagnostic_active[mid]", self._diagnostic_active[mid])
                print("_diagnostic_lock[mid]", self._diagnostic_lock[mid])

                self._diagnostic_log[mid] = []
                self._diagnostic_active[mid].clear()

                logger.error("Error occured while saving diagnostics:")
                raise e

    def _exit_app(self):
        # signal SIGUSR1 to itself
        # Gateway will handle it and gracefully exit the whole app
        self.notify("gateway", GatewayDiagnosticEvent.GATEWAY_SIGNAL, "SIGUSR1")
        os.kill(os.getpid(), signal.SIGUSR1)

    def _act_if_data_not_sent(self, mid: ModuleId, send_leeway: datetime.timedelta, now: datetime.datetime):
        """
        Check if module (usually its uucmd send handler) sent data in time
        interval (now-send_leeway[mid], now).

        If yes, save any current running diagnostic for `mid`. If not, run
        diagnostic - or - shutdown the application, if diagnostic is already
        running.

        Note:
            Even if the module has no data to send, this will flag it as
            malfunctioning and restart the app.

        Data send event is considered to be DiagnosticEvent.DATA_SEND_ATTEMPTED.
        No internet server communication is needed, only local information.

        .. code-block::

                               <--------> send_leeway
            -*-----------------*----------------------| now
             ^ attempted sends ^

        Args:
            mid: module id
            send_leeway (datetime.timedelta): specified time window (relative
                to now) to check for sent data
            now (datetime.datetime): current time
        """
        start_time = self._event_dates["gateway"][GatewayDiagnosticEvent.GATEWAY_START]

        # this handles the case when data were not yet sent (soon after start of gateway)
        dmin = datetime.datetime.min
        last_attempted_send = self._event_dates[mid].get(DiagnosticEvent.DATA_SEND_ATTEMPTED, dmin)

        if last_attempted_send == dmin:
            last_attempted_send = start_time

        if last_attempted_send + send_leeway < now:
            # Suspicious case:
            # module did not (even) tried sending any data during leeway.
            # gather diagnostic data about the situation and if this case
            # occurs once again, restart the application
            # (this should be solving the problem until the bug is fixed by
            # developer in new app version)
            if self._diagnostic_active[mid].is_set():
                logger.warning("Module `%s` again did not sent any data - exiting app.", mid)
                self._exit_app()
            else:
                logger.warning("HealthCheck detected an error in module `%s`: "
                    "no data are being sent.", mid)
                self.start_diagnostic(mid)
        else:
            # everything is ok now
            logger.debug("HealthCheck did not detect an error in module %s", mid)
            self._stop_diagnostic(mid)


        # ASSUMPTIONS:
        # uucmd handler signals <==> the handler tried
        # (successfully/unsuccessfully) sending data to server

        # OLD:
        # ASSUMPTIONS: uucmd handler signals offline <==> gateway is really offline
        # ie. no bugs in uucmd handler which would cause nothing to be sent,
        # even if the server is accessible
        # ALTERNATIVE approach: send only one signal (do not split into online/offline) in uucmd
        # this nested condition will reduce to only one if (if uucmd fired)
        # online & offline distinction is good for diagnostic only
        # ie. we only need to know IF uucmd handler fired during leeway,
        #     no need to know if it was online or offline

        # note: order of online/offline is irrelevant, what matters is if uucmd fired
        # if lonline + self.leeway < now:
        #     # suspicious case
        #     # this might mean that there has been no internet during leeway
        #     # OR that weathercondition module (WCM) is not sending data (due to some unknown bug)

        #     if loffline + self.leeway < now:
        #         # the WCM has attempted to send data but did not succeed
        #         # (offline state is signalled <=> the WCM uucmd tried to send data)
        #         # ==> there is no internet, nothing to do about it
