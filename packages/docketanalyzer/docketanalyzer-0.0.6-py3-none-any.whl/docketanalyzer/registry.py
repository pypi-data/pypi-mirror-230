import importlib
import inspect
import pkgutil
from typing import Any, Optional
from types import ModuleType
from pathlib import Path


class Registry:
    """
        A base registry class.
    """
    
    def __init__(self) -> None:
        self._registry: dict[str, Any] = {}
        self.module: ModuleType = inspect.getmodule(inspect.stack()[1][0])

    def register(self, name: str, item: Any) -> None:
        """
        Register an item with the given name.

        :param name: The name to register the item under.
        :param item: The item to register.
        :raises ValueError: If the name is already registered.
        """
        if name in self._registry:
            raise ValueError(f"'{name}' already exists.")
        self._registry[name] = item

    def get(self, name: str) -> Any:
        """
        Get an item by its registered name.

        :param name: The name of the item to get.
        :return: The item with the given name.
        :raises ValueError: If the name is not registered.
        """
        if name not in self._registry:
            raise ValueError(f"'{name}' does not exist.")
        return self._registry[name]
    
    def all(self) -> list[Any]:
        """
        Get a list of all registered items.

        :return: A list of all registered items.
        """
        return list(self._registry.values())

    def find_filter(self, obj: Any) -> bool:
        """
        A filter to determine if an object should be registered.

        :param obj: The object to check.
        :return: True if the object should be registered, False otherwise.
        :raises NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError("find_filter() must be implemented by a subclass.")

    def find(self, module: Optional[ModuleType] = None, recurse: bool = False) -> None:
        """
        Find all objects in current module and register those that pass the filter.
        """
        if module is None:
            module = self.module
        if isinstance(module, str):
            module = importlib.import_module(module)
        for _, submodule_name, _ in pkgutil.walk_packages(module.__path__):
            submodule = importlib.import_module(f"{module.__name__}.{submodule_name}")
            for name in dir(submodule):
                obj = getattr(submodule, name)
                if recurse and isinstance(obj, importlib.machinery.ModuleSpec):
                    next_module = importlib.util.module_from_spec(obj)
                    if hasattr(next_module, '__path__'):
                        self.find(module=next_module)
                if self.find_filter(obj) and name not in self._registry:
                    self.register(name, obj)
    
    def import_registered(self) -> None:
        """
        Import the registered classes into the module's namespace.
        """
        for cls in self.all():
            setattr(self.module, cls.__name__, cls)

