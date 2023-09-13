from typing import Self

from numerous.declarative.connectors.connection import Connection
from numerous.declarative.context_managers import _active_connections
from numerous.declarative.instance import Class
from numerous.declarative.specifications.interfaces import ModuleConnectionsInterface


class ModuleConnections(ModuleConnectionsInterface, Class):
    connections = []

    def __init__(self, *args):
        super(ModuleConnections, self).__init__()

        self._host = None
        self.connections = list(args)

    def __enter__(self):
        _active_connections.set_active_manager_context(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _active_connections.clear_active_manager_context(self)

    def register_connection(self, connection: Connection):
        self.connections.append(connection)

    def _instance_recursive(self, context: dict) -> Self:
        instance = ModuleConnections(*(v.instance(context) for v in self.connections))

        return instance
