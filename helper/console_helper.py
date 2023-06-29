import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

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
