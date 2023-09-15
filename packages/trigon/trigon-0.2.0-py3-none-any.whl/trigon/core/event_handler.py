from abc import ABC, abstractmethod


class EventHandler(ABC):
    event_type: str

    @abstractmethod
    def __call__(self) -> None:
        raise NotImplementedError
