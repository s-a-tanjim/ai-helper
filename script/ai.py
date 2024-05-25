import os
import re

import inquirer
import rich_click as click
from inquirer import prompt

from helper import prompt_helper, openai_helper, console_helper
from helper.ChatProviders import get_chat_provider
from helper.console_helper import chat_in_console
from helper.console_helper import console


@click.group()
def cli():
    pass


def add_common_options(func):
    func = click.option('--model', '-m', help="Model to use")(func)
    func = click.option('--provider', '-p', help="Provider to use")(func)
    return func


@cli.command('provider', help="Select a provider")
def select_provider():
    global_config = openai_helper.global_config
    console.log("Current provider:", global_config.provider)

    questions = [
        inquirer.List(
            'provider',
            message="Select a provider",
            choices=global_config.providers,
        )
    ]
    answers = prompt(questions)
    global_config.provider = answers['provider']
    global_config.save()


@cli.command('model', help="Select a model")
@add_common_options
def select_model(provider, model):
    global_config = openai_helper.global_config
    chat_provider = get_chat_provider(global_config.provider)
    console.log("Current provider:", global_config.provider, "Current model:", chat_provider.get_model())

    if provider and provider != global_config.provider:
        global_config.provider = provider
        global_config.save()

    chat_provider.set_model(model)
    chat_provider.save()


def set_provider(provider):
    if provider:
        openai_helper.global_config.provider = provider


@cli.command('cli', help="Generates cli command using GPT-3")
@click.argument('query', nargs=-1)
@click.option('--long', '-l', is_flag=True, help="provides additional information")
@add_common_options
def cli_gpt_completion(query, long, model, provider):
    set_provider(provider)

    if os.name == 'posix':
        prompt_text = prompt_helper.cli_linux_prompt_long if long else prompt_helper.cli_linux_prompt_short
    else:
        console.log("[yellow]Windows detected[/yellow]")
        prompt_text = prompt_helper.cli_windows_prompt_long if long else prompt_helper.cli_windows_prompt_short

    messages = [{'role': 'system', 'content': prompt_text}]

    last_message_text = chat_in_console(model, messages, query, temperature=0.0)

    try:
        command = re.findall(r'```(?:\w+\n)?(.*?)```', last_message_text, re.MULTILINE | re.DOTALL)[0]
        if command:
            console_helper.copy_to_clipboard(command)

    except IndexError:
        console.log("[yellow]No command found[/yellow]")


@cli.command('gr', help="Grammar")
@click.argument('query', nargs=-1)
@add_common_options
def gr_completion(query, model, provider):
    set_provider(provider)

    messages = [{'role': 'system', 'content': prompt_helper.grammar_system_prompt}]
    chat_in_console(model, messages, query)


@cli.command('chat', help="Chat with GPT-3")
@click.argument('query', nargs=-1)
@add_common_options
def chat(query, model, provider):
    set_provider(provider)

    messages = [
        {'role': 'system', 'content': 'You are a helpful AI assistant. Respond always with Markdown.'},
    ]
    chat_in_console(model, messages, query)


@cli.command('summary', help="Summarize text")
@click.argument('query', nargs=-1)
@add_common_options
def summary(query, model, provider):
    set_provider(provider)

    messages = [
        {'role': 'system', 'content': prompt_helper.summary_prompt},
    ]
    if not query:
        query = console_helper.get_clipboard_text()

    chat_in_console(model, messages, query)


@cli.command('commit', help="Auto generate commit message & does the commit")
@add_common_options
def commit(model, provider):
    set_provider(provider)

    messages = [
        {'role': 'system', 'content': prompt_helper.commit_prompt_template},
    ]

    code_diff = prompt_helper.get_code_diff()

    commit_message = chat_in_console(model, messages, [code_diff + prompt_helper.commit_prompt_instruction])
    commit_message = commit_message.strip()

    console.log("Commit message:", commit_message)
    if commit_message and click.confirm("Do you want to commit?"):
        os.system(f'git commit -m "{commit_message}"')


if __name__ == '__main__':
    cli()
