from abc import ABC, abstractmethod
class ILLMService(ABC):
    @abstractmethod
    def generate_report(self, prompt: str) -> str:
        pass
