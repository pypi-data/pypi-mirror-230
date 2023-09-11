"""
Main Gateway class which manages all user modules.
"""
from typing import Callable, List, Dict, Union
import contextlib
import json
import threading
import sys
import signal
import logging
import requests

from .typing import IModule, Numeric, ModuleId
from .modules import init as init_base_modules
from .UuAppClient import UuAppClient
from .decorators import on, _registered_methods, _filter_registered_methods
from .utils import RepeatTimer

logger = logging.getLogger(__name__)
loggerc = logging.getLogger(__name__ + '.Config')

class ModuleTimer:
    """ Store :class:`~uun_iot.modules.Module.IModule` instance together with its tick event timer(s).

        ``f`` and ``period`` are of type `function` and `float` respectively:

            - ``f``: function to be called on each timer hit (module's method)
            - ``period``: period of the timer in seconds,

        or ``f`` and ``period`` can be either of type `dict` and `dict` respectively,
        indexed by the **same** keys, the keys correspond to timer IDs:

            - ``f``: values of the dictionary are the ``module_instance``'s method
            - ``period``: values are timer periods in seconds.

        Args:
            module_instance: an instantiated :class:`~uun_iot.modules.Module.IModule`
                (for which the timer is created)
            f: method of ``module_instance`` object to be repeatedly called on `tick` event
            period: the `tick` period in seconds

        Raises:
            ValueError: argument type mismatch for `f` and `period`, see above.
    """
    #: ID of passed module
    id: ModuleId
    m_instance: IModule

    #: does timer have multiple subtimers?
    multi: bool
    timer: Union[RepeatTimer, Dict[str, RepeatTimer]]

    def __init__(self,
            module_instance: IModule,
            f: Union[Callable, Dict[str, Callable]],
            period: Union[Numeric, Dict[str, Numeric]]
        ):
        self.m_instance = module_instance
        self.id = module_instance.id

        # timers are now instanced as a registered function (from callback) and
        #   the module instance is passed to it as the `self` argument

        if callable(f) and isinstance(period, (int, float)):
            # single (unnamed) timer
            self.multi = False
            self.timer = RepeatTimer(period, f,
                    kwargs={'self': self.m_instance}
                )
            logger.debug("assigned %ss timer to `%s`", period, self.id)

        elif isinstance(f, dict) and isinstance(period, dict):
            # multiple timers
            self.multi = True
            self.timer = {}
            for timer_id, f_single in f.items():
                try:
                    period_single = period[timer_id]
                except KeyError:
                    logger.error(
                        "Could not find timer `%s:%s` in configuration "
                        "(this module has multiple timers).",
                        self.id, timer_id
                    )
                    continue
                self.timer[timer_id] = RepeatTimer(period_single, f_single,
                        kwargs={'self': self.m_instance}
                    )
                logger.debug("assigned %ss timer to `%s:%s`", period_single, self.id, timer_id)
        else:
            raise ValueError("Argument type mismatch. Arguments `f` and `period` have to "
                    "be of types Callable and float, or Dict[str, Callable] and Dict[str, float]."
                    f"They are `{type(f)}` and `{type(period)}` instead.")


class Gateway(contextlib.AbstractContextManager):
    """Main Gateway class which manages all user modules.

    Gateway is responsible for managing all modules and also manages
    event dispatch and configuration.

    This class is a `ContextManager`. On enter, the :meth:`.start` method is called,
    on leave, the :meth:`.stop` method is called.

    Warning:
        When an exception is thrown inside the ``module_init`` function (usually calling class constructors), it is not supressed and leads to classical exception behaviour (ie. program termination). 

        When an exception is thrown inside a :meth:`~uun_iot.decorators.on` event hook, the exception is catched and printed via logging.

    Examples:

        .. code-block:: python

            from uun_iot import Gateway:
            config_file="config.json"
            with Gateway(config_file) as g:
                while True:
                    time.sleep(1)

        In this example, the :class:`Gateway` is initialized using the
        configuration file in a `with` block. Upon entering, the gateway is
        started. When an exeption occurs, the gateway is gracefully stopped
        using its :meth:`.stop` method -- this allows the `Gateway` to do
        cleanup and inform user modules (here are none) that they should exit,
        too.


    Args:
        config_file: path to configuration JSON file. See :class:`Config` for
            information about format of the file.
        module_init: a function ``(config_dict, uuapp_client) -> List[IModule]``
            or ``(config_dict, uuapp_client) -> IModule`` for single module.
            Here, ``config_dict`` is the dictionary created from JSON ``config_file``
            and ``uuapp_client`` is an instance of :class:`~uun_iot.UuAppClient.UuAppClient`.
            The function is responsible for initializing user modules.
    """

    #: This Event is set when the Gateway :meth:`start`-s and cleared when :meth:`stop`-s.
    runev: threading.Event
    #: This Event is set when the Gateway :meth:`stop`-s and cleared when :meth:`start`-s.
    stopev: threading.Event

    #:class:`Config` instance managed by Gateway
    _config_obj: "Config"
    #: dictionary storing the gateway's configuration
    #: see :attr:`Config.config`
    config: dict

    uuapp_client: UuAppClient

    #: list of managed user modules
    _modules: Dict[ModuleId, IModule]
    #: list of tick event timers
    _timers: List[ModuleTimer]

    def __init__(
            self,
            config_file: str,
            module_init: Union[
                Callable[[dict, UuAppClient], List[IModule]],
                Callable[[dict, UuAppClient], IModule]
                ]=None
        ):

        logger.debug("Starting gateway module system.")

        self.runev = threading.Event()
        self.stopev = threading.Event()

        self._config_obj = Config(self, config_file)
        self.config = self._config_obj.config

        self.uuapp_client = UuAppClient(self.config)
        modules = init_base_modules(self.config, self.uuapp_client)

        # additional modules specific to application
        if module_init:
            mi = module_init(self.config, self.uuapp_client)
            if isinstance(mi, list):
                modules += mi
            else:
                # a single module
                modules += [mi]

        # add Config as an equivalent of module
        # see Config class for further details
        modules.append(self._config_obj)

        self._modules={}
        for m in modules:
            if not hasattr(m, "id") or m.id is None:
                logger.error("A user module does not have attribute 'id' or it "
                             "is set to None! Check that you properly define "
                             "'id' in all modules.")
                exit(1)
            else:
                self._modules[m.id] = m

        # clear some remnants of mass importing (for ex. when testing)
        _filter_registered_methods(list(self._modules.keys()))

        # register `on("update")` callbacks with the Config module which is responsible for updates
        self._config_obj.register_callbacks(self._modules)

        # register timers
        self._init_timers()

        logger.debug("module system initilized")

    def __enter__(self):
        """ Call :meth:`.start`. """
        self.start()
        return self

    def __exit__(self, *exc_info):
        """ Call :meth:`.stop`. """
        self.stop()

    def signal_handler(
            self,
            sig: signal.Signals,
            frame,
            additional_cleanup: Callable[["Gateway"], None]=None
        ):
        """ Handler for predefined signals.

        The following signals are supported:

        =================   ===========
        functionality no.   description
        =================   ===========
        1                   :meth:`.stop` Gateway, ``del`` ete all modules, run ``additional_cleanup`` and exit
        =================   ===========

        =========== =============
        signal      functionality
        =========== =============
        ``SIGINT``  1
        ``SIGTERM`` 1
        ``SIGUSR1`` 1 and exit with error code ``1``
        ``SIGUSR2`` 1
        =========== =============

        The signals need to be explicitly registered with this method being the
        associated handler. Register signals as:

        .. code-block:: python

            import signal
            from uun_iot import Gateway
            with Gateway(...) as g:
                signal.signal(signal.SIGTERM, g.signal_handler)
                ...

        If you want to specify ``additional_cleanup``, define a partial
        function from this method with first two arguments left empty.

        Args:
            sig: caught signal
            frame: exception frame
            additional_cleanup: optional function to be run to cleanup the
                `Gateway`. The function takes the `Gateway` instance as an
                argument.
        """
        logger.debug("Received signal `%s`", signal.Signals(sig).name)
        if sig in [signal.SIGINT, signal.SIGTERM, signal.SIGUSR1, signal.SIGUSR2]:
            # systemd issues SIGTERM to stop a program
            # user defined signal SIGUSR1 -- is issued from some Module to stop gateway and exit
            self.stop()

            # explicitly delete a module before exiting to give it a chance to execute its __del__
            for (mid, module) in self._modules.items():
                del module

            if additional_cleanup is not None:
                additional_cleanup(self)

            ec = sig in [signal.SIGUSR1]
            # SIGUSR1 -- exit with error
            # SIGUSR2 -- exit without error
            sys.exit(int(ec))

    def start(self):
        """Invoke all ``@on("start")`` functions and start all timers.

        This is no-op when the gateway is already started.
        """
        if not self.runev.is_set():
            self.runev.set()
            self.stopev.clear()
            self._invoke_on_start()
            self._start_timers()

    def stop(self):
        """
        Invoke all ``@on("stop")`` functions and peacefully stop (wait to finish)
        all timers and associated ``@on("tick")`` handlers.

        This is no-op when the gateway is already stopped.
        """

        # this also stops on_start function (oneshots) polling for the event
        if self.runev.is_set():
            self.runev.clear()
            self.stopev.set()
            self._invoke_on_stop()
            self._stop_timers()

    def _init_timers(self):
        """ Initialize tick event timers with interval(s) from configuration. """
        self._timers = {}
        for (mid, module) in self._modules.items():
            try:
                interval = self.config["gateway"]["moduleTimers"][mid]
            except KeyError:
                # module not present in configuration
                logger.info("The initialized module `%s` has no corresponding timer configuration "
                "entry. Did you forget to make a configuration entry for its timer?", mid)

                logger.debug("Disabling timer for module `%s`", mid)
                continue

            callback = _registered_methods['on_tick'][mid]
            self._timers[mid] = ModuleTimer(module, callback, interval)

    def _start_timers(self):
        """
        Start tick event timers for modules.
        """
        for mid, m_timer in self._timers.items(): #module_id, module_timer object
            if m_timer.multi:
                for tid, timer in m_timer.timer.items():
                    timer.start()
                    logger.debug("Timer `%s:%s` started.", mid, tid)
            else:
                m_timer.timer.start()
                logger.debug("Timer `%s` started.", mid)

    def _stop_timers(self):
        """
        Stop timers for modules.
        """
        for mid, m_timer in self._timers.items():
            if m_timer.multi:
                for tid, timer in m_timer.timer.items():
                    timer.stop()
            else:
                m_timer.timer.stop()

    def _invoke_on_start(self):
        """ Start each of ``@on("start")`` methods in its own thread. """
        for mid, func in _registered_methods["on_start"].items():
            # do not store the thread to kill it later, rely solely on the func
            #   to terminate itself when runev Event is unset
            logger.debug("Calling @on('start') function `%s`", func)
            threading.Thread(
                    target=func,
                    args=(self._modules[mid], (self.runev, self.stopev)) # self, (runev, stopev)
                ).start()
    def _invoke_on_stop(self):
        """ Start each of ``@on('stop')`` methods in its own thread. """
        for mid, func in _registered_methods["on_stop"].items():
            logger.debug("Calling ``@on('stop')`` function `%s`", func)
            threading.Thread(
                    target=func,
                    args=(self._modules[mid],) # self
                ).start()

# Class Config is in the same file as Gateway due to intimate connection of the two.
# Split would result in cyclic import or unneccesarry generalization in rest of
# the code only for this one case.
class Config(IModule):
    """ Configuration module.

    The preffered styling of the JSON keys is ``camelCase``, ie. first letter
    lowercase, letters after spaces uppercase and finally, the spaces removed.

    The JSON configuration file has the following example structure:

    .. code-block:: json
        :force:

        {
            "gateway": {

                "moduleTimers": {
                    "customModule1": {
                        "receive": 120,
                        "send": 400
                    },
                    "customModule2": 60
                },

                "moduleBackupStorage": {
                    "customModule1": "backup/customModule1.json",
                    "customModule2": {
                        "path": "backup/customModule2.json",
                        "limit": 50
                    }
                },

                "customModule2": {
                    "option1": "value1"
                }
            },

            "uuApp": { ... },
            "uuThing": { ... },
            "oidcGrantToken": { ... }
        }

    On the other hand, a **minimal** configuration file is an empty JSON file:

    .. code-block:: json

        {}

    Meaningful keys and subkeys are:

        - ``gateway``: `optional`. Main configuration for this IoT application

            - ``moduleTimers``: `optional`. Core functionality, dictionary with
              periods (in seconds) for ``@on("tick")`` events for corresponding
              modules. The module IDs are keys, the periods are values.

                - Multiple timers can be
                  specified by introducing a subobject with the timer ID and the
                  timer period. The timer ID corresponds to the event defined in
                  Python code as ``@on("tick", "timerId")``.

            - ``moduleBackupStorage``: `optional`. Applies to modules based on
              :class:`~uun_iot.modules.Module.Module`. The format is module ID
              as key and file path as value. This key is used to specify
              location to which should unsent data from the module be saved,
              see :class:`~uun_iot.modules.Module.Module` for more information.

                - You can specify additional information, such that the storage
                  should be limited in size. For this, specify the size of the
                  storage in number of entries in ``limit`` and add the
                  original file path in the ``path`` key.

            - ``<moduleId>``: `optional`. A default place for the configuration specific to
              the module with ID ``moduleId``. The structure is arbitrary and
              depends on your needs.

        - keys for :class:`uun_iot.UuAppClient`. `Optional`. See documentation there for
          more information. If you want to use secure communication with uuApp,
          specify the details in keys

            - ``uuApp``
            - ``uuThing``
            - ``oidcGrantToken``



    Args:
        gateway_instance: :class:`Gateway` instance
        config_file: path to configuration JSON file
    """

    id = 'config'

    def __init__(self, gateway_instance: Gateway, config_file: str):
        self.g = gateway_instance
        self._config_file = config_file
        with open(config_file, "r") as f:
            self.config = json.load(f)

        if "gateway" not in self.config:
            self.config["gateway"] = {}

    def _uucmd(self):
        # create uucmd function, separate from other cmd due to nature of Config
        uucmd = self.config["uuApp"]['uuCmdList']['gatewayGetConfiguration']
        r, (ok, err) = self.g.uuapp_client.get(uucmd, log_level=logging.DEBUG)
        if not ok:
            return False
        try:
            new_config = r.json()
            # this is not an actual configuration key, only a remnant of server communication
            if "uuAppErrorMap" in new_config:
                del new_config["uuAppErrorMap"]
            if new_config == {}:
                loggerc.debug("Received empty JSON configuration from server, ignoring.")
                return False
        except json.decoder.JSONDecodeError:
            loggerc.error("Received invalid configuration JSON from server")
            loggerc.debug("Invalid response: %s", r.text)
            return False

        return new_config

    def register_callbacks(self, modules):
        """ Register optional update event callbacks with :class:`Config`. """
        self._callbacks = {}
        for (mid, module) in modules.items():
            if mid in _registered_methods['on_update']:
                # store along with module instance
                self._callbacks[mid] = (_registered_methods['on_update'][mid], module)
                loggerc.debug("Registered update callback for `%s`.", mid)

    @on("tick")
    def on_tick(self):
        """
        Gets new configuration from the uuApp, validates it, restarts timers
        (if needed based on the new configuration) and saves the new
        configuration locally. It also notifies modules (via their
        ``@on("update")``) about configuration update.
        It is triggered by a tick event.
        """

        new_config = self._uucmd()

        if not new_config:
            # did not get a valid configuration
            return

        if new_config != self.config["gateway"]:

            loggerc.debug("Received new configuration from server: %s", new_config)

            # for loop: restart timers if needed
            for id, mt in self.g._timers.items():
                if id not in new_config["moduleTimers"]:
                    continue
                    
                # new timer values are presented
                if self.config["gateway"]["moduleTimers"][id] != new_config["moduleTimers"][id]:

                    if id == "config":
                        # TODO: needs testing if utils.Timer correctly handles setting period without stopping first
                        mt.timer.period = new_config["moduleTimers"][id]
                        loggerc.info(f"experimentally updated `{id}`'s timer to {new_config['moduleTimers'][id]} s")
                        continue

                    if mt.multi:
                        # multiple timers for one module
                        if self.config["gateway"]["moduleTimers"][id].keys() != new_config["moduleTimers"][id].keys():
                            loggerc.error("Update cannot introduce new timer_id for a module, only update timer values.")
                            continue

                        for timer_id, new_interval in new_config["moduleTimers"][id].items():
                            if new_interval != self.config["gateway"]["moduleTimers"][id][timer_id]:
                                mt.timer[timer_id].stop()
                                mt.timer[timer_id].period = new_config["moduleTimers"][id][timer_id]
                                mt.timer[timer_id].runonstart = False
                                mt.timer[timer_id].start()
                                loggerc.info(f"updated `{id}:{timer_id}` timer to {new_config['moduleTimers'][id][timer_id]} s")
                    else:
                        # single timer
                        mt.timer.stop()
                        mt.timer.period = new_config["moduleTimers"][id]
                        mt.timer.runonstart = False
                        mt.timer.start()
                        loggerc.info(f"updated `{id}`'s timer to {new_config['moduleTimers'][id]} s")

            # update config, only gateway key, rest is unchanged

            # PASSIVE CONFIGURATION UPDATE
            # propagated passively to each module
            # modules contain _config in form of config["gateway"] assigned at module's init
            #   (other keys are not needed and only cause more typing)
            
            # DOES NOT WORK:
            # cannot do `self.config["gateway"] = new_config` as it would not change the config["gateway"] dict present in each module:
            # self.config["gateway"]           --> { 'module_1' --> module_1_data_old, ... }
            # self.config["gateway"] --(update)--> { 'module_1' --> module_1_data_new, ... }
            # (some_module)._config            --> { 'module_1' --> module_1_data_old, ... } as
            #   it was never reassigned inside the module
            
            # DOES WORK:
            # update every key(pointer) in config["gateway"] separately; module's _config still points to the same config["gateway"]
            #   but every key inside config["gateway"] is correctly updated
            # self.config["gateway"] --> { 'module_1'           --> module_1_data_old, ... }
            # self.config["gateway"] --> { 'module_1' --(update)--> module_1_data_new, ... }
            # (some_module)._config  --> { 'module_1'           --> module_1_data_new, ... } as 
            #   the module's config and self.config["gateway"] point to the same (updated object)
            
            # new update cannot introduce new keys to ["gateway"] (which is to be expected -- cannot create objects at run-time without any defining code)
            updated_values = False
            for key in self.config["gateway"]:

                if key not in new_config:
                    loggerc.warning("Update does not contain a configuration key `%s`. Update is not deleting this key from current configuration but it will be deleted on next run of application.", key)
                    continue

                if self.config["gateway"][key] != new_config[key]:
                    updated_values = True
                    loggerc.debug("changed key `%s` from %s to %s", key, self.config["gateway"][key],  new_config[key])
                    self.config["gateway"][key] = new_config[key]

            if not updated_values: 
                loggerc.debug("New configuration introduced only new keys not present on old config, discarding update.")
                return

            # allow module callbacks to alter the configuration before saving to disk
            self._invoke_update_callback()

            # save updated config to file in case of power outage/app restart
            with open(self._config_file, 'w') as f:
                f.write(json.dumps(self.config, indent=4)) # pretty print in case of manual editing

            loggerc.info("Updated configuration.")

    def _invoke_update_callback(self):
        """ Notify all modules (which support it) about configuration change. """
        for id, (callback, m_instance) in self._callbacks.items():
            threading.Thread(
                    target=callback,
                    args=(m_instance,)
                ).start()

