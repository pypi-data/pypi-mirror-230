# abc is a builtin module, we have to import ABC and abstractmethod
from abc import ABC, abstractmethod


class IOperatorService(ABC):     # Decorator to define an abstract method

    @abstractmethod     # Decorator to define an abstract method
    def create_operator(self, config: dict):
        pass
