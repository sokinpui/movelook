from langchain_google_genai import ChatGoogleGenerativeAI
import tiktoken
from pydantic import BaseModel, Field
import os

import config as cfg
from logger import Logger


class LLMModel():
    """
    provide common interface for Gemini model, but user can still access the model-specific methods via `self.model`
    """
    def __init__(self):
        self._logger = Logger()
        self.model = None

    def generate(self, prompt: str, schema):
        if schema:
            model = self.model.with_structured_output(schema)
            structured_output = model.invoke(prompt)
            return structured_output

        response = self.model.invoke(prompt)
        content = response.content

        return content

    def token_count(self, prompt: str) -> int:
        tokenizer = tiktoken.get_encoding("cl100k_base")

        tokens = tokenizer.encode(prompt)
        token_count = len(tokens)
        return token_count

class GeminiModel(LLMModel):
    # Gemini-specific implementation
    def __init__(self):
        super().__init__()

        model = cfg.GEMINI_LLM_MODEL
        api_key = os.environ['GENAI_API_KEY']
        if api_key is None:
            self._logger.error("Please define GENAI_API_KEY in the environment variable")
            raise ValueError("Please define GENAI_API_KEY in the environment variable")
        os.environ["GOOGLE_API_KEY"] = api_key

        try:
            self.model = ChatGoogleGenerativeAI(model=model)
            self._logger.info("Gemini model is using, Gemini model initialized")
        except Exception as e:
            self._logger.error(f"Error in initializing Gemini model: {e}")


def main():
    # test the Gemini model
    model = GeminiModel()

    prompt = "What is the capital of France?"
    response = model.generate(prompt, None)
    print("Unstructured output:")
    print(response + "\n")

    class TestSchema(BaseModel):
        question: str
        answer: str

    response = model.generate(prompt="What is the capital of France?", schema=TestSchema)
    print("Structured output:")
    print(f"Question: {response.question}")
    print(f"Answer: {response.answer}")

if __name__ == "__main__":
    main()
