import logging

from numerous.declarative.specifications.interfaces import ModuleSpecInterface, ModuleInterface
from numerous.declarative.enums import Directions
from numerous.declarative.variables.declarative_variables import StateVar, Derivative, DeclarativeVariable
from numerous.declarative.utils import BoundValues
from numerous.engine.system.subsystem import Subsystem
from numerous.multiphysics.equation_base import EquationBase
from numerous.multiphysics.equation_decorators import add_equation

from time import time

_logger = logging.getLogger("system generator")


def path_str(path: list):
    return ".".join(path
                    )


def tab_str(tabs, text):
    return "".join(tabs + [text])


def process_module_items(module: ModuleInterface | ModuleSpecInterface, path, tabs):
    _logger.info(tabs + f'process module: {module}')
    for scope_name, scope in module.scopes.items():
        scope_path = path + (scope_name,)
        _logger.info(tabs + "\t" + f'process scope: {scope}')

        for var_name, variable in scope.variables.items():
            if variable.path is None:

                variable.path = scope_path + (var_name,)

                _logger.info(tabs + "\t\t" + f"Setting path of {path_str(variable.path)}")
            else:
                _logger.info(tabs + "\t\t" + f"Already have path: {path_str(variable.path)}")
                _logger.info(tabs + "\t\t" + f"Wanted to set {path_str(scope_path + (var_name,))}")

    for itemsspec_name, itemsspec in module.items_specs.items():
        items_path = path + (itemsspec_name,)
        _logger.info(tabs + f"Processing {path_str(items_path)}, {itemsspec}")

        for sub_module_name, sub_module in itemsspec.get_module_specs().items():
            if sub_module.assigned_to is not None:
                module_path = sub_module.assigned_to.path
            else:
                module_path = items_path + (sub_module_name,)

            _logger.info(tabs + f"Setting path for {path_str(module_path)}, {sub_module}")

            process_module_items(sub_module, module_path, tabs + "\t")

        for sub_module_name, sub_module in itemsspec.get_modules(ignore_not_assigned=True).items():
            module_path = items_path + (sub_module_name,)
            _logger.info(tabs + f"Setting path for {path_str(module_path)}, {sub_module}")

            process_module_items(sub_module, module_path, tabs + "\t")


def process_module_connections(module_path: tuple[str], module: ModuleInterface, tabs, objects):
    if isinstance(module, ModuleInterface):
        _logger.info(tabs + f"Processing connections of module {path_str(module_path)}")

        for connection_set_name, connection_set in module.connection_sets.items():
            # Check all connections
            for connection in connection_set.connections:
                _logger.info(tabs + f"Processing connection {connection}")

                for side1_name, side1, side2_name, side2, direction in connection.channels:
                    to_ = side1 if direction == Directions.GET else side2
                    from_ = side2 if direction == Directions.GET else side1
                    _logger.info(tabs + f"{side1_name} <<>> {side2_name}")
                    if isinstance(to_, (ModuleSpecInterface,)) and isinstance(from_, (ModuleSpecInterface,)) and from_.assigned_to:
                        objects[to_.path].assigned_to = from_.assigned_to

                        _logger.info(f"!{to_.path}, {from_.assigned_to}")

                    elif isinstance(from_, DeclarativeVariable) and isinstance(to_, DeclarativeVariable):
                        _logger.info(tabs + "mapping variables")
                        to_.add_sum_mapping(from_)
                    else:
                        raise TypeError('!')

    for itemsspec_name, itemsspec in module.items_specs.items():
        items_path = module_path + (itemsspec_name,)
        for sub_module_name, sub_module in itemsspec.get_modules(ignore_not_assigned=True).items():
            sub_module_path = items_path + (sub_module_name,)

            process_module_connections(sub_module_path, sub_module, tabs + "\t", objects)


def process_mappings(module: ModuleInterface | ModuleSpecInterface, path, objects, tabs, spec=False):
    _logger.info(tabs + f"Process for {path_str(path)} - spec: {spec}")

    for scope_name, scope in module.scopes.items():

        for variable_name, variable in scope.variables.items():

            var_path = path_str(variable.path)

            for mapping in variable.mappings:

                if mapping[1].path is None:
                    _logger.info(tabs + f"{var_path} << ?, {mapping[1]}")
                else:
                    map_path = path_str(mapping[1].path)

                    var = objects[variable.path].native_ref


                    mapping_var = objects[mapping[1].path].native_ref
                    if not mapping_var in var.sum_mapping:
                        _logger.info(tabs + f"{var_path} << {map_path}")
                        var.add_sum_mapping(mapping_var)

    for itemsspec_name, itemsspec in module.items_specs.items():
        items_path = path + (itemsspec_name,)
        for sub_module_name, sub_module in itemsspec.get_modules(ignore_not_assigned=True).items():
            sub_module_path = items_path + (sub_module_name,)

            process_mappings(sub_module, sub_module_path, objects, tabs + "\t")

        for sub_module_name, sub_module in itemsspec.get_module_specs().items():
            sub_module_path = items_path + (sub_module_name,)

            process_mappings(sub_module, sub_module_path, objects, tabs + "\t", spec=True)


def reprocess(module: ModuleInterface, path: tuple, objects):
    for scope_name, scope in module.scopes.items():
        scope_path = path + (scope_name,)

        for var_name, variable in scope.variables.items():
            var_path = scope_path + (var_name,)
            objects[var_path] = variable

    for itemsspec_name, itemsspec in module.items_specs.items():
        items_path = path + (itemsspec_name,)
        for sub_module_name, sub_module in itemsspec.get_modules().items():
            submodule_path = items_path + (sub_module_name,)

            reprocess(sub_module, submodule_path, objects)

        for sub_module_name, sub_module in itemsspec.get_module_specs().items():
            submodule_path = items_path + (sub_module_name,)

            reprocess(sub_module, submodule_path, objects)


def generate_subsystem(name: str, module: ModuleInterface, processed_modules, path, objects, tabs):
    system = Subsystem(name)

    for k, v in module.__dict__.items():
        if isinstance(v, BoundValues):
            for k, vv in v.bound_values.items():
                setattr(system, k, vv)

    objects[path] = system

    for scope_name, scope in module.scopes.items():

        scope_path = tuple(path + (scope_name,))

        namespace = system.create_namespace(scope_name)
        objects[scope_path] = namespace
        setattr(system, scope_name, namespace)

        equation = create_equation(system, scope_name, scope.equations)

        for var_name, variable in scope.variables.items():

            if variable.value is None:
                raise TypeError(f"Variable {var_name} has not been assigned a value!")

            if isinstance(variable, StateVar):
                equation.add_state(var_name, variable.value)
            elif isinstance(variable, Derivative):
                ...
            else:
                equation.add_parameter(var_name, variable.value)

        namespace.add_equations([equation])

        for var_name, variable in scope.variables.items():
            variable.native_ref = getattr(namespace, var_name)
            var_path = scope_path + (var_name,)
            objects[var_path] = variable

    processed_modules.append(module)

    for itemsspec_name, itemsspec in module.items_specs.items():
        items_path = path + (itemsspec_name,)
        _logger.info(f"Building subsystem for {items_path}")
        for sub_module_name, sub_module in itemsspec.get_modules(ignore_not_assigned=False, update_first=True).items():
            submodule_path = items_path + (sub_module_name,)
            if not sub_module in processed_modules:
                _logger.info(tabs + f"sub module: {path_str(submodule_path)}")
                sub_system = generate_subsystem(sub_module_name, sub_module, processed_modules, submodule_path, objects,
                                                tabs + '\t')

                system.register_item(sub_system)
            else:
                reprocess(sub_module, submodule_path, objects)

    return system


def generate_paths(module: ModuleInterface, path: tuple[str], objects):
    if module.path is None:
        module.path = path
        _logger.info(path)
        objects[path] = module

    for itemsspec_name, itemsspec in module.items_specs.items():
        items_path = path + (itemsspec_name,)

        for sub_module_name, sub_module in itemsspec.modules.items():
            submodule_path = items_path + (sub_module_name,)

            generate_paths(sub_module, submodule_path, objects)

        for sub_module_name, sub_module in itemsspec.get_module_specs().items():
            submodule_path = items_path + (sub_module_name,)

            generate_paths(sub_module, submodule_path, objects)


def create_equation(system, name, equation_specifications):
    class Eq(EquationBase):
        tag = name + "_eq"

    equation = Eq()

    for eq_spec in equation_specifications:
        eq_func = eq_spec.func
        eq_func.__self__ = system
        _ = add_equation(equation, eq_func)

    return equation


def generate_system(name: str, module: ModuleInterface):
    tic = time()
    objects = {}
    path = (name,)
    processed_modules = []

    tabs = ""

    # Process connections - this ensures all modules are updated through connectors,
    # before check of items specs assignments are complete.
    _logger.info("Processing model connections")

    generate_paths(module, path, objects)

    process_module_connections(path, module, tabs + "\t", objects)

    # Process items specs - create system hierarchy
    _logger.info("Processing model items")

    process_module_items(module, path, tabs)

    _logger.info("Generating numerous engine system")

    system = generate_subsystem(name, module, processed_modules, path, objects, tabs + '\t')

    # Process mappings - finally loop to ensure all mappings are in place
    _logger.info("Processing model mappings")
    process_mappings(module, path, objects, tabs)
    toc = time()
    _logger.info(f'completed generation of system from model in {toc - tic} s.')

    return system
