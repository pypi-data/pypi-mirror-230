from abc import ABC, abstractmethod


class AppProcessor(ABC):
    """Abstract module which defines AWS event resources."""

    @property
    @abstractmethod
    def data_type(self) -> type:
        """Property that mentions the event's payload type."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def handlers(self) -> dict[str, tuple[callable, dict | None]]:
        """Dictionary that contains the event's handlers."""
        raise NotImplementedError()
