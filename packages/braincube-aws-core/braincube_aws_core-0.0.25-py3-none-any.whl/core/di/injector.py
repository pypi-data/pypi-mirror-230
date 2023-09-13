from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod


class Scope(Enum):
    request = "REQUEST"
    singleton = "SINGLETON"


@dataclass
class Module:
    name: str | None
    scope: Scope
    qualifier: dict
    component: callable


class IInjector(ABC):
    """Abstract class which holds the reference of multiple dependencies in order to be created by IInjectorManager."""

    @property
    @abstractmethod
    def modules(self) -> list[Module]:
        """Dependencies in form of Module objects."""
        raise NotImplementedError()

    @abstractmethod
    def inject(self, name: str = None, scope: Scope = Scope.singleton, qualifier: dict = None):
        """Function that injects a class or function.
        :param name: Optional name of the component.
        :param scope: The scope of the component.
        :param qualifier: Dictionary, used by injection package in order to
        specify components by name in case of multiple implementations.
        """
        raise NotImplementedError()


class Injector(IInjector):

    def __init__(self):
        self._modules: list[Module] = list()

    @property
    def modules(self) -> list[Module]:
        return self._modules

    def inject(self, name: str = None, scope: Scope = Scope.singleton, qualifier: dict = None):
        def _inject(component):
            self._modules.append(Module(name, scope, qualifier, component))
            return component

        return _inject
