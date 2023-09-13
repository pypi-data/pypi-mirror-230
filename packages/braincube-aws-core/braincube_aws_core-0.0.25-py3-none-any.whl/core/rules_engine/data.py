from enum import Enum
from uuid import UUID
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class CriteriaRule:
    id: str
    type: int
    priority: int
    data: dict


class CashFlowType(Enum):
    in_ = "IN"
    out_ = "OUT"


class ActionType(Enum):
    email = "EMAIL"
    push = "PUSH"


class CashFlowStatusType(Enum):
    created = "CREATED"
    completed = "COMPLETED"


class CashFlow(BaseModel):
    type: CashFlowType
    status: CashFlowStatusType
    account_id: UUID | None
    value_date: str
    settle_type: str
    basis_amount: str
    basis_currency: str
    cash_flow_date: str
    currency_change_allowed: bool


class ActionContent(BaseModel):
    subject: str
    template: str
    receivers: list[str]
    params: dict


class Action(BaseModel):
    type: ActionType
    content: ActionContent


class Instruction(BaseModel):
    actions: list[Action]
    cash_flows: list[CashFlow]
    reverse_cash_flows_netting: bool
    reverse_current_cash_flows: bool
