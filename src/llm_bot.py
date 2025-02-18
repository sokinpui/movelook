from llm_model import LLMModel

class LLMBot:
    def __init__(self, model : LLMModel):
        self.model = model

    def summarize_log(self, logs : str) -> str:
        pass

    def analyze_log(self, logs : str) -> str:
        pass
