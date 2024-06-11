import os
import time

from rich.live import Live

from helper.Config import Config
from helper.logger import log
from providers import ChatProvider


class GoogleChatProvider(ChatProvider):
    provider = "google"
    CONFIG_FILE = os.path.expanduser("~/.google_config")
    unit = 'char/s'

    def __init__(self):
        from google import generativeai as genai
        super().__init__()

        self.config = Config(self.CONFIG_FILE)
        self.genai = genai
        self.genai.configure(api_key=self._get_api_key())

    def models(self) -> list[str]:
        models = list(self.genai.list_models())

        return [model.name for model in models]

    def calculate_input_token(self, messages):
        # google uses characters instead of tokens
        return sum(len(message['content']) for message in messages)

    def chat(self, messages, **kwargs):
        self.input_token = self.calculate_input_token(messages)
        self.total_input_token += self.input_token

        self.response_token = 0
        self.generation_start_time = time.time()

        messages = self._to_google_message_history(messages)

        model = self.genai.GenerativeModel(self.config.model)
        return model.generate_content(messages, stream=True)

    def print_messages(self, response):
        with Live(refresh_per_second=3) as live:
            for chunk in response:
                self.response_text += chunk.text
                self.response_token += len(chunk.text)

                self.update_live_ai_message(live)
            self.update_live_ai_message(live)

        self.total_response_token += self.response_token
        self.print_footer()

    def _to_google_message_history(self, messages):
        return [self._create_content(message) for message in messages]

    @staticmethod
    def _create_content(message):
        from google.ai.generativelanguage import Content, Part

        content = Content()
        content.role = message['role'] if message['role'] == 'user' else 'model'
        content.parts.append(Part(text=message['content']))
        return content

    def _model_cost(self, input_tokens: int, output_tokens: int) -> float:
        one_k = 1_000
        model_rate = {
            "models/gemini-1.5-flash": {'input': 0.000125 / one_k, 'output': 0.000375 / one_k},
            "models/gemini-1.5-pro": {'input': 0.00125 / one_k, 'output': 0.00375 / one_k},
            "models/gemini-1.0": {'input': 0.000125 / one_k, 'output': 0.000375 / one_k},
        }

        for model_name, rate in model_rate.items():
            if model_name in self.config.model:
                return round(input_tokens * rate['input'] + output_tokens * rate['output'], 5)

        log.info('[yellow]Pricing info not found for model[/yellow]')
        return 0.0

    def cost(self) -> float:
        return self._model_cost(self.input_token, self.response_token)

    def total_cost(self) -> float:
        return self._model_cost(self.total_input_token, self.total_response_token)
