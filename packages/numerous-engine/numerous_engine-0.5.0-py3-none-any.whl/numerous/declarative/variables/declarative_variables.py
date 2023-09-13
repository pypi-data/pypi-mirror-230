from __future__ import annotations

from enum import Enum

from numerous.declarative.specifications.interfaces import DirectionInterface, VariableInterface
from numerous.declarative.instance import Class
from numerous.declarative.signal import Signal, PhysicalQuantities, Units


class MappingTypes(Enum):
    ASSIGN = 0
    ADD = 1


class DeclarativeVariable(Class, VariableInterface, DirectionInterface):
    _mappings: list[tuple[MappingTypes, VariableInterface]] = []
    signal: Signal
    name:str
    value: float
    path: tuple[str] = None

    def __init__(self, value=None,
                 signal: Signal = Signal(physical_quantity=PhysicalQuantities.Default, unit=Units.NA)):
        Class.__init__(self)
        self.signal = signal
        self.value = value

    def set_mappings(self, mappings: list):
        self._mappings = mappings

    def add_sum_mapping(self, mapping):
        self._mappings.append((MappingTypes.ADD, mapping))

    def add_assign_mapping(self, mapping):
        self._mappings.append((MappingTypes.ASSIGN, mapping))

    def __add__(self, other):
        self.add_sum_mapping(other)
        return self

    def _instance_recursive(self, context):
        instance = self.__class__()
        instance._context = context
        instance.set_mappings([(v[0], v[1].instance(context)) for v in self._mappings])
        instance.value = self.value
        instance.signal = self.signal
        return instance

    @property
    def mappings(self):
        return self._mappings


class Parameter(DeclarativeVariable):
    """
    Declaration of a Parameter
    """
    ...


class Constant(DeclarativeVariable):
    """
    Declaration of a Constant. A constant cannot be changed.
    """


class StateVar(DeclarativeVariable):
    """
    Declaration of a Constant. A constant cannot be changed.
    """

    ...


class Derivative(DeclarativeVariable):
    """
    Declaration of a Constant. A constant cannot be changed.
    """

    ...


def State(value):
    """
    Declaration of a State. States have time derivatives which are integrated to the state values of the system.
    """
    return StateVar(value=value), Derivative(value=0)


def integrate(var, integration_spec):
    var.integrate = integration_spec
    return var, DeclarativeVariable(value=0)
