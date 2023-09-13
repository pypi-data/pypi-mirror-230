from enum import Enum
from json import loads
from http import HTTPStatus
from dataclasses import dataclass
from typing import Generic, TypeVar, Type
from pydantic import BaseModel, Field

from ..utils.convert import try_str_to_float
from ..utils.data import Order, OrderType, Condition, ConditionType, Pageable

T = TypeVar("T")


####################################
# Event
####################################

class CallerContext(BaseModel):
    aws_sdk_version: str = Field(alias="awsSdkVersion")
    client_id: str = Field(alias="clientId")


class UserPoolEvent(BaseModel):
    version: str
    trigger_source: str = Field(alias="triggerSource")
    region: str
    user_pool_id: str = Field(alias="userPoolId")
    user_name: str = Field(alias="userName")
    caller_context: CallerContext = Field(alias="callerContext")
    request: dict
    response: dict


class Attributes(BaseModel):
    approximate_receive_count: str = Field(alias="ApproximateReceiveCount")
    aws_trace_header: str | None = Field(alias="AWSTraceHeader")
    sent_timestamp: str = Field(alias="SentTimestamp")
    sender_id: str = Field(alias="SenderId")
    approximate_first_receive_timestamp: str = Field(alias="ApproximateFirstReceiveTimestamp")


class Record(BaseModel):
    message_id: str = Field(alias="messageId")
    receipt_handle: str = Field(alias="receiptHandle")
    body: str
    md5_of_body: str = Field(alias="md5OfBody")
    md5_of_message_attributes: str | None = Field(alias="md5OfMessageAttributes")
    event_source_arn: str = Field(alias="eventSourceARN")
    event_source: str = Field(alias="eventSource")
    aws_region: str = Field(alias="awsRegion")
    attributes: Attributes
    message_attributes: dict = Field(alias="messageAttributes")


class SqsEvent(BaseModel):
    records: list[Record] = Field(alias="Records")


class SqsResponse(BaseModel):
    batch_item_failures: list[str] = Field(alias="batchItemFailures")


class EventType(Enum):
    sqs = 1
    cognito = 2


@dataclass()
class EventPayload(Generic[T]):
    event: T
    context: dict


@dataclass()
class AuthUser:
    cognito_id: str = None
    email: str = None
    email_confirmed: bool = False


@dataclass()
class QueryParams:
    fields: list[str] = None
    conditions: list[Condition] = None
    page: Pageable = Pageable()
    order: list[Order] = None


@dataclass()
class HTTPRequest(Generic[T]):
    body: T = None
    headers: dict[str, any] = None
    path_params: dict[str, any] = None
    user: AuthUser = AuthUser()
    query_params: QueryParams = QueryParams()


@dataclass()
class HTTPResponse:
    status: HTTPStatus = HTTPStatus.OK
    body: any = None
    headers: dict[str, any] = None


####################################
# Helpers
####################################


@dataclass()
class Handler:
    func: callable
    payload_type: type | None
    dependencies: list[tuple]


http_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Credentials": True,
    "Access-Control-Allow-Headers":
        "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token"
}


def convert_to_event_payload(cls: Type[T], event: dict[str, any], context) -> EventPayload[T]:
    return EventPayload(cls(**event) if cls is not dict else event, context)


def convert_to_http_request(cls: Type[T], event: dict[str, any], context) -> HTTPRequest[T]:
    data = loads(event["body"]) if event.get("body") else None

    request = HTTPRequest(body=cls(**data) if cls is not dict else data,
                          headers=event.get("headers"),
                          path_params=event.get("pathParameters"))

    if "authorizer" in event["requestContext"]:
        claims = event["requestContext"]["authorizer"]["claims"]
        request.user = AuthUser(claims["sub"], claims["email"], claims["email_verified"] == "true")

    params: dict[str, any] | None = event.get("queryStringParameters")

    if params:
        fields = params["fields"].replace(" ", "").split(",") if params.get("fields") else list()
        pageable = Pageable(_page_param(params, alias="pageNo"),
                            _page_param(params, alias="pageSize", default=20, max_=50, min_=1),
                            _page_param(params, alias="topSize", max_=1000, min_=-1))

        conditions = list()
        for k, v in params.items():
            key = k.strip()
            if key in _reserved_keys:
                continue
            else:
                value = v.strip()
                value_ = value.lower()
                if value_.startswith("range(") and value_.endswith(")"):
                    condition_type = ConditionType.range
                    d = _condition_param("range", value)
                    if not len(d) >= 2:
                        continue
                elif value_.startswith("any(") and value_.endswith(")"):
                    condition_type = ConditionType.any
                    d = _condition_param("any", value)
                else:
                    condition_type = ConditionType.compare
                    d = try_str_to_float(value)
                conditions.append(Condition(condition_type, key, d))

        order = list()
        for order_ in (params["order"].split(",") if params.get("order") else list()):
            o = order_.strip().split(" ")
            if len(o) < 1:
                continue
            order_type = OrderType.asc
            if len(o) == 2:
                order_type = next((e for e in OrderType if e.value == o[1].upper()), None)
            if not order_type:
                continue
            order.append(Order(order_type, alias=o[0]))

        request.query_params = QueryParams(fields, conditions, pageable, order)

    return request


def _page_param(params: dict[str, any], alias: str, default: int = 0, max_: int = None, min_: int = 0) -> int:
    try:
        if not params.get(alias):
            return default
        value_ = int(params[alias])
        return value_ if (max_ >= value_ >= min_ if max_ else value_ >= min_) else default
    except ValueError:
        return default


def _condition_param(type_, p) -> list:
    return [try_str_to_float(i) for i in p[len(type_) + 1:len(p) - 1].replace(" ", "").split(",")]


_reserved_keys = ["fields", "pageNo", "pageSize", "topSize", "order"]
