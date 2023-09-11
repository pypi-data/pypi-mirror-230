"""
Event handler registration using ``@on`` decorator.
"""

from typing import List, Callable, Any, Dict, Union
from .typing import IModule
from .utils import module_id_from_str

#: dict: Global dictionary ``_registered_methods`` is a way to register
#:       modules' event handlers before inicialization of Gateway.
_registered_methods: Union[
        Dict[str, Dict],
        Dict[str, Dict[str, Callable]],
        Dict[str, Dict[str, Dict[str, Callable]]]
    ]
_registered_methods = {
    'on_tick': {},
    'on_update': {},
    'on_start': {},
    'on_stop': {},
}

# Exception for specifying unknown event in `on()` function
class UnsupportedEvent(Exception):
    """ Unknown gateway event. """

def _filter_registered_methods(module_names: List[str]):
    """Delete event handlers, which do not come from given list ``module_names``.

    The non-present event handlers are removed from :attr:`~uun_iot.decorators._registered_methods`.
    This is used internally to clear some remnants of mass importing (for ex. when testing).

    Args:
        module_names: list of module IDs. Any event handlers not belonging to
            these modules will be deleted from :attr:`~uun_iot.decorators._registered_methods`.
    """
    to_delete = []
    for event_types, event_handlers in _registered_methods.items():
        for module_name in event_handlers.keys():
            if module_name not in module_names:
                to_delete.append((event_types, module_name))

    for event_types, module_name in to_delete:
        del _registered_methods[event_types][module_name]

def _unbound_function(f: Callable) -> Callable:
    """
    If the function :func:`f` is bounded (ie. it is a method in some object instance,
    unbound it and return it. Otherwise, return original :func:`f`.
    """
    if hasattr(f, "__self__"):
        f = f.__func__
    return f

def _get_module_id_from_method(f: Callable) -> str:
    """
    Get corresponding class/module name of the passed method/function and get module ID
    using :func:`uun_iot.utils.module_id_from_str`. If the method
    is bound, return class name of the bound `self` object.

    Args:
        f: method belonging to class instance, alternatively a function belonging to Python module

    Returns:
        str: Module id to which the method belongs, alternatively a module id
        of Python module to which the function belongs
    """
    if hasattr(f, "__self__"):
        # f is a bound method (self argument is automatically prefilled)
        clsname = f.__self__.__class__.__name__
        if isinstance(f.__self__, IModule):
            return f.__self__.id
    else:
        clsname = f.__qualname__.split('.')[-2]
    mid = module_id_from_str(clsname) #clsname[0].lower() + clsname[1:]
    return mid

def on(*outer_args):
    """ Decorator for event handler registration.

    Synopsis: ``on(event[,id])``

    Supported events: ``tick``, ``update``, ``start``, ``stop``.

    ============= =======================================
        event                   description              
    ============= =======================================
     ``update``    gateway's configuration was updated   
     ``tick``      timer tick (configured in JSON)       
     ``start``     `Gateway` just started (using :meth:`~uun_iot.Gateway.Gateway.start`)
     ``stop``      `Gateway` is stopping (using :meth:`~uun_iot.Gateway.Gateway.stop`), end module's action as soon as possible
    ============= =======================================

        - ``tick`` event can take another argument to specify the timer id 
          (see ``gateway.moduleTimers`` key in configuration JSON), ie. ``on(fn)``,
          or  ``on(fn, "timerId")`` with :func:`fn` being the handler function.

    Handlers registered for the corresponding event with this decorator will be
    called on corresponding event by :class:`~uun_iot.Gateway.Gateway` or
    :class:`~uun_iot.Gateway.Config` objects. Passed arguments are different for each
    event and the methods have to take these arguments. Note: ``self`` denotes
    method's module instance, `origin` indicates which module initiates the event


    ============= ======================= ===================================
        event       handler synopsis             origin           
    ============= ======================= ===================================
     ``update``    ``handler(self)``        :class:`~uun_iot.Gateway.Config`   
     ``tick``      ``handler(self)``        :class:`~uun_iot.Gateway.Gateway`  
     ``start``     ``handler(self, evs)``   :class:`~uun_iot.Gateway.Gateway`   
     ``stop``      ``handler(self)``        :class:`~uun_iot.Gateway.Gateway`   
    ============= ======================= ===================================

    where ``evs = (g.runev, g.stopev)`` is a tuple of :class:`threading.Event`
    attributes :attr:`~uun_iot.Gateway.Gateway.runev` and
    :attr:`~uun_iot.Gateway.Gateway.stopev`. Here, ``g`` is the corresponding
    :class:`~uun_iot.Gateway.Gateway` instance.

    Note:

        In a typical use case, `@on` decorators are invoked on method/class definition,
        not at run-time. This can be seen on examples below.

    Examples:

        - ``timer`` event without ID

            - configuration:

                .. code-block:: json

                    {
                        "gateway": {
                            "moduleTimers": {
                                "timerModule": 1
                            }
                        }
                    }

            .. code-block:: python


                from uun_iot import on, Module
                class TimerModule(Module):
                    @on("tick")
                    def periodical(self):
                        print("Tick tock every 1 s.")

        - ``timer`` event with ID

            - configuration

                .. code-block:: json

                    {
                        "gateway": {
                            "moduleTimers": {
                                "sendReceive": {
                                    "send": 2,
                                    "get": 1
                                }
                            }
                        }
                    }

            .. code-block:: python

                class SendReceive(Module):
                    @on("tick", "get")
                    def get(self):
                        print(f"Retrieving data...")

                    @on("tick", "send")
                    def send(self):
                        print(f"Sending data...")

        - ``start`` event

            - configuration:

                .. code-block:: json

                    {
                        "gateway": {}
                    }

            .. code-block:: python

                class AdvancedDataMeasurement(Module):
                    @on("start")
                    def oneshot(self, evs):
                        runev, stopev = evs
                        while runev.is_set():
                            print("Polling for voltage reading from voltmeter...")
                            data = 53.8
                            if data > 50:
                                time.sleep(1)
                            else:
                                time.sleep(1.5)
                                print(data)

    Warning:

        *Dev note TODO.* Is method unbounding needed?
        Why is the decorated method being unbound here in the first place?

    Args:
        event (str): one of ``tick``, ``update``, ``start``, ``stop``
        id (str): optional, ID of the corresponding event, when more are
            specified in configuration JSON
    """
    eventarg = outer_args[0]
    event = "on_" + eventarg
    def wrapper(f):
        module_id = _get_module_id_from_method(f)
        f = _unbound_function(f)
        if event in _registered_methods.keys():
            if event == 'on_tick' and len(outer_args[1:]) == 1:
                _on_tick_id(f, outer_args[1])
            else:
                _registered_methods[event][module_id] = f
        else:
            raise UnsupportedEvent(f"Event type '{eventarg}' is not recognized. "
                    "Known events are:"
                    f"`{[k.replace('on_','') for k in _registered_methods]}`.")
        return f
    return wrapper

def _on_tick_id(f: Callable, timer_id: str):
    """
    Do not use directly! Use `@on(event)` instead. Registers a timer with specified id.

    If ``@on("tick")`` was already defined without ID, undefine the old handler.

    Args:
        f: Handler for the ``tick`` event.
        timer_id: ID of the timer as specified in configuration JSON

    """
    mid = _get_module_id_from_method(f)
    try:
        _registered_methods['on_tick'][mid][timer_id] = f
    except (TypeError, KeyError):
        # TypeError: storage was previously initialized with on("tick")
        #   - delete storage and save only this one
        # KeyError: storage is not yet initialized for `id`
        _registered_methods['on_tick'][mid] = {}
        _registered_methods['on_tick'][mid][timer_id] = f
