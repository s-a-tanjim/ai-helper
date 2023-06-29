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


@click.command('cli_gpt', help="Generates cli command using GPT-3")
@click.argument('query', nargs=-1)
def cli_gpt_completion(query):
    query = " ".join(query)
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [
        {'role': 'system', 'content': prompt_helper.unix_prompt_gpt35},
        {'role': 'user', 'content': query},
    ]

    response = openai_helper.chat_completion(messages, stop=["\n\n\n\n"])

    console_helper.console.log("Tokens: ", response.usage.total_tokens)
    console_helper.console.log("Cost: ", openai_helper.cost(response.usage.total_tokens))

    command = ""
    for choice in response.choices:
        if choice.message.content:
            console_helper.console.print(Markdown(choice.message.content))
            try:
                command = re.findall(r'```(.*?)```', choice.message.content)[0]
            except IndexError as e:
                console_helper.console.log(e)

    if command:
        pyperclip.copy(command)


@click.command('gr', help="Grammar")
@click.argument('query', nargs=-1)
def gr_completion(query):
    query = " ".join(query)
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [
        {'role': 'system', 'content': prompt_helper.grammer_system_prompt},
        {'role': 'user', 'content': query},
    ]

    response = openai_helper.chat_completion(messages)

    console_helper.console.log("Tokens: ", response.usage.total_tokens)
    console_helper.console.log("Cost: ", openai_helper.cost(response.usage.total_tokens))

    for choice in response.choices:
        if choice.message.content:
            console_helper.console.print(Markdown(choice.message.content))


@click.command('assessment', help="Guess assessment hours")
@click.argument('query', nargs=-1)
def assessment_completion(query):
    query = " ".join(query)
    query = re.sub(r'\n+', ' ', query)
    console_helper.console.log("Model: ", openai_helper.config.model)

    prompt = prompt_helper.assessment + 'Assessment: ' + query + '\nHours:'
    response = openai_helper.complete(prompt)

    console_helper.console.log("Tokens: ", response.usage.total_tokens)
    console_helper.console.log("Cost: ", openai_helper.cost(response.usage.total_tokens))

    for choice in response.choices:
        if choice.text:
            text = choice.text.replace('\n', '\n\n')
            console_helper.console.print(Markdown('Hours:' + text))
        console_helper.console.print(Markdown('---'))


def generate_table() -> Table:
    """Make a new table."""
    table = Table()
    table.add_column("ID")
    table.add_column("Value")
    table.add_column("Status")

    for row in range(random.randint(2, 6)):
        value = random.random() * 100
        table.add_row(
            f"{row}", f"{value:3.2f}", "[red]ERROR" if value < 50 else "[green]SUCCESS"
        )
    return table


@click.command('chat', help="Chat with GPT-3")
def chat():
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [
        {'role': 'system', 'content': 'You are a helpful AI assistant. Respond always with Markdown.'},
    ]

    cost = 0
    token = 0

    try:
        while True:
            input_text = console_helper.get_multiline_input('You')
            messages.append({'role': 'user', 'content': input_text})

            response = openai_helper.chat_completion(messages, stream=True)

            response_text = ""
            with Live(refresh_per_second=6) as live:
                for chunk in response:
                    for choice in chunk.choices:

                        if choice.finish_reason == 'stop':
                            live.update(Markdown('**AI:** ' + response_text))
                            break

                        if choice.delta.content:
                            response_text += choice.delta.content
                            token += 2

                        live.update(Markdown(
                            '**AI:** ' +
                            response_text +
                            "\n\n---"
                            f"\nResponse Tokens: {token}"
                            f"\nCost: {openai_helper.cost(token)}"
                            "\n\n---"
                        ))

            messages.append({'role': 'system', 'content': response_text})
            console_helper.console.print(Markdown('---'))
            console_helper.console.log("Response Tokens: ", token)
            console_helper.console.log("Cost: ", openai_helper.cost(token))
            console_helper.console.print(Markdown('---'))

    except KeyboardInterrupt:
        pass


cli.add_command(select_model)
cli.add_command(gr_completion)
cli.add_command(cli_gpt_completion)
cli.add_command(assessment_completion)
cli.add_command(chat)

if __name__ == '__main__':
    cli()
