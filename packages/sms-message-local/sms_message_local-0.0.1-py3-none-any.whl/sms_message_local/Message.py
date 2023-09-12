from abc import ABC, abstractmethod

from item_local.item import Item


class Message(Item, ABC):
    def __init__(self, message_content: str, message_importance: int) -> None:
        self.message_content = message_content
        self.message_importance = message_importance

    @abstractmethod
    def send(self, recipient: str) -> None:
        pass

    @abstractmethod
    def was_read(self) -> bool:
        pass

    @abstractmethod
    def importance(self) -> int:
        pass
