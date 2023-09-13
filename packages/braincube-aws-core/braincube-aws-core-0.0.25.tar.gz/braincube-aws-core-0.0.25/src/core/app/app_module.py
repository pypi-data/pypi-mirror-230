import time
from json import dumps
from inspect import signature
from typing import get_args, get_origin

from .data import *
from .app_processor import AppProcessor
from .http_exception_handler import HttpExceptionHandler, BaseHttpExceptionHandler

from ..utils.convert import JSONEncoder
from ..di.injector import IInjector
from ..di.injector_manager import IInjectionManager, InjectionManager


class AppModule:
    """AWS lambda application main entry point.
    :param processors: AWS event resources.
    :param injectors: Components injected to application.
    :param ex_handler: APIGateway global exception handler.
    """

    def __init__(self, processors: list[AppProcessor] = None,
                 injectors: list[IInjector] = None,
                 ex_handler: HttpExceptionHandler = BaseHttpExceptionHandler()):

        manager: IInjectionManager = InjectionManager()
        if injectors:
            manager.store_injectors(injectors)
        self._injector_manager = manager

        self._exception_handler = ex_handler

        self._handlers = dict()

        if not processors:
            return

        for proc in processors:
            for event_alias, (func, qualifier) in proc.handlers.items():
                dependencies = list()
                payload_type: type | None = None
                data = qualifier.copy() if qualifier else dict()
                for key, value in signature(func).parameters.items():
                    origin = get_origin(value.annotation)
                    cls = origin if origin else value.annotation
                    if cls is proc.data_type:
                        args = get_args(value.annotation)
                        payload_type = args[0] if len(args) > 0 else dict
                        continue
                    dependencies.append((cls, data.get(key)))
                if not payload_type:
                    raise Exception(f"{str(proc.data_type)} param is not provided.")
                self._handlers[event_alias] = Handler(func, payload_type, dependencies)

    async def serve(self, event: dict, context):

        if "httpMethod" in event:
            return await self._serve_http(event, context)

        if "triggerSource" in event:
            event_type = EventType.cognito
        elif event.get("Records") and event["Records"][0]["eventSource"] == "aws:sqs":
            event_type = EventType.sqs
        else:
            event_type = None

        if event_type:
            return await self._serve_event(event_type, event, context)

        raise Exception("Handler not found.")

    async def _serve_event(self, event_type: EventType, event: dict, context):

        cognito_unique_key = f"{EventType.cognito.value}::{event.get('triggerSource')}"
        key = str(event_type.value) \
            if event_type is not EventType.cognito or (cognito_unique_key not in self._handlers) \
            else cognito_unique_key

        trigger = self._handlers.get(key)
        if not trigger:
            if event_type is EventType.cognito:
                return event
            raise ValueError(f"unknown event: {key}")

        params = [
            *[await self._injector_manager.provide(c, n) for c, n in trigger.dependencies],
            convert_to_event_payload(trigger.payload_type, event, context)
        ]

        result = await trigger.func(*params)

        return result.dict(by_alias=True) if isinstance(result, BaseModel) else result

    async def _serve_http(self, event: dict, context):

        try:
            start = time.time()

            route = self._handlers[f"{event['resource']}::{event['httpMethod']}"]
            if not route:
                raise ValueError(f"unknown route, resource: {event['resource']} method: {event['httpMethod']}")

            params = [
                *[await self._injector_manager.provide(c, n) for c, n in route.dependencies],
                convert_to_http_request(route.payload_type, event, context)
            ]
            response: HTTPResponse = await route.func(*params)

            status_code = response.status
            body = dumps(response.body, cls=JSONEncoder) if response.body else response.body

            headers = {"X-Process-Time": int((time.time() - start) * 1000)}

            if response.headers:
                headers.update(response.headers)

        except Exception as error:
            status_code, body, headers = self._exception_handler.handle(error)

        headers.update(http_headers)

        return {
            "body": body,
            "headers": headers,
            "statusCode": status_code
        }
