import os
import sys

from rich.console import Console
from rich.prompt import Prompt

from helper import openai_helper
from helper.ChatProviders import get_chat_provider

console = Console()


def copy_to_clipboard(text):
    import pyperclip

    try:
        pyperclip.copy(text.strip())
    except ModuleNotFoundError:
        if os.name == 'posix':
            os.system(f'echo "{text}" | xclip -selection clipboard')
        else:
            os.system(f'echo "{text}" | clip')

    pyperclip.copy(text.strip())
    console.log("[green]Copied to clipboard: [/green]", text)


def get_clipboard_text():
    import pyperclip
    try:
        return pyperclip.paste()
    except ModuleNotFoundError:
        if os.name == 'posix':
            return os.popen('xclip -o').read()
        else:
            return os.popen('clip').read()


def get_multiline_input(prompt=""):
    lines = []

    while True:
        line = Prompt.ask(f"\r[b]  {prompt}[/b]")
        if not line:
            sys.stdout.write("\033[F")
            break
        lines.append(line)

    return "\n".join(lines)


def chat_in_console(model, messages, query, **kwargs):
    chat_provider = get_chat_provider(openai_helper.global_config.provider)
    if model:
        chat_provider.set_model(model)
    console.log(f"Provider: {chat_provider.provider}, Model: {chat_provider.get_model()}")

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


def print_current_provider(chat_provider):
    console.log(f"Current Provider: {chat_provider.provider}, Model: {chat_provider.get_model()}")
