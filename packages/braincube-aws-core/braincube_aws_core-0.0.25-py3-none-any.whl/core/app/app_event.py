from .app_processor import AppProcessor
from .data import EventType, EventPayload


class AppEvent(AppProcessor):
    """Module with which you can define AWS events like Cognito and SQS, except
    APIGateway (use AppController instead).
    """

    def __init__(self):
        self._triggers = dict()

    @property
    def data_type(self) -> type:
        return EventPayload

    @property
    def handlers(self) -> dict[str, tuple[callable, dict | None]]:
        return self._triggers

    def event(self, event_type: EventType, subtype: str = None, qualifier: dict = None):
        """Function that represents an event.
        :param event_type: Type of event.
        :param subtype: Topic of event.
        :param qualifier: Dictionary, used by injection package in order to
         specify components by name in case of multiple implementations.
        """

        def _event(func: callable):
            self._triggers[f"{event_type.value}::{subtype}" if subtype else str(event_type.value)] = func, qualifier
            return func

        return _event

    def cognito(self, trigger_source: str = None, qualifier: dict = None):
        """Function that represents a Cognito event.
        :param trigger_source: Local user trigger source of Amazon Cognito API.
        :param qualifier: Dictionary, used by injection package in order to
         specify components by name in case of multiple implementations.
        """

        return self.event(EventType.cognito, trigger_source, qualifier)

    def sqs(self, qualifier: dict = None):
        """Function that represents an Amazon Simple Queue Service.
        :param qualifier: Dictionary, used by injection package in order to
         specify components by name in case of multiple implementations.
        """

        return self.event(EventType.sqs, qualifier)
