import os

from rich.live import Live

from helper.Config import Config
from providers import OpenAIChatProvider, ChatProvider


class Ai21ChatProvider(OpenAIChatProvider):
    provider = "ai21"
    CONFIG_FILE = os.path.expanduser("~/.ai21_config")
    unit = 'tok/s'

    def __init__(self):
        from ai21 import AI21Client
        ChatProvider.__init__(self)

        self.config = Config(self.CONFIG_FILE)
        self.client = AI21Client(api_key=self._get_api_key())

    def _model_cost(self, input_tokens: int, output_tokens: int) -> float:
        k = 1_000
        million = 1_000_000
        model_rate = {
            "j2-instruct": {'input': 0.5 / million, 'output': 0.7 / million},
            "j2-ultra": {'input': 0.002 / k, 'output': 0.01 / k},
            "j2-mid": {'input': 0.000255 / k, 'output': 0.00125 / k},
            "j2-light": {'input': 0.0001 / k, 'output': 0.0005 / k},
        }.get(
            self.config.model,
            {'input': 0.0, 'output': 0.0}
        )

        return round(input_tokens * model_rate['input'] + output_tokens * model_rate['output'], 4)

    @staticmethod
    def _to_ai21_message_history(messages):
        from ai21.models.chat import ChatMessage

        return [
            ChatMessage(role=message['role'], content=message['content'])
            for message in messages
        ]

    def create_chat_completions(self, messages, **kwargs):
        transformed_messages = self._to_ai21_message_history(messages)

        return self.client.chat.completions.create(
            model='jamba-instruct',
            messages=transformed_messages,
            stream=True
        )

    def models(self) -> list[str]:
        return ['jamba-instruct']
