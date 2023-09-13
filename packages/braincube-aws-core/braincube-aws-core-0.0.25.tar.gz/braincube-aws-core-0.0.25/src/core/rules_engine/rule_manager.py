from abc import ABC, abstractmethod

from rule_engine import Rule, Context

from ..dal.postgres_connection import Connection

from .data import CriteriaRule, Instruction
from .exceptions import RuleNotFound


class RuleManager(ABC):

    def __init__(self):
        self.__criteria: dict[int, list] = dict()
        self.__instructions: dict[str, dict] = dict()
        self.__context = Context(default_value=None)

    @abstractmethod
    def _get_criteria_props(self) -> dict[str, list]:
        raise NotImplemented("_retrieve_criteria_properties")

    @abstractmethod
    async def _get_criteria_rules(self, type_class: int) -> list[CriteriaRule]:
        raise NotImplemented("_retrieve_criteria_rules")

    def _convert_to_command(self, **kwargs):
        command = ""
        for k, v in kwargs.items():
            data = v.dict(exclude_unset=True)
            for prop in self._get_criteria_props()[k]:
                if prop not in data:
                    continue
                value = data[prop]
                if not value:
                    query = f"not {k}.{prop}"
                else:
                    value_ = f"'{value}'" if isinstance(value, str) else value
                    query = f"({k}.{prop} == {value_} or not {k}.{prop})"
                command += f"{query}" if not command else f" and {query}"
        return command

    async def _get_criteria(self, type_class: int) -> list:
        if type_class not in self.__criteria:
            criteria_rules = await self._get_criteria_rules(type_class)
            self.__criteria[type_class] = [{
                **{"_id_": cr.id, "_priority_": cr.priority},
                **cr.data["criteria"].copy()
            } for cr in criteria_rules]
            [self.__instructions.update({cr.id: cr.data["instructions"]}) for cr in criteria_rules]
        return self.__criteria[type_class]

    async def get_instruction(self, type_class: int, **kwargs) -> Instruction:
        cmd = self._convert_to_command(**kwargs)
        criteria = await self._get_criteria(type_class)
        result = list(Rule(cmd, context=self.__context).filter(criteria))

        if not result:
            raise RuleNotFound(cmd)

        matched: dict = max(result, key=lambda m: m["_priority_"])
        return Instruction(**self.__instructions[matched["_id_"]])

    @abstractmethod
    async def execute_instruction(self, instruction: Instruction, connection: Connection | None, **kwargs):
        raise NotImplemented("execute_instruction")

    async def execute(self, type_class: int, connection: Connection | None, **kwargs):
        instruction = await self.get_instruction(type_class, **kwargs)
        return await self.execute_instruction(instruction, connection, **kwargs)
