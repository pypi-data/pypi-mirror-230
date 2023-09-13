from numerous.declarative.specifications.interfaces import ScopeSpecInterface, VariableInterface
from numerous.declarative.instance import Class, get_class_vars


class ScopeSpec(Class, ScopeSpecInterface):
    _equations: list
    _variables: dict
    init = False

    def __init__(self, context=None, init=True):
        self.init = False
        super(ScopeSpec, self).__init__()

        if init:
            self._equations = []

            context = {} if context is None else context
            self._variables = {k: v.instance(context) for k, v in get_class_vars(self, (VariableInterface,)).items()}

            for name, variable in self._variables.items():
                variable.name = name
                setattr(self, name, variable)
        self.init = True

    def _instance_recursive(self, context):
        instance = self.__class__(init=False)
        instance._equations = self._equations
        instance._variables = {k: v.instance(context) for k, v in self._variables.items()}
        for name, variable in instance._variables.items():
            instance.__setattr__(name, variable, mapping=False)

        return instance

    @property
    def equations(self):
        return self._equations

    @property
    def variables(self):
        return self._variables

    def set_values(self, **kwargs):
        """
            Set values of variables in the namespace by passing keyword arguments corresponding to variable names.
        """
        for k, v in kwargs.items():
            self._variables[k].value = v

    def __setattr__(self, key, value, mapping=True):
        if mapping and self.init and hasattr(self, key) and isinstance((var := getattr(self, key)),
                                                                       VariableInterface) and value is not var:

            var.add_assign_mapping(value)
        else:
            super(ScopeSpec, self).__setattr__(key, value)
