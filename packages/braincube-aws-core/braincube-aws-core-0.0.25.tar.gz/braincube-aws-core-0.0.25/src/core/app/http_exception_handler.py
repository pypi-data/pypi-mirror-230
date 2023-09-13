from json import dumps
from http import HTTPStatus
from abc import ABC, abstractmethod


class HttpExceptionHandler(ABC):
    """Global exception handler for APIGateway events in order to customize error messages and HTTP status codes."""

    @abstractmethod
    def handle(self, error: Exception) -> tuple[HTTPStatus, str, dict]:
        """Method that is invoked every time an exception occurred."""
        raise NotImplementedError()


class BaseHttpExceptionHandler(HttpExceptionHandler):

    def handle(self, error: Exception) -> tuple[HTTPStatus, str, dict]:
        print(f"error:: {error}")
        return HTTPStatus.BAD_REQUEST, dumps({"message": str(error)}), dict()
