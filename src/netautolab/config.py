import typer
from rich import print
from rich.console import Console
from rich.table import Table

from .config import load_config
from .doctor import run
from .version import __version__

app = typer.Typer(
    help="Professional Network Automation Learning Platform",
    add_completion=False,
)

console = Console()

@app.command()
def config():
    """Display the current configuration."""

    cfg = load_config()

    table = Table(title="NetAutoLab Configuration")

    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Lab Name", cfg["lab"]["name"])
    table.add_row("Environment", cfg["lab"]["environment"])
    table.add_row("Inventory", cfg["inventory"]["file"])
    table.add_row("SSH User", cfg["ssh"]["username"])
    table.add_row("SSH Port", str(cfg["ssh"]["port"]))
    table.add_row("Log Level", cfg["logging"]["level"])
    table.add_row("Reports", cfg["reports"]["directory"])

    console.print(table)
