from abc import ABC

from rich.live import Live
from rich.markdown import Markdown
from rich.padding import Padding

from helper import openai_helper


class ChatProvider(ABC):
    input_token: int = 0
    response_token: int = 0
    total_input_token: int = 0
    total_response_token: int = 0
    response_text: str = ""

    def __init__(self, model):
        self.model = model

    def chat(self, messages, **kwargs):
        raise NotImplementedError

    def print_messages(self, response):
        raise NotImplementedError

    def cost(self) -> float:
        return 0.0

    def total_cost(self) -> float:
        return 0.0

    def update_live_ai_message(self, live):
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
            f"[dim]Model[/]: {openai_helper.config.model}    "
            f"[dim]Input[/]: {self.total_input_token:<6}"
            f"[dim]Output[/]: {self.total_response_token:<6}"
            f"[dim]Total[/]: {self.total_input_token + self.total_response_token:<6}"
            f"[dim]Cost[/]: {self.total_cost():<.4f}",
        )

    @staticmethod
    def calculate_input_token(messages):
        return sum(len(message['content'].split()) for message in messages)


class OllamaChatProvider(ChatProvider):
    def chat(self, messages, **kwargs):
        import ollama

        self.input_token = self.calculate_input_token(messages)
        self.total_input_token += self.input_token
        self.response_token = 0

        return ollama.chat(model=self.model, messages=messages, stream=True)

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
    def chat(self, messages, **kwargs):
        from helper import openai_helper

        self.input_token = self.calculate_input_token(messages)
        self.total_input_token += self.input_token
        self.response_token = 0

        return openai_helper.chat_completion(messages, stream=True, **kwargs)

    def cost(self):
        return openai_helper.cost(self.input_token, self.response_token)

    def total_cost(self):
        return openai_helper.cost(self.total_input_token, self.total_response_token)

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
