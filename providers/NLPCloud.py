import os

from rich.live import Live

from helper.Config import Config
from providers import OpenAIChatProvider, ChatProvider


class NLPCloudChatProvider(OpenAIChatProvider):
    provider = "nlpcloud"
    CONFIG_FILE = os.path.expanduser("~/.nlpcloud_config")
    unit = 'tok/s'

    def __init__(self):
        ChatProvider.__init__(self)
        self.config = Config(self.CONFIG_FILE)

    def _model_cost(self, input_tokens: int, output_tokens: int) -> float:
        k = 1_000
        # @formatter:off
        model_rate = {
            "chatdolphin"           : {'input': 0.0005 / k, 'output': 0.0005 / k},
            "finetuned-llama-3-70b" : {'input': 0.0018 / k, 'output': 0.0018 / k},
            "dolphin-yi-34b"        : {'input': 0.0005 / k, 'output': 0.0005 / k},
            "dolphin-mixtral-8x7b"  : {'input': 0.0005 / k, 'output': 0.0005 / k},
        }.get(
            self.config.model,
            {'input': 0.0, 'output': 0.0}
        )
        # @formatter:on

        return round(input_tokens * model_rate['input'] + output_tokens * model_rate['output'], 4)

    @staticmethod
    def _to_nlpcloud_message_format(messages):
        text = ""
        context = ""
        history = []

        for message in messages[:-1]:
            if message["role"] == "system":
                context = message["content"]
                continue

            if message["role"] == "user":
                history.append({
                    'input': message["content"],
                })
            elif message["role"] == "assistant":
                history[-1]['output'] = message["content"]
        text = messages[-1]["content"]

        return text, context, history

    def create_chat_completions(self, messages, **kwargs):
        import nlpcloud

        text, context, history = self._to_nlpcloud_message_format(messages)

        self.client = nlpcloud.Client(token=self._get_api_key(), model=self.config.model, gpu=True)
        return self.client.chatbot(text, context, history)

    def print_messages(self, response):
        with Live(refresh_per_second=6) as live:

            self.response_text += response['response']
            self.response_token += len(response['response'].split())

            self.update_live_ai_message(live)

        self.total_response_token += self.response_token
        self.print_footer()

    def models(self) -> list[str]:
        return ["chatdolphin", "finetuned-llama-3-70b", "dolphin-yi-34b", "dolphin-mixtral-8x7b"]
