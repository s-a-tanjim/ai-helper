import os

from helper.Config import Config
from providers import OpenAIChatProvider


class GroqChatProvider(OpenAIChatProvider):
    provider = "groq"
    CONFIG_FILE = os.path.expanduser("~/.groq_config")
    unit = 'tok/s'

    def __init__(self):
        from groq import Groq
        super().__init__()

        self.config = Config(self.CONFIG_FILE)
        self.client = Groq(api_key=self._get_api_key())

    def _model_cost(self, input_tokens: int, output_tokens: int) -> float:
        million = 1_000_000
        model_rate = {
            "llama3-70b-8192": {'input': 0.59 / million, 'output': 0.79 / million},
            'mixtral-8x7b-32768': {'input': 0.24 / million, 'output': 0.24 / million},
            'llama3-8b-8192': {'input': 0.05 / million, 'output': 0.08 / million},
            "gemma-7b-it": {'input': 0.07 / million, 'output': 0.07 / million},
        }.get(
            self.config.model,
            {'input': 0.0, 'output': 0.0}
        )

        return round(input_tokens * model_rate['input'] + output_tokens * model_rate['output'], 4)

    def models(self) -> list[str]:
        return [model.id for model in self.client.models.list().data]
