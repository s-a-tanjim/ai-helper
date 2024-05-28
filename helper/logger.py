import logging

from rich.logging import RichHandler

from helper.console import console

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(console=console)]
)

log = logging.getLogger("rich")
