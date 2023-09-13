from numerous.declarative.connectors.module_connections import ModuleConnections


def create_connections():
    """
        helper method to create a Connection context manager to capture defined connections of the module where is used.
    """
    return ModuleConnections()
