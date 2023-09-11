""" Types and interfaces frequently used in uun-iot library and apps. """

from abc import ABC, abstractmethod
from typing import Union

ModuleId = str
Numeric = Union[float, int]

class IModule(ABC):
    """ Module interface. All user modules must inherit from this interface. """
    id: str

    @property
    @abstractmethod
    def id(self) -> str:
        pass
