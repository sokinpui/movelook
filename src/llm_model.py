from abc import ABC, abstractmethod

class LLMModel(ABC):

    # use LangChain to unified interface across different models, so schema is accepted
    @abstractmethod
    def generate(self, prompt: str, schema) -> str:
        pass

    @abstractmethod
    def token_count(self, text: str) -> dict:
        pass

class GeminiModle(LLMModel):
    def generate(self, prompt: str, schema) -> str:
        # Gemini-specific implementation
        pass

    def token_count(self, prompt: str) -> dict:
        # Gemini-specific implementation
        pass
