import os
from abc import ABC

import inquirer
from inquirer import prompt
from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding
from rich.prompt import Prompt

from helper import openai_helper
from helper.openai_helper import Config


class ChatProvider(ABC):
    CONFIG_FILE = None
    provider = None
    config: Config = None

    input_token: int = 0
    response_token: int = 0
    total_input_token: int = 0
    total_response_token: int = 0
    response_text: str = ""

    def __init__(self):
        pass

    def chat(self, messages, **kwargs):
        raise NotImplementedError

    def print_messages(self, response):
        raise NotImplementedError

    def cost(self) -> float:
        return 0.0

    def total_cost(self) -> float:
        return 0.0

    def get_model(self) -> str:
        try:
            return self.config.model
        except AttributeError:
            self.set_model()
            self.save()

            return self.config.model

    def models(self) -> list[str]:
        raise NotImplementedError

    def set_model(self, model: str = None):
        if not model:
            questions = [
                inquirer.List(
                    'model',
                    message="Select a model",
                    choices=self.models(),
                )
            ]
            model = prompt(questions)['model']

        self.config.model = model

    def _get_api_key(self):
        try:
            return self.config.api_key
        except AttributeError:
            self.config.api_key = Prompt.ask(f"Enter your {self.provider} API key")
            self.save()
            return self.config.api_key

    def save(self):
        self.config.save()

    def update_live_ai_message(self, live: Live):
        live.update(
            Padding(
                Markdown(
                    f'**AI:** {self.response_text}\n'
                    f"\nInput: {self.input_token:<10} "
                    f"Output: {self.response_token:<10} "
                    f"Cost: {self.cost():<10.4f}"
                    "\n---"
                ),
                (1, 2, 2, 2)
            )
        )

    def print_footer(self):
        from helper.console_helper import console

        console.rule(
            f"[dim]Model[/]: {self.config.model}    "
            f"[dim]Input[/]: {self.total_input_token:<6}"
            f"[dim]Output[/]: {self.total_response_token:<6}"
            f"[dim]Total[/]: {self.total_input_token + self.total_response_token:<6}"
            f"[dim]Cost[/]: {self.total_cost():<.4f}",
        )

    @staticmethod
    def calculate_input_token(messages):
        return sum(len(message['content'].split()) for message in messages)


class OllamaChatProvider(ChatProvider):
    provider = "ollama"
    CONFIG_FILE = os.path.expanduser("~/.ollama_config")

    def __init__(self):
        import ollama
        super().__init__()

        self.config = openai_helper.Config(self.CONFIG_FILE)
        self.client = ollama

    def models(self) -> list[str]:
        models = self.client.list()['models']

        return [model['name'] for model in models]

    def chat(self, messages, **kwargs):
        self.input_token = self.calculate_input_token(messages)
        self.total_input_token += self.input_token
        self.response_token = 0

        return self.client.chat(model=self.config.model, messages=messages, stream=True)

    def print_messages(self, response):
        with Live(refresh_per_second=6) as live:
            for chunk in response:
                if chunk['done']:
                    self.update_live_ai_message(live)
                    break

                if chunk['message']['content']:
                    self.response_text += chunk['message']['content']
                    self.response_token += len(chunk['message']['content'].split())

                self.update_live_ai_message(live)

        self.total_response_token += self.response_token
        self.print_footer()


class OpenAIChatProvider(ChatProvider):
    provider = "openai"
    CONFIG_FILE = os.path.expanduser("~/.openai_config")

    def __init__(self):
        import openai
        super().__init__()

        self.config = openai_helper.Config(self.CONFIG_FILE)
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

    def chat(self, messages, **kwargs):
        self.input_token = self.calculate_input_token(messages)
        self.total_input_token += self.input_token
        self.response_token = 0

        return self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=True,
            **kwargs
        )

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


def get_chat_provider(provider):
    return {
        "ollama": OllamaChatProvider,
        "openai": OpenAIChatProvider,
    }[provider]()
