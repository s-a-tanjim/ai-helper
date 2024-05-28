import functools
import os
import re

import inquirer
import rich_click as click
from inquirer import prompt

from helper import prompt_helper, Config, console_helper
from helper.ChatProviders import get_chat_provider
from helper.console import console
from helper.console_helper import chat_in_console, log


@click.group()
def cli():
    pass


def add_common_options(func):
    func = click.option('--model', '-m', help="Model to use")(func)
    func = click.option('--provider', '-p', help="Provider to use")(func)
    func = click.option('--debug', '-d', is_flag=True, help="Debug mode")(func)
    return func


def add_common_functionality(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('provider'):
            Config.global_config.provider = kwargs['provider']
        kwargs.pop('provider')

        Config.global_config.debug = kwargs['debug']
        log.setLevel('DEBUG' if kwargs['debug'] else 'INFO')
        kwargs.pop('debug')

        return func(*args, **kwargs)

    return wrapper


def add_common_llm_options(func):
    func = click.option('--temperature', '-t', help="Temperature for sampling", type=float)(func)
    func = click.option('--top_p', '-tp', help="Top-p for sampling", type=float)(func)
    func = click.option('--top_k', '-tk', help="Top-k for sampling", type=float)(func)
    return func


@cli.command('provider', help="Select a provider")
def select_provider():
    global_config = Config.global_config
    log.info(f"Current provider: {global_config.provider}")

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
@click.option('--provider', '-p', help="Provider to use")
@click.option('--debug', '-d', is_flag=True, help="Debug mode")
def select_model(provider, debug):
    global_config = Config.global_config
    global_config.debug = debug

    provider = provider or global_config.provider

    chat_provider = get_chat_provider(provider)
    log.info(f"Current provider: {provider} Current model: {chat_provider.get_model()}")

    if provider and provider != global_config.provider:
        global_config.provider = provider
        global_config.save()

    chat_provider.set_model()
    chat_provider.save()


@cli.command('cli', help="Generates cli commands")
@click.argument('query', nargs=-1)
@click.option('--long', '-l', is_flag=True, help="provides additional information")
@add_common_options
@add_common_functionality
@add_common_llm_options
def cli_gpt_completion(query, long, model, **kwargs):
    if os.name == 'posix':
        prompt_text = prompt_helper.cli_linux_prompt_long if long else prompt_helper.cli_linux_prompt_short
    else:
        log.info("[yellow]Windows detected[/yellow]")
        prompt_text = prompt_helper.cli_windows_prompt_long if long else prompt_helper.cli_windows_prompt_short

    messages = [{'role': 'system', 'content': prompt_text}]
    last_message_text = chat_in_console(model, messages, query, **kwargs)

    try:
        command = re.findall(r'```(?:\w+\n)?(.*?)```', last_message_text, re.MULTILINE | re.DOTALL)[0]
        if command:
            console_helper.copy_to_clipboard(command)

    except IndexError:
        log.info("[yellow]No command found[/yellow]")


@cli.command('gr', help="Grammar")
@click.argument('query', nargs=-1)
@add_common_options
@add_common_functionality
@add_common_llm_options
def gr_completion(query, model, **kwargs):
    messages = [{'role': 'system', 'content': prompt_helper.grammar_system_prompt}]
    chat_in_console(model, messages, query, **kwargs)


@cli.command('chat', help="Chat with GPT-3")
@click.argument('query', nargs=-1)
@add_common_options
@add_common_functionality
@add_common_llm_options
def chat(query, model, **kwargs):
    messages = [
        {'role': 'system', 'content': 'You are a helpful AI assistant. Respond always with Markdown.'},
    ]
    chat_in_console(model, messages, query, **kwargs)


@cli.command('summary', help="Summarize text")
@click.argument('query', nargs=-1)
@add_common_options
@add_common_functionality
@add_common_llm_options
def summary(query, model, **kwargs):
    messages = [
        {'role': 'system', 'content': prompt_helper.summary_prompt},
    ]
    if not query:
        query = console_helper.get_clipboard_text()

    chat_in_console(model, messages, query, **kwargs)


@cli.command('commit', help="Auto generate commit message & does the commit")
@add_common_options
@add_common_functionality
@add_common_llm_options
def commit(model, **kwargs):
    messages = [
        {'role': 'system', 'content': prompt_helper.commit_prompt_template},
    ]

    code_diff = prompt_helper.get_code_diff()
    query = f"Summarize this git diff into a useful commit message: \n{code_diff}"

    commit_message = chat_in_console(model, messages, query, **kwargs)
    commit_message = commit_message.strip()

    log.info(f"Commit message: {commit_message}")
    if commit_message and click.confirm("Do you want to commit?"):
        os.system(f'git commit -m "{commit_message}"')


@cli.group()
def custom():
    pass


@custom.command('create', help="Create a custom prompt")
@click.argument('name')
@click.argument('system')
def custom_create(name, system):
    # error out if the name collides with a built-in command
    if name in cli.commands:
        log.info(f"[red]Error:[/red] Command '{name}' conflicts with a built-in commands! Use a different name.")
        return

    Config.global_config.prompts[name] = system
    Config.global_config.save()


@custom.command('list', help="List custom prompts")
def custom_create():
    for name, system in Config.global_config.prompts.items():
        console.print(name, ": ", system)


def load_custom_prompts():
    if not Config.global_config.prompts:
        return

    for name, system in Config.global_config.prompts.items():
        @cli.command(name, help="Custom prompt")
        @click.argument('query', nargs=-1)
        @add_common_options
        @add_common_functionality
        def _custom_prompt(query, model):
            messages = [
                {'role': 'system', 'content': system},
            ]
            chat_in_console(model, messages, query)


load_custom_prompts()

if __name__ == '__main__':
    cli()
