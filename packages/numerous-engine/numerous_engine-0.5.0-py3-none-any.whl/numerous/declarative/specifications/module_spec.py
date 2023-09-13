from numerous.declarative.instance import Class, get_class_vars
from numerous.declarative.specifications.interfaces import DirectionInterface, ModuleSpecInterface,\
    ItemsSpecInterface, ScopeSpecInterface, ModuleInterface


class ModuleSpec(Class, ModuleSpecInterface, DirectionInterface):
    assigned_to: ModuleInterface | None = None
    path: tuple[str] | None

    def __init__(self, items: dict):
        super(ModuleSpec, self).__init__()
        self._items = items
        self.path = None

        for k, v in self._items.items():
            setattr(self, k, v)

    @classmethod
    def from_module_cls(cls, module):
        items = get_class_vars(module, (Class,))
        context = {}
        module_spec = cls({k: v.instance(context) for k, v in items.items()})
        return module_spec

    def _instance_recursive(self, context: dict):
        instance = ModuleSpec({k: v.instance(context) for k, v in self._items.items()})

        return instance

    @property
    def scopes(self):
        return self._items_of_type(ScopeSpecInterface)

    @property
    def items_specs(self):
        return self._items_of_type(ItemsSpecInterface)
