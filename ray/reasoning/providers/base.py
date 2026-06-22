from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    def think(self, context: dict) -> dict:
        ...
