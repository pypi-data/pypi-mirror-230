from abc import ABC, abstractmethod


class KeyValueStore(ABC):
    @abstractmethod
    def get(self, key: str) -> str:
        ...
