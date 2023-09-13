from typing import Self

from numerous.declarative.connectors.create_connections import create_connections
from numerous.declarative.connectors.connection import Connection
from numerous.declarative.enums import reversed_direction
from numerous.declarative.exceptions import AlreadyConnectedError
from numerous.declarative.instance import Class
from numerous.declarative.specifications.interfaces import ModuleSpecInterface, ConnectorInterface, ModuleInterface, \
    VariableInterface, Channel


class DeclarativeConnector(Class, ConnectorInterface):

    def __init__(self, optional=False, **kwargs):
        super().__init__()
        self.channels = kwargs
        self.optional = optional
        self.connection = None
        self.module_connections = None
        self.directions = {}
        self.validate_channels()

    def validate_channels(self):
        for name, channel in self.channels.items():
            if not isinstance(channel, Channel):
                raise TypeError(
                    f"Channel '{name}' must be a tuple. Did you miss a call to get_value_for or set_value_from?")
            setattr(self, name, channel.value)

    def _instance_recursive(self, context: dict) -> Self:
        instance_channels = {name: Channel(channel.value.instance(context), channel.direction) for name, channel in
                             self.channels.items()}
        instance = DeclarativeConnector(optional=self.optional, **instance_channels)
        return instance

    def connect(self, other: ConnectorInterface, _map: dict = None):
        with create_connections() as module_connections:
            self.directions = {}
            _map = _map or {key: key for key in other.channels.keys()}
            self.check_if_already_connected()
            self.check_connection_validity(other, _map)
            self.connection = Connection(self, other, _map, self.directions)
        self.module_connections = module_connections

    def check_if_already_connected(self):
        if self.connection:
            raise AlreadyConnectedError()

    def check_connection_validity(self, other: ConnectorInterface, map: dict):

        for other_key, self_key in map.items():
            self.check_channel_types(other, self_key, other_key)
            self.check_channel_signals(other, self_key, other_key)
            self.check_channel_directions(other, self_key, other_key)

    def check_channel_types(self, other: ConnectorInterface, self_key: str, other_key: str):
        other_channel = other.channels[other_key].value
        self_channel = self.channels[self_key].value
        if not (
                isinstance(other_channel, (ModuleInterface, ModuleSpecInterface)) and isinstance(self_channel, (
                ModuleInterface, ModuleSpecInterface)) or
                isinstance(other_channel, (VariableInterface,)) and isinstance(self_channel, (VariableInterface,))
        ):
            raise TypeError(f"Cannot connect channel different types {self_channel} != {other_channel}")

    def check_channel_signals(self, other: ConnectorInterface, self_key: str, other_key: str):
        if isinstance(self.channels[self_key].value, VariableInterface):
            other_signal = other.channels[other_key].value.signal
            self_signal = self.channels[self_key].value.signal
            if other_signal != self_signal:
                raise ValueError(
                    f"Cannot connect channel with signal {other_signal} to channel with signal {self_signal}")

    def check_channel_directions(self, other: ConnectorInterface, self_key: str, other_key: str):
        other_direction = other.channels[other_key].direction
        self_direction = self.channels[self_key].direction
        if other_direction == self_direction:
            raise ValueError(
                f"Cannot connect channel of same directions <{self_key}> to <{other_key}> with direction {self_direction}")
        self.directions[other_key] = self_direction

    def connect_reversed(self, **kwargs):

        reverse_connector = DeclarativeConnector(
            **{k: Channel(v, reversed_direction(self.channels[k].direction)) for k, v in kwargs.items()})

        self.connect(reverse_connector)

    @property
    def connected(self) -> bool:
        return self.connection is not None

    def check_connection(self):
        if not (self.optional or self.connected):
            raise ConnectionError("Connector is not connected!")

    def get_connection(self) -> Connection:
        return self.connection

    def __lshift__(self, other):

        self.connect(other)

    def __rshift__(self, other):

        other.connect(self)
