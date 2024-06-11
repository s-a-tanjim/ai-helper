import os

from rich.live import Live

from helper.Config import Config
from providers import OpenAIChatProvider


class CohereChatProvider(OpenAIChatProvider):
    provider = "cohere"
    CONFIG_FILE = os.path.expanduser("~/.cohere_config")
    unit = 'tok/s'

    def __init__(self):
        import cohere
        super().__init__()

        self.config = Config(self.CONFIG_FILE)
        self.client = cohere.Client(api_key=self._get_api_key())

    def _model_cost(self, input_tokens: int, output_tokens: int) -> float:
        million = 1_000_000
        # @formatter:off
        model_rate = {
            'command-r-plus'       : {'input': 3.00 / million, 'output': 15.00 / million},
            'command-r'            : {'input': 0.50 / million, 'output': 1.50 / million},
            'command-nightly'      : {'input': 3.00 / million, 'output': 15.00 / million},
            'command-light-nightly': {'input': 0.50 / million, 'output': 1.50 / million},
            'c4ai-aya-23'          : {'input': 0.50 / million, 'output': 1.50 / million},
            'command'              : {'input': 0.50 / million, 'output': 1.50 / million},
            'command-light'        : {'input': 0.50 / million, 'output': 1.50 / million},
        }.get(
            self.config.model,
            {'input': 0.0, 'output': 0.0}
        )
        # @formatter:on

        return round(input_tokens * model_rate['input'] + output_tokens * model_rate['output'], 4)

    def models(self) -> list[str]:
        return [model.name for model in self.client.models.list().models if
                any([e in model.endpoints for e in ['generate', 'chat', 'summarize']])]

    @staticmethod
    def _to_cohere_chat_history(messages):
        role_map = {
            'system': 'CHATBOT',
            'user': 'USER'
        }
        return [{'role': role_map[message['role']], 'text': message['content']} for message in messages]

    def create_chat_completions(self, messages, **kwargs):
        transformed_messages = self._to_cohere_chat_history(messages)

        return self.client.chat_stream(
            model=self.config.model,
            message=transformed_messages[-1]['text'],
            chat_history=transformed_messages[:-1]
        )

    def print_messages(self, response):
        with Live(refresh_per_second=6) as live:
            for event in response:
                if event.event_type == 'stream-end':
                    self.update_live_ai_message(live)
                    break

                if event.event_type == 'text-generation':
                    self.response_text += event.text
                    self.response_token += 1

                self.update_live_ai_message(live)

        self.total_response_token += self.response_token
        self.print_footer()
