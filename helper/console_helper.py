import sys

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt

from helper import openai_helper

console = Console()


def get_multiline_input(prompt=""):
    lines = []

    while True:
        line = Prompt.ask(f"\r[b]{prompt}[/b]")
        if not line:
            sys.stdout.write("\033[F")
            break
        lines.append(line)

    return "\n".join(lines)


def chat_in_console(messages, query):
    token = 0
    response_text = ""
    try:
        while True:
            if query:
                input_text = " ".join(query)
                query = None
            else:
                input_text = get_multiline_input('You')
                if not input_text:
                    return response_text

                response_text = ""
                token = (token * 2) + len(input_text.split())

            messages.append({'role': 'user', 'content': input_text})
            response = openai_helper.chat_completion(messages, stream=True)

            with Live(refresh_per_second=6) as live:
                for chunk in response:
                    for choice in chunk.choices:

                        if choice.finish_reason == 'stop':
                            live.update(Markdown('**AI:** ' + response_text))
                            break

                        if choice.delta.content:
                            response_text += choice.delta.content
                            token += 1

                        live.update(Markdown(
                            '**AI:** ' +
                            response_text +
                            "\n\n---"
                            f"\nResponse Tokens: {token}"
                            f"\nCost: {openai_helper.cost(token)}"
                            "\n\n---"
                        ))

            messages.append({'role': 'system', 'content': response_text})
            console.print(Markdown('---'))
            console.log("Response Tokens: ", token)
            console.log("Cost: ", openai_helper.cost(token))
            console.print(Markdown('---'))

    except KeyboardInterrupt:
        pass

    return response_text
