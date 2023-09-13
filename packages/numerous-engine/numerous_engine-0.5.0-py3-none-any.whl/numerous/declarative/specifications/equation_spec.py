from typing import Callable

from numerous.declarative.specifications.scope_spec import ScopeSpec


class EquationSpec:
    """
       Specification of an equation in a module. Use this as a decorator for your methods implementing the equations in a module.
   """

    def __init__(self, scope: ScopeSpec):
        """
            scope: instance of the scope specification to which this equation will be added.
        """

        super(EquationSpec, self).__init__()
        """
        Create an equation specification.

        Will add the equation to the scope passed as the argument
        """
        self.scope = scope
        self.func = None

    def __call__(self, func: Callable) -> Callable:
        self.func = func
        self.scope._equations.append(self)

        return self.func
