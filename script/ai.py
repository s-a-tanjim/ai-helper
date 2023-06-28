import os
import re

import rich_click as click
from pick import pick
from rich.markdown import Markdown
from rich.status import Status
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


@click.command('cli', help="Generates cli commands")
@click.argument('query', nargs=-1, required=True)
def cli_completion(query):
    query = " ".join(query)
    console_helper.console.log("Model: ", openai_helper.config.model)

    if os.name == "nt":
        prompt = prompt_helper.powershell_prompt
        console_helper.console.log("Detected Windows")
    else:
        prompt = prompt_helper.unix_prompt
        console_helper.console.log("Detected Unix")

    prompt = prompt + query + "\nA -"
    response = openai_helper.complete(prompt)

    console_helper.console.log("Tokens: ", response.usage.total_tokens)
    console_helper.console.log("Cost: ", openai_helper.cost(response.usage.total_tokens))

    command = response.choices[0].text
    try:
        command = re.findall(r"```(.*)```", command)[0]
    except IndexError:
        print("No command found: ", command)
        return

    print(command)

    # copy to clipboard
    import pyperclip
    pyperclip.copy(command)


@click.command('clie', help="Generates cli commands")
@click.argument('query', nargs=-1, required=True)
def clie_completion(query):
    query = " ".join(query)
    console_helper.console.log("Model: ", openai_helper.config.model)
    prompt = prompt_helper.unix_prompt_enhanced
    console_helper.console.log("Detected Unix")

    prompt = prompt + query + "\nA -"
    response = openai_helper.complete(prompt)

    console_helper.console.log("Tokens: ", response.usage.total_tokens)
    console_helper.console.log("Cost: ", openai_helper.cost(response.usage.total_tokens))

    command = response.choices[0].text
    try:
        command = re.findall(r"```(.*)```", command)[0]
    except IndexError:
        print("No command found: ", command)
        return

    for choice in response.choices:
        if choice.text:
            console_helper.console.print(Markdown('AI: ' + choice.text))

    # copy to clipboard
    import pyperclip
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
            print(choice.message.content)
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


@click.command('chat', help="Chat with GPT-3")
def chat():
    openai_helper.config.model = 'gpt-3.5-turbo'
    console_helper.console.log("Model: ", openai_helper.config.model)

    messages = [
        {'role': 'system', 'content': 'You are a helpful AI assistant. Respond always with Markdown.'},
        # {'role': 'user', 'content': 'I am good, how about you?'},
    ]

    cost = 0
    token = 0
    status = Status('Thinking...')

    try:
        while True:
            input_text = console_helper.get_multiline_input("You")
            messages.append({'role': 'user', 'content': input_text})

            status.start()
            response = openai_helper.chat_completion(messages)
            cost += openai_helper.cost(response.usage.total_tokens)
            token += response.usage.total_tokens
            status.stop()

            console_helper.console.print(Markdown('---'))

            for choice in response.choices:
                if choice.message.content:
                    console_helper.console.print(Markdown('AI: ' + choice.message.content))
                    messages.append({'role': 'system', 'content': choice.message.content})

            console_helper.console.log("Tokens: ", token)
            console_helper.console.log("Cost: ", cost)
    except KeyboardInterrupt:
        pass


cli.add_command(select_model)
cli.add_command(cli_completion)
cli.add_command(clie_completion)
cli.add_command(gr_completion)
cli.add_command(assessment_completion)
cli.add_command(chat)

if __name__ == '__main__':
    cli()