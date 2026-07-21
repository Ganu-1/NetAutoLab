import typer
from rich import print
from rich.console import Console
from rich.table import Table

from .config import load_config
from .connectivity import ping as ping_host
from .doctor import run
from .inventory import load_inventory, get_all_hosts
from .ssh import test_connection
from .version import __version__
from .commands.version import register as register_version

app = typer.Typer(
    help="Professional Network Automation Learning Platform",
    add_completion=False,
)

ssh_app = typer.Typer(
    help="SSH Operations"
)

app.add_typer(
    ssh_app,
    name="ssh",
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


@app.command()
def inventory():
    """Display the inventory."""

    inv = load_inventory()

    table = Table(title="Inventory Summary")
    table.add_column("Group", style="cyan")
    table.add_column("Host", style="green")
    table.add_column("Host", style="yellow")

    groups = inv.get("groups", {})

    for group_name, group_data in groups.items():
        hosts = group_data.get("hosts", {})

        for host_name, host_data in hosts.items():
            table.add_row(
                group_name,
                host_name,
                host_data.get("host", "-"),
            )

    console.print(table)

@app.command()
def ping():
    """Ping all devices in the inventory."""

    inv = load_inventory()

    table = Table(title="Connectivity Check")
    table.add_column("Host", style="cyan")
    table.add_column("IP", style="green")
    table.add_column("Status", style="yellow")

    groups = inv.get("groups", {})

    for group_data in groups.values():
        hosts = group_data.get("hosts", {})

        for host_name, host_data in hosts.items():
            ip = host_data.get("host", "")

            status = "✅ Reachable" if ping_host(ip) else "❌ Unreachable"

            table.add_row(host_name, ip, status)

    console.print(table)


@ssh_app.command("test")
def ssh_test():
    console = Console()

    table = Table(title="SSH Connectivity")

    table.add_column("Host")
    table.add_column("IP")
    table.add_column("Status")

    hosts = get_all_hosts()

    for host in hosts:
        success, message = test_connection(
            host=host["host"],
            platform=host["platform"],
            username=host["username"],
            password=host["password"],
        )

        status = "✅ Connected" if success else f"❌ {message}"

        table.add_row(
            host["name"],
            host["host"],
            status,
        )

    console.print(table)

register_version(app)

if __name__ == "__main__":
    app()
