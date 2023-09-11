from enum import IntEnum, auto

class GeneralDiagnosticEvent(IntEnum):
    """ Base class for diagnostic events specified by uun-iot library or user
    applications. Diagnostic events are used to notify HealthCheck about some
    important events in via `HealthCheck.notify`. If user application needs
    more diagnostic events, inherit from this class. """
    pass

class DiagnosticEvent(GeneralDiagnosticEvent):
    """ General diagnostic events. """

    DIAGNOSTICS_START = auto()
    """ Start of diagnostics. """

    DIAGNOSTICS_STOP = auto()
    """ Stop of diagnostics. """

    TIMER_CALL = auto()
    """ Registered @on(tick) method is called.
    Specify timer ID in custom argument for better debugging purposes. """

    ON_START_CALL = auto()
    """ Registered @on(start) method is called. """

    ON_STOP_CALL = auto()
    """ Registered @on(stop) method is called. """

    ON_UPDATE_CALL = auto()
    """ Registered @on(update) method is called. """


    DATA_RECEIVED = auto()
    """ Module received valid data. """

    DATA_SEND_IMMINENT = auto()
    """ Module is going to send data. Use directly in front of `self._send_storage()` call. """

    DATA_SEND_OK = auto()
    """ Module has sent all data successfully. """

    DATA_SEND_PARTIAL = auto()
    """ Module has sent some data successfully, but some data were not sent. """

    DATA_SEND_FAIL = auto()
    """ Module could not send any data due to an error. """

    DATA_SEND_ATTEMPTED = auto()
    """ Module could not send any data due to an error. """


class GatewayDiagnosticEvent(GeneralDiagnosticEvent):
    """ Events tied directly to the Gateway instance. """

    """ Gateway was started. """
    GATEWAY_START=auto()

    """ Gateway was stopped. """
    GATEWAY_STOP=auto()

    """ Gateway received a signal.
    Specify signal type in custom argument for better debugging purposes."""
    GATEWAY_SIGNAL=auto()

