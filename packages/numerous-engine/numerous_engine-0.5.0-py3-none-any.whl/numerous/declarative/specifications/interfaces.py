from abc import ABC, abstractmethod
from collections import namedtuple
from numerous.declarative.enums import Directions

Channel = namedtuple('Channel', ['value', 'direction'])


class ScopeSpecInterface(ABC):
    pass


class DirectionInterface(ABC):

    def set_direction(self) -> Channel:
        return Channel(self, Directions.SET)

    def get_direction(self) -> Channel:
        return Channel(self, Directions.GET)


class ModuleSpecInterface(ABC):
    pass


class ItemsSpecInterface(ABC):
    pass


class ModuleInterface(ABC):
    pass


class ConnectorInterface(ABC):
    channels: dict

    @abstractmethod
    def instance(self, context: dict):
        pass


class ModuleConnectionsInterface(ABC):
    pass


class EquationSpecInterface(ABC):
    pass


class VariableInterface(ABC):

    @abstractmethod
    def instance(self, context: dict):
        pass
