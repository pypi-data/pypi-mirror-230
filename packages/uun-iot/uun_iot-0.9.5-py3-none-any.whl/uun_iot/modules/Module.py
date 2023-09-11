from abc import abstractmethod, ABC
from enum import Enum, auto
import logging
from typing import Callable, List, Optional, Any, Union

from uun_iot.utils import module_id, Storage
from uun_iot.typing import IModule

logger = logging.getLogger(__name__)

class ConfigScopeEnum(Enum):
    """ Enumeration for configuration scopes. """

    #: Use the root ``gateway`` key for the module configuration.
    GATEWAY=auto()

    #: Use the ``gateway.moduleId`` key for the module configuration.
    SELF=auto()

class Module(IModule, ABC):
    """ Provides utility functions for modules.

    Class :class:`Module` implements interface :class:`uun_iot.typing.IModule`
    for derived classes automatically. The :attr:`id` attribute is derived from
    the class name using :func:`uun_iot.utils.module_id_from_str`. If the class
    already has the :attr:`id` attribute, keep it.

    The derived classes must call the :class:`Module`'s init function using :func:`super`. Example:

    .. code-block:: python

        from uun_iot import Module
        class TestModule(Module):
            def __init__(self, config, uucmd):
                super().__init__(config=config, uucmd=uucmd)
                self.attribute1 = "value1"

    The utility functions include:

        - configuration management
        - storage management
        - backup and restore of storage to filesystem (useful for power failures)
        - automation for sending storage to uuApp
        - handling of failed send storage actions (useful for unstable internet connection)

    Configuration management:

        Access configuration in easy way as ``self._c("key/subkey/subsubkey")``
        instead of cumbersome ``self._config["key"]["subkey"]["subsubkey"]`` and more.
        See configuration manager :meth:`._config_manager` or its alias :meth:`._c`.

    Storage management:

        An instanced thread-safe :class:`~uun_iot.utils.Storage` is available as
        :attr:`._storage`. The class provides backup and restore to
        JSON files and limiting the storage in number of its entries. If
        enabled, oldest entries will be removed for the sake of newer ones.

    If the derived class does not have the ``_config`` attribute, set it to the
    constructor argument ``config``.

    Args:
        uucmd: function(storage)->failed_send_data to send data to uuApp server
        config: gateway configuration
    """
    #: is set in :meth:`__init__` dynamically according to derived class
    id: str = None

    #: optional uuCmd function for data sending
    _uucmd: Optional[Callable[..., List]]
    #: gateway configuration
    _config: dict

    #: storage facility
    _storage: Storage
    #: is backup to file active?
    __backup: bool

    def __init__(self, config: dict={}, uucmd: Callable[[Any], List]=None):

        self._uucmd = uucmd

        if not hasattr(self, "id") or (hasattr(self, "id") and self.id is None):
            self.id = module_id(self.__class__)

        if not hasattr(self, "_config"):
            self._config = config

        # load backup file with previous data
        # if module is supposed to be backed up
        if "moduleBackupStorage" in self._config and self.id in self._config["moduleBackupStorage"]:
            try:
                backup_path = self._config["moduleBackupStorage"][self.id]["path"]
                storage_limit = self._config["moduleBackupStorage"][self.id]["limit"]
                if not isinstance(storage_limit, int):
                    logger.warning("Configuration for `%s`: "
                    "limit of 'gateway.moduleBackupStorage' must be an integer.",
                    self.id)
                    raise TypeError
            except (KeyError, TypeError):
                backup_path = self._config["moduleBackupStorage"][self.id]
                storage_limit = 0
        else:
            backup_path = None
            storage_limit = 0

        self.__backup = backup_path is not None
        self._storage = Storage(self.id, backup_path, storage_limit)

    def _config_manager(self, key: Optional[str]=None, scope: ConfigScopeEnum=ConfigScopeEnum.SELF) -> Any:
        """ Return configuration key.

        Examples:
            
            Following example JSON configuration file with Python outputs:

            .. code-block:: json
                
                {
                    "gateway": {
                        "testModule1": {
                            "option1": "value1",
                            "structure": {
                                "field1": 1,
                                "field2": {
                                    "nested": 2
                                }
                            }
                        },

                        "testModule2": {
                            "option2": "value2"
                        }
                    }

            .. code-block:: python

                from uun_iot import ConfigScopeEnum

                # inside of a method of class TestModule1 derived from Module
                print(self._c("option1"))
                >>> value1

                print(self._c("structure/field1/nested"))
                >>> 2

                print(self._c("option1", scope=ConfigScopeEnum.SELF))
                >>> value1

                print(self._c("testModule1/option1", scope=ConfigScopeEnum.GATEWAY))
                >>> value1

                print(self._c("testModule2/option2", scope=ConfigScopeEnum.GATEWAY))
                >>> value2

        Args:
            key: specify value of configuration key to read. Set to ``None`` to
                return whole dictionary of corresponding configuration given by
                ``scope``. delimit subdictionaries with ``/`` symbol, ie.
                ``self._c("color/bright/red")`` is the same as
                ``self._c("color")["bright"]["red"]``

            scope: the root of configuration ``scope`` can be any of
                :class:`ConfigScopeEnum`. Defaults to :attr:`ConfigScopeEnum.SELF`,
                ie. ``key`` is taken as a subkey of ``gateway.<moduleId>``.
                Alternatively, specify :attr:`ConfigScopeEnum.GATEWAY` to take
                ``key`` as subkey of ``gateway`` key

        Returns:
            Any: the configuration entry

        Raises:
            KeyError: when a given key does not exist inside the configuration
        """

        mconf = self._config

        if key is None:
            return mconf[self.id] if scope == ConfigScopeEnum.SELF else mconf

        if scope == ConfigScopeEnum.SELF:
            key = self.id + "/" + key

        key_parts = key.split("/")
        for k in key_parts:
            try:
                mconf = mconf[k]
            except KeyError:
                raise KeyError(f"key `{key}` is not present in configuration")

        return mconf

    def _send_data(self, data: Union[List, Any], usecase: Callable=None):
        """Logging wrapper for sending ``data`` with ``usecase`` function.

        Log a message with INFO level with information about the data, then send the data.

        Args:
            data: data to be sent by usecase as ``usecase(data)``
            usecase: if ``None``, use stored :attr:`._uucmd`

        Raises:
            TypeError: if ``usecase`` is not specified and ``self._uucmd`` is also not specified
        """
        if usecase is None:
            usecase = self._uucmd
        if usecase is None:
            raise TypeError(f"No usecase was specified and the module `{self.id}` "
                "has no stored uucmd." )

        try:
            length = len(data)
            logger.info("Sending data object for `%s` with [%i] entries", self.id, length)
        except TypeError:
            logger.info("Sending data object for `%s`", self.id)

        usecase(data)

    def _send_storage(self, usecase: Optional[Callable[[List], List]]=None):
        """ Sends entire storage of module to uuApp via ``usecase`` or stored :attr:`uucmd`.

        The ``usecase`` takes data and outputs items which failed to be sent.
        This method saves these failed attempts to file and retries again
        together with new data on next envocation. Only failed entries will be
        saved to the backup file. This functionality is independent on the
        backup functionality.

        Args:
            usecase: function ``List->List`` with one argument taking the data
            to be sent and outputting list with items which were not sent. If
            ``None``, use ``self._uucmd``

        Raises:
            TypeError: if ``usecase`` is not specified and ``self._uucmd`` is also not specified
        """

        if self._storage.is_empty():
            # no data to send
            return

        if usecase is None:
            usecase = self._uucmd
        if usecase is None:
            raise TypeError(f"No usecase was specified and the module `{self.id}` "
                "has no stored uucmd." )

        # prevent situation, where data are sent, another thread writes data to
        # storage, and (as a consequence of sending data) storage is emptied
        # thus discarding the latest unsent data
        with self._storage.write_lock:
            length = len(self._storage)
            logger.info("Sending storage of `%s` with [%i] entries", self.id, length)

            failed_entries = usecase(self._storage.data)
            self._storage.empty()

        if not self.__backup:
            # do not backup
            return

        if len(failed_entries) == 0:
            # everything was sent
            logger.info("Whole storage of `%s` sent successfully", self.id)
        else:
            # merge the two objects (chronologically) to prevent discarding
            # entries added to ._storage while previus ones were being
            # processed/sent

            # extend the storage with entries of the failed_entries list
            self._storage.merge(failed_entries, new_data=False)
            logger.warning("Could not send %i entries from storage of `%s`",
                    len(failed_entries), self.id)

    _c = _config_manager
