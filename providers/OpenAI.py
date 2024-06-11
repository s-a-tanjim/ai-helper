import os
import time

from rich.live import Live

from helper.Config import Config
from providers import ChatProvider


class OpenAIChatProvider(ChatProvider):
    provider = "openai"
    CONFIG_FILE = os.path.expanduser("~/.openai_config")
    unit = 'tok/s'

    def __init__(self):
        import openai
        super().__init__()

        self.config = Config(self.CONFIG_FILE)
        self.client = openai
        self.client.api_key = self._get_api_key()

    def models(self):
        return [model.id for model in self.client.models.list()]

    def _model_cost(self, input_tokens: int, output_tokens: int) -> float:
        million = 1_000_000
        model_rate = {
            "gpt-3.5-turbo": {'input': 0.50 / million, 'output': 1.50 / million},
            "gpt-4": {'input': 10.00 / million, 'output': 30.00 / million},
            'gpt-4o': {'input': 5.00 / million, 'output': 15.00 / million},
        }.get(
            self.config.model,
            {'input': 0.0, 'output': 0.0}
        )

        return round(input_tokens * model_rate['input'] + output_tokens * model_rate['output'], 4)

    def create_chat_completions(self, messages, **kwargs):
        return self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=True,
            **self.filter_kwargs(kwargs)
        )

    def chat(self, messages, **kwargs):
        self.input_token = self.calculate_input_token(messages)
        self.total_input_token += self.input_token

        self.response_token = 0
        self.generation_start_time = time.time()

        return self.create_chat_completions(messages, **kwargs)

    def cost(self):
        return self._model_cost(self.input_token, self.response_token)

    def total_cost(self):
        return self._model_cost(self.total_input_token, self.total_response_token)

    def print_messages(self, response):
        with Live(refresh_per_second=6) as live:
            for chunk in response:
                for choice in chunk.choices:
                    if choice.finish_reason == 'stop':
                        self.update_live_ai_message(live)
                        break

                    if choice.delta.content:
                        self.response_text += choice.delta.content
                        self.response_token += len(choice.delta.content.split())

                    self.update_live_ai_message(live)

        self.total_response_token += self.response_token
        self.print_footer()

    @staticmethod
    def filter_kwargs(kwargs):
        return {key: value for key, value in kwargs.items() if key in ['temperature', 'top_p']}
