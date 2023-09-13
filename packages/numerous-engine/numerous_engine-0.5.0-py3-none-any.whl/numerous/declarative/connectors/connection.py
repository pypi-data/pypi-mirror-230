from typing import Self, Tuple

from numerous.declarative.context_managers import _active_connections
from numerous.declarative.enums import Directions
from numerous.declarative.instance import Class
from numerous.declarative.specifications.interfaces import ConnectorInterface


class Connection(Class):
    """
        A connection is representing two connectors connected
    """

    side1: ConnectorInterface
    side2: ConnectorInterface
    map: dict[str, str]
    directions: dict[str:Directions]
    processed: bool = False

    def __init__(self, side1: ConnectorInterface = None, side2: ConnectorInterface = None, _map: dict = None,
                 directions: dict = None, init: bool = True):
        super(Connection, self).__init__()
        """
            map: dictionary where the keys are channels on side1 and values are channels on side 2
        """
        if init:
            self.side1 = side1
            self.side2 = side2
            self.map = _map
            self.directions = directions

            _active_connections.get_active_manager_context().register_connection(self)

    @property
    def channels(self) -> Tuple:
        for k, v in self.map.items():
            yield k, self.side1.channels[k][0], v, self.side2.channels[v][0], self.directions[k]

    def _instance_recursive(self, context: dict) -> Self:
        instance = Connection(None, None, None, None, False)
        instance.side1 = self.side1.instance(context)
        instance.side2 = self.side2.instance(context)
        instance.directions = self.directions
        instance.map = self.map

        return instance
