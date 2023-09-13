from __future__ import annotations

from .context_managers import _active_mappings
from numerous.declarative.variables.declarative_variables import MappingTypes, DeclarativeVariable


class Obj:
    def __init__(self, scope_specs, items_specs):
        self._item_specs = items_specs
        self._scopes = scope_specs


class Mapping:
    _mapping_type: MappingTypes
    _from: DeclarativeVariable
    _to: DeclarativeVariable

    def __init__(self, to_var: DeclarativeVariable = None, from_var: DeclarativeVariable = None,
                 mapping_type: MappingTypes = None):
        super(Mapping, self).__init__()

        self._mapping_type = mapping_type
        self._to = to_var
        self._from = from_var

    @property
    def mapping_type(self):
        return self._mapping_type


class ModuleMappings():
    _mappings: list

    def __init__(self, *args):

        super(ModuleMappings, self).__init__()
        self._mappings = []

    def __enter__(self):
        _active_mappings.set_active_manager_context(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _active_mappings.clear_active_manager_context(self, ignore_not_set=True)

    def assign(self, a, b):
        if not isinstance(a, DeclarativeVariable):
            raise TypeError(f"to_var is not a Variable, but {a.__class__.__name__}")
        if not isinstance(b, DeclarativeVariable):
            raise TypeError(f"from_var is not a Variable, but {b.__class__.__name__}")
        self._mappings.append(Mapping(a, b, MappingTypes.ASSIGN))
        # a.mapped_to.append(b)

    def add(self, a, b):
        self._mappings.append(Mapping(a, b, MappingTypes.ADD))

    @property
    def mappings(self):
        return self._mappings


def create_mappings(*args):
    return ModuleMappings(*args)
