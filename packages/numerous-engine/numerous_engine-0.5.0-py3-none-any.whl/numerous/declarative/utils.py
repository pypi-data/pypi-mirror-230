from __future__ import annotations

import inspect
import uuid

from numerous.declarative.exceptions import DuplicateItemError
from numerous.declarative.specifications.interfaces import ModuleInterface
from numerous.declarative.specifications.module_spec import ModuleSpec
from numerous.engine.system import Item


class BoundValues:

    def __init__(self, **kwargs):
        self.bound_values = kwargs


def local(tag, mod: ModuleInterface):
    mod.tag = tag

    return mod


class RegisterHelper:

    def __init__(self):
        self._items = {}

    def register_item(self, item):
        self._items[str(uuid.uuid4())] = item

    def get_items(self):
        return self._items


def handler(annotation):
    return ModuleSpec.from_module_cls(annotation)


def recursive_get_attr(obj, attr_list):
    attr_ = getattr(obj, attr_list[0])

    if len(attr_list) > 1:
        return recursive_get_attr(attr_, attr_list[1:])
    else:
        return attr_


def is_instance_or_subclass(obj, target_superclass):
    return any(issubclass(base, target_superclass) for base in type(obj).__bases__) \
        or issubclass(type(obj), target_superclass)


def path_to_str(var):
    if var is None:
        return "None"
    return ".".join(list(var.path.path.values())[-1])


def print_map(var):
    print(path_to_str(var) + ": " + path_to_str(var.mapping) + ", " + str([path_to_str(v) for v in var.sum_mapping]))


class RegisterHelper:

    def __init__(self):
        self._items = {}

    def register_item(self, item):
        if item.tag in self._items:
            raise DuplicateItemError(f"An item with tag {item.tag} already registered.")
        self._items[item.tag] = item

    def get_items(self):
        return self._items


def allow_implicit(func):
    sign = inspect.signature(func)

    def check_implicit(*args, **kwargs):

        if len(args) > 1 and isinstance(item := args[1], Item):
            _kwargs = {}
            _args = []
            for n, p in sign.parameters.items():
                if n != "self":
                    val = getattr(getattr(item, 'variables'), n)
                    if n in kwargs:

                        _kwargs[n] = val
                    else:
                        _args.append(val)

            func(args[0], *_args, **kwargs)
        else:
            func(*args, **kwargs)

    return check_implicit
