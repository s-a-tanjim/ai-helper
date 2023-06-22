from rich.console import Console
from rich.prompt import Prompt

console = Console()


def get_multiline_input(prompt=""):
    lines = []

    while True:
        line = Prompt.ask(prompt)
        if not line:
            break
        lines.append(line)

    return "\n".join(lines)
