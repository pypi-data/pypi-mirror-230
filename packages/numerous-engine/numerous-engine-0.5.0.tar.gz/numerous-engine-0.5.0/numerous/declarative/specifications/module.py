import uuid

from numerous.declarative.generator import generate_system
from numerous.declarative.specifications.module_spec import ModuleSpec
from numerous.declarative.connectors.module_connections import ModuleConnections
from numerous.declarative.context_managers import _active_subsystem
from numerous.declarative.instance import Class, get_class_vars
from numerous.declarative.specifications.interfaces import ScopeSpecInterface, ItemsSpecInterface, ModuleInterface, \
    ConnectorInterface, DirectionInterface
from numerous.declarative.specifications.item_spec import AutoItemsSpec
from numerous.declarative.utils import RegisterHelper
from numerous.engine.system import Subsystem


def _get_connections(vars):
    _connections = []
    for k, v in vars.items():
        for key, value in get_class_vars(v, ModuleSpec).items():
            if hasattr(value, 'connector'):
                if value.connector.module_connections:
                    _connections.extend(value.connector.module_connections.connections)
    if _connections:
        return ModuleConnections(*_connections)


class Module(ModuleInterface, Class, DirectionInterface):
    _parent = None
    path: tuple[str] | None

    def __new__(cls, *args, **kwargs):

        parent_module = _active_subsystem.get_active_manager_context(ignore_no_context=True)
        register_helper = RegisterHelper()

        _active_subsystem.clear_active_manager_context(parent_module)
        _active_subsystem.set_active_manager_context(register_helper)

        org_init = cls.__init__

        def wrap(self, *args, **kwargs):

            org_init(self, *args, **kwargs)
            _active_subsystem.clear_active_manager_context(register_helper)
            _active_subsystem.set_active_manager_context(parent_module)

            if isinstance(parent_module, RegisterHelper):
                parent_module.register_item(self)

            _auto_modules = []
            for module in register_helper.get_items().values():
                if module._parent is None:
                    _auto_modules.append(module)
                    module._parent = self
            if len(_auto_modules) > 0:
                self._auto_modules = AutoItemsSpec(_auto_modules)

            cls.__init__ = org_init

        cls.__init__ = wrap

        instance = Class.__new__(cls)

        return instance

    def __init__(self, tag: str | None = None):
        super(Module, self).__init__()
        if tag is None:
            tag = self.__class__.__name__ + str(uuid.uuid4())
        self.tag = tag
        self.path = None
        self._item_specs = {}
        vars = get_class_vars(self, (Class,))
        self.connections = _get_connections(vars)
        if self.connections:
            vars["connections"] = self.connections
        context = {}

        self._items = {}

        for k, v in vars.items():
            instance = v.instance(context)
            setattr(self, k, instance)
            self._items[k] = instance

    def generate_subsystem(self, system_name: str) -> Subsystem:
        return generate_system(system_name, self)

    @property
    def connectors(self):
        return self._items_of_type(ConnectorInterface)

    @property
    def items_specs(self):
        return self._items_of_type(ItemsSpecInterface)

    @property
    def connection_sets(self):
        connection_sets = {k: v for k, v in self.__dict__.items() if isinstance(v, ModuleConnections)}

        return connection_sets

    @property
    def scopes(self):
        return self._items_of_type(ScopeSpecInterface)

    def finalize(self):
        self._finalized = True

        for item_spec in self._item_specs.values():
            item_spec.finalize()
