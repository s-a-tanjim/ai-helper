import sys

from rich.console import Console
from rich.prompt import Prompt

from helper import openai_helper
from helper.ChatProviders import OllamaChatProvider, OpenAIChatProvider

console = Console()


def get_multiline_input(prompt=""):
    lines = []

    while True:
        line = Prompt.ask(f"\r[b]  {prompt}[/b]")
        if not line:
            sys.stdout.write("\033[F")
            break
        lines.append(line)

    return "\n".join(lines)


def get_chat_provider(provider):
    if provider == "ollama":
        return OllamaChatProvider(openai_helper.config.model)
    else:
        return OpenAIChatProvider(openai_helper.config.model)


def chat_in_console(messages, query, **kwargs):
    chat_provider = get_chat_provider(openai_helper.config.provider)

    while True:
        if query:
            input_text = " ".join(query)
            query = None
        else:
            input_text = get_multiline_input('You')
            if not input_text:
                return chat_provider.response_text

        chat_provider.response_text = ""

        messages.append({'role': 'user', 'content': input_text})
        chat_provider.print_messages(chat_provider.chat(messages, **kwargs))

        messages.append({'role': 'system', 'content': chat_provider.response_text})


def print_current_provider():
    console.log(f"Current Provider: {openai_helper.config.provider}, Model: {openai_helper.config.model}")
