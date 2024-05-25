import os
import re

import inquirer
import rich_click as click
from inquirer import prompt

from helper import prompt_helper, openai_helper, console_helper
from helper.console_helper import chat_in_console, chat_in_console_ollama2


@click.group()
def cli():
    pass


@cli.command('provider', help="Select a provider")
def select_provider():
    try:
        print("Current provider:", openai_helper.config.provider)
    except AttributeError:
        print("Current provider: openai")

    providers = ['openai', 'ollama']
    questions = [
        inquirer.List('provider',
                      message="Select a provider",
                      choices=providers,
                      )
    ]
    answers = prompt(questions)
    openai_helper.set_provider(answers['provider'])


@cli.command('model', help="Select a model")
def select_model():
    from pprint import pprint

    print("Current model:", openai_helper.config.model)
    models = list(openai_helper.get_models())
    try:
        models.sort(key=lambda x: x.name)
        mode_names = [model.name for model in models]
    except AttributeError:
        models.sort(key=lambda x: x.id)
        mode_names = [model.id for model in models]

    questions = [
        inquirer.List('model',
                      message="Select a model",
                      choices=mode_names,
                      )
    ]
    answers = prompt(questions)
    openai_helper.set_model(answers['model'])
    model = openai_helper.get_model_details()
    pprint(model)


def add_common_options(func):
    func = click.option('--model', '-m', help="Model to use")(func)
    func = click.option('--provider', '-p', help="Provider to use")(func)
    return func


def set_mode_and_provider(model, provider):
    if model:
        openai_helper.set_model(model, save=False)
    if provider:
        openai_helper.set_provider(provider, save=False)

    console_helper.console.log(f"Provider: {openai_helper.config.provider}, Model: {openai_helper.config.model}")


@cli.command('cli', help="Generates cli command using GPT-3")
@click.argument('query', nargs=-1)
@click.option('--long', '-l', is_flag=True, help="provides additional information")
@add_common_options
def cli_gpt_completion(query, long, model, provider):
    set_mode_and_provider(model, provider)

    if os.name == 'posix':
        prompt_text = prompt_helper.unix_prompt_gpt35 if long else prompt_helper.unix_prompt_gpt35_short
    else:
        console_helper.console.log("[yellow]Windows detected[/yellow]")
        prompt_text = prompt_helper.windows_prompt_gpt35 if long else prompt_helper.windows_prompt_gpt35_short

    messages = [{'role': 'system', 'content': prompt_text}]

    if openai_helper.config.provider == "ollama":
        last_message_text = chat_in_console_ollama2(messages, query)
    elif openai_helper.config.provider == "openai":
        last_message_text = chat_in_console(messages, query, temperature=0)

    try:
        command = re.findall(r'```(?:\w+\n)?(.*?)```', last_message_text, re.MULTILINE | re.DOTALL)[0]
        if command:
            console_helper.copy_to_clipboard(command)
    except IndexError:
        console_helper.console.log("[yellow]No command found[/yellow]")


@cli.command('gr', help="Grammar")
@click.argument('query', nargs=-1)
@add_common_options
def gr_completion(query, model, provider):
    set_mode_and_provider(model, provider)

    messages = [{'role': 'system', 'content': prompt_helper.grammer_system_prompt}]
    if openai_helper.config.provider == "ollama":
        chat_in_console_ollama2(messages, query)
    else:
        chat_in_console(messages, query)


@cli.command('assessment', help="Guess assessment hours")
@click.argument('query', nargs=-1)
@add_common_options
def assessment_completion(query, model, provider):
    set_mode_and_provider(model, provider)

    messages = [
        {'role': 'system', 'content': prompt_helper.assessment},
    ]

    if openai_helper.config.provider == "ollama":
        chat_in_console_ollama2(messages, query)
    else:
        chat_in_console(messages, query)


@cli.command('chat', help="Chat with GPT-3")
@click.argument('query', nargs=-1)
@add_common_options
def chat(query, model, provider):
    set_mode_and_provider(model, provider)

    messages = [
        {'role': 'system', 'content': 'You are a helpful AI assistant. Respond always with Markdown.'},
    ]

    if openai_helper.config.provider == "ollama":
        chat_in_console_ollama2(messages, query)
    else:
        chat_in_console(messages, query)


@cli.command('summary', help="Summarize text")
@click.argument('query', nargs=-1)
@add_common_options
def summary(query, model, provider):
    set_mode_and_provider(model, provider)

    messages = [
        {'role': 'system', 'content': prompt_helper.summary_prompt},
    ]
    if not query:
        # get from clipboard
        query = console_helper.get_clipboard_text()

    if openai_helper.config.provider == "ollama":
        chat_in_console_ollama2(messages, query)
    else:
        chat_in_console(messages, query)


@cli.command('commit', help="Auto generate commit message & does the commit")
@add_common_options
def commit(model, provider):
    set_mode_and_provider(model, provider)

    messages = [
        {'role': 'system', 'content': prompt_helper.commit_prompt_template},
    ]

    code_diff = prompt_helper.get_code_diff()

    if openai_helper.config.provider == "ollama":
        commit_message = chat_in_console_ollama2(messages, [code_diff + prompt_helper.commit_prompt_instruction])
    else:
        commit_message = chat_in_console(messages, [code_diff + prompt_helper.commit_prompt_instruction])

    commit_message = commit_message.strip()
    console_helper.console.log("Commit message:", commit_message)
    if commit_message and click.confirm("Do you want to commit?"):
        os.system(f'git commit -m "{commit_message}"')


if __name__ == '__main__':
    cli()
