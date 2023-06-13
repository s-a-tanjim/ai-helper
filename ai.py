import os
import re

import rich_click as click
from pick import pick
from rich_click.cli import patch

import cli_helper
import console_helper
import openai_helper

patch()


@click.group()
def cli():
    pass


@click.command('model')
def select_model():
    print("Current model:", openai_helper.config.model)
    models = openai_helper.get_models()
    option, index = pick([model.id for model in models.data], "Select a model")
    openai_helper.set_model(option)


@click.command('cli')
@click.argument('query', nargs=-1)
def cli_completion(query):
    query = " ".join(query)
    console_helper.console.log("Model: ", openai_helper.config.model)

    if os.name == "nt":
        prompt = cli_helper.powershell_prompt
        console_helper.console.log("Detected Windows")
    else:
        prompt = cli_helper.unix_prompt
        console_helper.console.log("Detected Unix")

    prompt = prompt + query + "\nA -"
    response = openai_helper.complete(prompt)

    console_helper.console.log("Tokens: ", response.usage.total_tokens)
    console_helper.console.log("Cost: ", openai_helper.cost(response.usage.total_tokens))

    command = response.choices[0].text
    command = re.findall(r"`(.*)`", command)[0]
    print(command)

    # copy to clipboard
    if os.name == "nt":
        import pyperclip
        pyperclip.copy(command)
    else:
        import subprocess
        subprocess.run("echo " + command + " | xclip -selection clipboard", shell=True)


if __name__ == '__main__':
    cli.add_command(select_model)
    cli.add_command(cli_completion)
    cli()
