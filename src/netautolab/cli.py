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
from .backup import (
    SnapshotError,
    backup_devices,
    create_backup_structure,
    list_snapshots,
    load_snapshot,
)


app = typer.Typer(
    help="Professional Network Automation Learning Platform",
    add_completion=False,
)

ssh_app = typer.Typer(
    help="SSH Operations"
)

backup_app = typer.Typer(
    help="Backup Operations"
)


app.add_typer(
    ssh_app,
    name="ssh",
)

app.add_typer(
    backup_app,
    name="backup",
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

    devices = get_all_hosts()

    for device in devices:
        success, message = test_connection(
            host=device.host,
            platform=device.platform,
            username=device.username,
            password=device.password,
        )

        status = "✅ Connected" if success else f"❌ {message}"

        table.add_row(
            device.name,
            device.host,
            status,
        )

    console.print(table)

register_version(app)

@backup_app.command("all")
def backup_all():
    """Backup configuration from all devices."""

    backup_dir = create_backup_structure()
    devices = get_all_hosts()

    results = backup_devices(
        devices=devices,
        backup_dir=backup_dir,
    )

    table = Table(title="Backup Results")
    table.add_column("Device")
    table.add_column("Status")
    table.add_column("Details")

    for result in results:
        status = result["status"]

        if status == "success":
            table.add_row(
                result["device"],
                "✅ Success",
                "Configuration backed up",
            )
        else:
            table.add_row(
                result["device"],
                "❌ Failed",
                result.get("error", "Unknown error"),
            )

    console.print(table)
    console.print(f"Location: {backup_dir}")




@backup_app.command("list")
def backup_list():
    """List available backup snapshots."""

    snapshots = list_snapshots()

    if not snapshots:
        console.print("[yellow]No backup snapshots found.[/yellow]")
        return

    table = Table(title="Backup Snapshots")

    table.add_column("Snapshot")
    table.add_column("Status")
    table.add_column("Devices")
    table.add_column("Successful")
    table.add_column("Failed")

    for snapshot in snapshots:
        manifest = snapshot["manifest"]

        table.add_row(
            snapshot["name"],
            manifest.get("status", "-"),
            str(manifest.get("devices", 0)),
            str(manifest.get("successful", 0)),
            str(manifest.get("failed", 0)),
        )

    console.print(table)


if __name__ == "__main__":
    app()

    console.print(table)


if __name__ == "__main__":
    app()

@backup_app.command("show")
def backup_show(snapshot: str):
    """Show details of a backup snapshot."""

    try:
        snapshot_data = load_snapshot(snapshot)
    except SnapshotError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)

    manifest = snapshot_data["manifest"]

    console.print(f"\n[bold]Snapshot:[/bold] {snapshot}")
    console.print(
        f"[bold]Status:[/bold] {manifest.get('status', '-')}"
    )
    console.print(
        f"[bold]Backup Time:[/bold] "
        f"{manifest.get('backup_time', '-')}"
    )
    console.print(
        f"[bold]Devices:[/bold] {manifest.get('devices', 0)}"
    )
    console.print(
        f"[bold]Successful:[/bold] "
        f"{manifest.get('successful', 0)}"
    )
    console.print(
        f"[bold]Failed:[/bold] {manifest.get('failed', 0)}"
    )

    results = manifest.get("results", [])

    table = Table(title="Device Backups")

    table.add_column("Device")
    table.add_column("Platform")
    table.add_column("Status")
    table.add_column("Configuration")
    table.add_column("Error")

    for result in results:
        table.add_row(
            result.get("device", "-"),
            result.get("platform", "-"),
            (
                "✅ Success"
                if result.get("status") == "success"
                else "❌ Failed"
            ),
            result.get("config", "-"),
            result.get("error", "-"),
        )

    console.print(table)

    
if __name__ == "__main__":
    app()
