from __future__ import annotations

from typing import Self

from numerous.declarative.specifications.module_spec import ModuleSpec
from numerous.declarative.exceptions import ItemNotAssignedError
from numerous.declarative.instance import Class, get_class_vars
from numerous.declarative.specifications.interfaces import DirectionInterface, ItemsSpecInterface, ModuleInterface
from numerous.declarative.utils import handler


class AutoItemsSpec(Class, ItemsSpecInterface, DirectionInterface):
    _modules: dict

    def __init__(self, modules: list):
        super(AutoItemsSpec, self).__init__()
        counter = 0
        for module in modules:
            if not hasattr(module, 'tag') or not module.tag:
                module.tag = "unnamed_" + str(counter)
                counter += 1
        self._modules = {module.tag: module for module in modules}
        setattr(self, module.tag, module)

    def get_modules(self, ignore_not_assigned=False, update_first=False):

        return self._modules

    def get_module_specs(self):

        return {}

    @property
    def modules(self):
        return self._modules

    def remove_non_orphants(self):

        orphants = {}

        for name, module in self.modules.items():
            if module._parent is None:
                orphants[name] = module
                setattr(self, name, module)
        self.modules = orphants


class ItemsSpec(Class, ItemsSpecInterface):
    _modules: dict
    _module_specs: dict
    _module_connections = None

    def __init__(self, init=True):
        super(ItemsSpec, self).__init__()
        if init:
            module_specs = get_class_vars(self, (ModuleInterface,), _handle_annotations=handler)

            context = {}

            self._modules = {}
            self._module_specs = {}

            for k, v in module_specs.items():
                instance = v.instance(context)

                self._module_specs[k] = instance
                instance.assigned_field = k
                setattr(self, k, instance)

    def _instance_recursive(self, context: dict) -> Self:

        instance = ItemsSpec(init=False)
        instance._modules = {k: m.instance(context) for k, m in self._modules.items()}
        instance._module_specs = {k: m.instance(context) for k, m in self._module_specs.items()}

        for name, module in instance._module_specs.items():
            setattr(instance, name, module)

        for name, module in instance._modules.items():
            setattr(instance, name, module)

        return instance

    def update_modules(self):

        for k, v in self._module_specs.items():
            if k not in self._modules and v.assigned_to:
                self._modules[k] = v.assigned_to

    def get_modules(self, ignore_not_assigned: bool = False, update_first: bool = False):
        if update_first:
            self.update_modules()

        if not ignore_not_assigned:
            not_assigned = {}
            for k, v in self._module_specs.items():
                if k not in self._modules:
                    not_assigned[k] = v

            if len(not_assigned) > 0:
                for v in not_assigned.values():
                    print(v.assigned_to)
                    print(v.path)
                raise ItemNotAssignedError(f"Items not assigned: {list(not_assigned.keys())}")

        return self._modules

    def get_module_specs(self) -> dict:

        return self._module_specs

    @property
    def modules(self):

        return self._modules

    def __setattr__(self, key, value):
        if isinstance(value, ModuleInterface):
            # TODO add checks on if assigned etc
            if not key in self._module_specs:
                raise ModuleNotFoundError(f"Items spec does not have a module {key}")
            self._module_specs[key].assigned_to = value
            self._modules[key] = value
            value._parent = True

            for module in self.modules.values():
                for item in module._items.values():
                    if type(item) is ItemsSpec:
                        for ms_name  in item._module_specs.keys():
                            if q:=getattr(item, ms_name):
                                if type(q) is ModuleSpec and q.assigned_to:
                                    if q.assigned_to.tag== value.tag:
                                        setattr(item, ms_name, value)

        super(ItemsSpec, self).__setattr__(key, value)
