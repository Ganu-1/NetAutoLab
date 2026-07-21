import typer
from rich import print
from rich.console import Console
from rich.table import Table

from .config import load_config
from .doctor import run
from .inventory import load_inventory
from .version import __version__

app = typer.Typer(
    help="Professional Network Automation Learning Platform",
    add_completion=False,
)

console = Console()


@app.command()
def version():
    """Show NetAutoLab version."""
    print(f"NetAutoLab {__version__}")


@app.command()
def doctor():
    """Run environment diagnostics."""
    raise typer.Exit(run())


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
    table.add_row("SSH Timeout", str(cfg["ssh"]["timeout"]))
    table.add_row("Log Level", cfg["logging"]["level"])
    table.add_row("Reports", cfg["reports"]["directory"])

    console.print(table)


if __name__ == "__main__":
    app()

@app.command()
def inventory():
    """Display the inventory."""

    inv = load_inventory()

    table = Table(title="Inventory Summary")
    table.add_column("Group", style="cyan")
    table.add_column("Host", style="green")
    table.add_column("Hostname", style="yellow")

    groups = inv.get("groups", {})

    for group_name, group_data in groups.items():
        hosts = group_data.get("hosts", {})

        for host_name, host_data in hosts.items():
            table.add_row(
                group_name,
                host_name,
                host_data.get("hostname", "-"),
            )

    console.print(table)
