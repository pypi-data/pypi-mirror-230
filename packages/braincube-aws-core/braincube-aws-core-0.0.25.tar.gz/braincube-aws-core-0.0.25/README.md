# braincube-aws-core

Microframework for Python AWS lambdas.

[![Language](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/)
[![pypi](https://img.shields.io/pypi/v/braincube-aws-core.svg)](https://pypi.org/project/braincube-aws-core/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Installation

```bash
pip install braincube-aws-core
```

## Built With

- [asyncpg](https://github.com/MagicStack/asyncpg) - A fast PostgreSQL Database Client Library for Python/asyncio.
- [pydantic](https://github.com/pydantic/pydantic) - Data validation using Python type hints.
- [pypika](https://github.com/kayak/pypika) - Python Query Builder.

### Application Controllers Example

```python
import asyncio

from uuid import uuid4
from http import HTTPStatus

from core.app.data import HTTPRequest, HTTPResponse
from core.app.app_module import AppModule
from core.app.app_controller import AppController

from pydantic import BaseModel


class AccountDto(BaseModel):
    iban: str
    bban: str


data = {
    "a0a412d9-87ef-474b-9ac8-b682ec5e0fb3": AccountDto(iban="EUR27100777770209299700", bban="EURC12345612345678"),
    "5ebc25bd-e152-4a70-b251-d68e43be581e": AccountDto(iban="GR27100777770209299700", bban="GRC12345612345678"),
}

app = AppController("/accounts")


@app.get("/{id}")
async def get_account(request: HTTPRequest) -> HTTPResponse:
    account = data.get(request.path_params["id"])
    return HTTPResponse(HTTPStatus.OK if account else HTTPStatus.NO_CONTENT, account)


@app.post()
async def create_account(request: HTTPRequest[AccountDto]) -> HTTPResponse:
    data[uuid4()] = request.body
    return HTTPResponse(HTTPStatus.CREATED)


loop = asyncio.get_event_loop()

module = AppModule([app])


def main(event, context):
    return loop.run_until_complete(module.serve(event, context))
```

### Dependency Injection Example

```python
from core.di.injector import inject
from core.dal.postgres_connection import get_pool, Pool


@inject("data_warehouse_pool")
async def provide_warehouse_pool() -> Pool:
    return await get_pool()


@inject(qualifier="pool:data_warehouse_pool")
class BankService:

    def __init__(self, pool: Pool):
        self._pool = pool
```

### Postgres Repository Example

```python
from core.app.data import HTTPRequest
from core.utils.data import Order, OrderType
from core.dal.data import Key, Schema, Column, Relation, SimpleColumn, JoinType, JoinThrough, StatementField
from core.dal.postgres_connection import get_pool, Pool
from core.dal.postgres_repository import PostgresRepository

# schema definition
equities = Schema(
    table="equities",
    alias="e",
    primary_key=["id"],
    columns=[
        Column("id", updatable=False, insertable=False),
        Column("name"),
        Column("type"),
        Column("issuer_id", alias="issuerId"),
        Column("industry_sector", alias="industrySector"),
        Column("isin"),
        Column("reference"),
        Column("bloomberg_code", alias="bloombergCode"),
        Column("market_symbol", alias="marketSymbol"),
        Column("currency"),
        Column("country", ),
        Column("min_amount", alias="minAmount"),
    ],
    statement_fields=[
        StatementField("isTypeOne", statement="CASE WHEN e.type = 1 then True else False END")
    ],
    order=[
        Order(type=OrderType.asc, alias="name")
    ],
    relations=[
        Relation(
            table="parties",
            alias="p",
            columns=[
                SimpleColumn("name"),
                SimpleColumn("short_name", alias="shortName"),
            ],
            join_forced=False,
            join_type=JoinType.left,
            join_through=JoinThrough(from_column_name="issuer_id", to_column_name="id")
        )
    ]
)


# repository definition
class EquitiesRepo(PostgresRepository):

    def __init__(self, pool: Pool):
        super().__init__(pool, equities)


# repository usage

request = HTTPRequest()

repo = EquitiesRepo(await get_pool())

await repo.find_by_pk(Key(request.path_params["id"]), request.query_params.fields)

await repo.exists_by_pk(Key("9448a57b-f686-4935-b152-566baab712db"))

await repo.find_one(
    request.query_params.fields,
    conditions=request.query_params.conditions,
    order=request.query_params.order)

await repo.find_all(
    request.query_params.fields,
    conditions=request.query_params.conditions,
    order=request.query_params.order)

await repo.find_all_by_pk(
    [
        Key("9448a57b-f686-4935-b152-566baab712db"),
        Key("43c8ec37-9a59-44eb-be90-def391ba2f02")
    ],
    aliases=request.query_params.fields,
    order=request.query_params.order)

await repo.find_many(
    request.query_params.fields,
    conditions=request.query_params.conditions,
    page=request.query_params.page,
    order=request.query_params.order)

await repo.insert({
    "name": "Bursa de Valori Bucuresti SA",
    "type": 1,
    "industrySector": 40,
    "isin": "ROBVBAACNOR0",
    "bloombergCode": "BBG000BBWMC5",
    "marketSymbol": "BVB RO Equity",
    "currency": "RON",
    "country": "RO",
})

await repo.insert_bulk(
    aliases=["name", "type", "industrySector", "isin", "bloombergCode", "marketSymbol", "currency", "country"],
    data=[
        ["Bursa de Valori Bucuresti SA", 1, 40, "ROBVBAACNOR0", "BBG000BBWMC5", "BVB RO Equity", "RON", "RO"],
        ["Citigroup Inc", 1, 40, "US1729674242", "BBG000FY4S11", "C US Equity", "USD", "US"],
        ["Coca-Cola HBC AG", 1, 49, "CH0198251305", "BBG004HJV2T1", "EEE GA Equity", "EUR", "GR"],
    ]
)

await repo.update({
    "type": 1,
    "isin": 40,
}, request.query_params.conditions, request.query_params.fields)

await repo.update_by_pk(Key("9448a57b-f686-4935-b152-566baab712db"), {
    "type": 1,
    "isin": 40
})

await repo.delete(request.query_params.conditions, ["id", "name", "type"])

await repo.delete_by_pk(Key("9448a57b-f686-4935-b152-566baab712db"), ["id", "name", "type"])

await repo.fetch("SELECT * FROM equities WHERE type = $1 and isin = $2", [1, "TREEGYO00017"])

await repo.fetch_one("SELECT * FROM equities WHERE id = $1", ["2b67122a-f47e-41b1-b7f7-53be5ca381a0"])

await repo.execute("DELETE FROM equities WHERE id = $1", ["2b67122a-f47e-41b1-b7f7-53be5ca381a0"])
```

### Query params format

```
fields=name, type, industrySector, isin, bloombergCode, parties_name, parties_shortName
type=1
isin=range(40, 49)
id=any(9448a57b-f686-4935-b152-566baab712db, 43c8ec37-9a59-44eb-be90-def391ba2f02)
page_no=1
page_size=50
top_size=50
order=name, id DESC
```

### Local Development Requirements

To use the SAM CLI, you need the following tools.

* [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3](https://www.python.org/downloads/)
* [Docker](https://hub.docker.com/search/?type=edition&offering=community)

### Run server locally

```bash
# open ssh tunel
sudo sh ssh_tunnel_Analog_JBox.sh
# apply code changes to docker image
sam-api$ sam build
# start server locally on http://127.0.0.1:3000
sam-api$ sam local start-api --warm-containers EAGER
# or run function locally using event.json as parameter
sam-api$ sam local invoke ApiFunction --event events/event.json
```

### Deploy to AWS

```bash
sam build --use-container
sam deploy --capabilities CAPABILITY_NAMED_IAM --guided --profile analog_user --region eu-west-1
```

### Build and deploy new package version using twine

```bash
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine
```

```bash
python3 -m build
twine upload --skip-existing dist/*
```

### Resources

* [SAM template.yml](https://github.com/aws/serverless-application-model/blob/master/docs/internals/generated_resources.rst)
* [asyncpg driver](https://magicstack.github.io/asyncpg/current/)
* [PyPika query builder](https://pypika.readthedocs.io/en/latest/)
* [Pydantic](https://docs.pydantic.dev/)
