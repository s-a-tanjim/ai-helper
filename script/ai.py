import os
import random
import re
import time

import pyperclip
import rich_click as click
from pick import pick
from rich.live import Live
from rich.markdown import Markdown
from rich.status import Status
from rich.table import Table
from rich_click.cli import patch

from helper import prompt_helper, openai_helper, console_helper
from helper.console_helper import chat_in_console

patch()


@click.group()
def cli():
    pass


@click.command('model', help="Select a model")
def select_model():
    print("Current model:", openai_helper.config.model)
    models = openai_helper.get_models()
    option, index = pick([model.id for model in models.data], "Select a model")
    openai_helper.set_model(option)


@click.command('cli', help="Generates cli command using GPT-3")
@click.argument('query', nargs=-1)
def cli_gpt_completion(query):
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [{'role': 'system', 'content': prompt_helper.unix_prompt_gpt35}]
    last_message_text = chat_in_console(messages, query)

    try:
        command = re.findall(r'```(.*?)```', last_message_text)[0]
        if command:
            pyperclip.copy(command)
            console_helper.console.log("[green]Copied to clipboard: [/green]", command)
    except IndexError:
        console_helper.console.log("[yellow]No command found[/yellow]")


@click.command('gr', help="Grammar")
@click.argument('query', nargs=-1)
def gr_completion(query):
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [{'role': 'system', 'content': prompt_helper.grammer_system_prompt}]
    chat_in_console(messages, query)


@click.command('assessment', help="Guess assessment hours")
@click.argument('query', nargs=-1)
def assessment_completion(query):
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [
        {'role': 'system', 'content': prompt_helper.assessment},
    ]

    chat_in_console(messages, query)


@click.command('chat', help="Chat with GPT-3")
@click.argument('query', nargs=-1)
def chat(query):
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [
        {'role': 'system', 'content': 'You are a helpful AI assistant. Respond always with Markdown.'},
    ]

    chat_in_console(messages, query)


cli.add_command(select_model)
cli.add_command(gr_completion)
cli.add_command(cli_gpt_completion)
cli.add_command(assessment_completion)
cli.add_command(chat)

if __name__ == '__main__':
    cli()
