from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar
from inspect import signature, isfunction, iscoroutinefunction

from .injector import Scope, Module, IInjector
from ..dal.postgres_connection import Pool, get_pool

T = TypeVar("T")


@dataclass()
class Dependency(Generic[T]):
    scope: Scope
    cls: Type[T]
    params: list[tuple[type, str | None]] = None
    name: str = None
    instance: T = None
    factory: callable = None


class IInjectionManager(ABC):
    """Abstract class that manages the dependencies of a IInjector class."""

    @abstractmethod
    def store_module(self, module: Module):
        """Function that handles the initialization process of the given dependency.
        :param module: The dependency.
        """
        raise NotImplementedError()

    @abstractmethod
    async def provide(self, cls: Type[T], name: str = None) -> T:
        """Function that returns the desired dependency handled by the manager.
        param cls: The dependency type.
        param name: An optional dependency name.
        """
        raise NotImplementedError()

    def store_modules(self, modules: list[Module]):
        """Function that handles the initialization process of the given dependencies.
        :param modules: The dependencies.
        """
        [self.store_module(module) for module in modules]

    def store_injector(self, injector: IInjector):
        """Function that handles the initialization process of the given Injector's dependencies.
        :param injector: The IInjector instance.
        """
        self.store_modules(injector.modules)

    def store_injectors(self, injectors: list[IInjector]):
        """Function that handles the initialization process of the givens Injectors dependencies.
        :param injectors: The IInjectors instance.
        """
        [self.store_injector(injector) for injector in injectors]


class InjectionManager(IInjectionManager):

    def __init__(self):
        # noinspection PyTypeChecker
        self._dependencies: list[Dependency] = [
            Dependency(Scope.singleton, Pool, factory=get_pool)
        ]

    def store_module(self, module: Module):
        data = module.qualifier.copy() if module.qualifier else dict()
        if isfunction(module.component):
            cls = module.component.__annotations__.get("return")
            if not cls:
                raise ValueError(f"injected function '{module.component.__name__}' must specify return type.")
            params = [(v.annotation, data.get(k)) for k, v in signature(module.component).parameters.items()]
            dependency = Dependency(module.scope, cls, params, module.name, factory=module.component)
            self._dependencies.append(dependency)
        else:
            items_ = dict(filter(lambda i: i[0] != "self", signature(module.component.__init__).parameters.items()))
            params = [(v.annotation, data.get(k)) for k, v in items_.items()]
            dependency = Dependency(module.scope, module.component, params, module.name)
            self._dependencies.append(dependency)

    async def provide(self, cls: Type[T], name: str = None) -> T:
        if issubclass(IInjectionManager, cls):
            return self
        match = list(filter(lambda d: (d.cls is cls or issubclass(d.cls, cls)) and (name is None or d.name == name),
                            self._dependencies))
        if not match:
            raise ValueError(f"component name:'{name}', class:'{cls}' not found.")
        if len(match) > 1:
            raise ValueError(f"multiple matching components have been found for class: '{cls}'")
        if not match[0].instance:
            nested = list()
            if match[0].params:
                for param in match[0].params:
                    nested.append(await self.provide(param[0], param[1]))
            if match[0].factory:
                instance = await match[0].factory(*nested) \
                    if iscoroutinefunction(match[0].factory) else match[0].factory(*nested)
            else:
                instance = match[0].cls(*nested)
            if match[0].scope is Scope.request:
                return instance
            match[0].instance = instance

        return match[0].instance
