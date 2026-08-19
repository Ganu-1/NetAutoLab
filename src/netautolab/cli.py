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

from .backup.restore import (
    RestoreValidationError,
    preview_restore,
    validate_restore,
)

from .providers import get_provider


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

restore_app = typer.Typer(
    help="Restore Operations"
)

app.add_typer(
    ssh_app,
    name="ssh",
)

app.add_typer(
    backup_app,
    name="backup",
)

app.add_typer(
    restore_app,
    name="restore",
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

@backup_app.command("diff")
def backup_diff(snapshot: str, device: str):
    """Compare a snapshot configuration with the current device configuration."""

    from .backup.diff import diff_snapshot

    try:
        result = diff_snapshot(
            snapshot_name=snapshot,
            device_name=device,
        )

    except Exception as exc:
        console.print(
            f"[red]❌ Configuration diff failed:[/red] {exc}"
        )
        raise typer.Exit(code=1)

    table = Table(title="Configuration Diff")

    table.add_column("Item")
    table.add_column("Value")

    table.add_row("Snapshot", result["snapshot"])
    table.add_row("Device", result["device"])
    table.add_row("Added", str(result["added"]))
    table.add_row("Removed", str(result["removed"]))

    if result["changed"]:
        table.add_row("Status", "⚠️ CHANGED")
    else:
        table.add_row("Status", "✅ IDENTICAL")

    console.print(table)

    if result["changed"]:
        console.print("\n[bold]Changes:[/bold]")

        added_lines = [
            line
            for line in result["diff"]
            if line.startswith("+") and not line.startswith("+++")
        ]

        removed_lines = [
            line
            for line in result["diff"]
            if line.startswith("-") and not line.startswith("---")
        ]

        console.print(
            "\n[bold]Added to current configuration:[/bold]"
        )

        if added_lines:
            for line in added_lines:
                console.print(f"[green]{line}[/green]")
        else:
            console.print("[dim]None[/dim]")

        console.print(
            "\n[bold]Removed from current configuration:[/bold]"
        )

        if removed_lines:
            for line in removed_lines:
                console.print(f"[red]{line}[/red]")
        else:
            console.print("[dim]None[/dim]")

    else:
        console.print(
            "\n[green]"
            "Snapshot and current configuration are identical."
            "[/green]"
        )

@restore_app.command("validate")
def restore_validate(snapshot: str, device: str):
    """Validate a restore operation without modifying the device."""

    try:
        result = validate_restore(
            snapshot_name=snapshot,
            device_name=device,
        )

    except RestoreValidationError as exc:
        console.print(f"[red]❌ Restore validation failed:[/red] {exc}")
        raise typer.Exit(code=1)

    table = Table(title="Restore Validation")

    table.add_column("Check")
    table.add_column("Result")

    table.add_row(
        "Snapshot",
        result["snapshot"],
    )

    table.add_row(
        "Device",
        result["device"],
    )

    table.add_row(
        "Platform",
        result["platform"],
    )

    table.add_row(
        "Host",
        result["host"],
    )

    table.add_row(
        "Configuration",
        result["config"],
    )

    table.add_row(
        "Configuration Size",
        f'{result["config_size"]} bytes',
    )

    table.add_row(
        "Validation",
        "✅ PASS",
    )

    console.print(table)
    console.print(
        "[green]Restore validation successful. "
        "No device configuration was changed.[/green]"
    )

@restore_app.command("preview")
def restore_preview(snapshot: str, device: str):
    """Preview a restore without modifying the device."""

    try:
        result = preview_restore(
            snapshot_name=snapshot,
            device_name=device,
        )

    except RestoreValidationError as exc:
        console.print(
            f"[red]❌ Restore preview failed:[/red] {exc}"
        )
        raise typer.Exit(code=1)

    table = Table(title="Restore Preview")

    table.add_column("Item")
    table.add_column("Value")

    table.add_row(
        "Snapshot",
        result["snapshot"],
    )

    table.add_row(
        "Device",
        result["device"],
    )

    table.add_row(
        "Platform",
        result["platform"],
    )

    table.add_row(
        "Host",
        result["host"],
    )

    table.add_row(
        "Configuration",
        result["config"],
    )

    table.add_row(
        "Configuration Size",
        f'{result["config_size"]} bytes',
    )

    console.print(table)

    console.print(
        "\n[yellow]⚠️ PREVIEW ONLY[/yellow]"
    )

    console.print(
        "[yellow]"
        "No configuration changes will be made to the device."
        "[/yellow]"
    )

    console.print("\n[bold]Configuration:[/bold]")
    console.print(result["configuration"])


@restore_app.command("apply")
def restore_apply(
    snapshot: str,
    device: str,
    yes: bool = typer.Option(
        False,
        "--yes",
        help="Confirm and apply the restore.",
    ),
):
    """Apply a snapshot configuration to a device."""

    # ---------------------------------------------------------
    # 1. Validate restore
    # ---------------------------------------------------------

    try:
        validation = validate_restore(
            snapshot_name=snapshot,
            device_name=device,
        )

    except RestoreValidationError as exc:
        console.print(
            f"[red]❌ Restore validation failed:[/red] {exc}"
        )
        raise typer.Exit(code=1)

    # ---------------------------------------------------------
    # 2. Show restore information
    # ---------------------------------------------------------

    table = Table(title="Restore Apply")

    table.add_column("Item")
    table.add_column("Value")

    table.add_row(
        "Snapshot",
        validation["snapshot"],
    )

    table.add_row(
        "Device",
        validation["device"],
    )

    table.add_row(
        "Platform",
        validation["platform"],
    )

    table.add_row(
        "Host",
        validation["host"],
    )

    table.add_row(
        "Configuration",
        validation["config"],
    )

    table.add_row(
        "Configuration Size",
        f'{validation["config_size"]} bytes',
    )

    console.print(table)

    # ---------------------------------------------------------
    # 3. Require explicit confirmation
    # ---------------------------------------------------------

    if not yes:
        console.print(
            "\n[yellow]⚠️ RESTORE NOT APPLIED[/yellow]"
        )

        console.print(
            "[yellow]"
            "This operation will modify the device."
            "[/yellow]"
        )

        console.print(
            "\nRun the command again with [bold]--yes[/bold] "
            "to apply the configuration."
        )

        raise typer.Exit(code=0)

    # ---------------------------------------------------------
    # 4. Create pre-restore backup
    # ---------------------------------------------------------

    console.print(
        "\n[cyan]Creating pre-restore backup...[/cyan]"
    )

    try:
        backup_dir = create_backup_structure()

        devices = get_all_hosts()

        target_device = next(
            (
                current_device
                for current_device in devices
                if current_device.name == device
            ),
            None,
        )

        if target_device is None:
            raise RestoreValidationError(
                f"Device '{device}' is not present in inventory."
            )

        backup_results = backup_devices(
            [target_device],
            backup_dir,
        )

        backup_result = backup_results[0]

        if backup_result.get("status") != "success":
            raise RestoreValidationError(
                "Pre-restore backup failed: "
                + backup_result.get(
                    "error",
                    "Unknown backup error.",
                )
            )

        console.print(
            f"[green]✅ Pre-restore backup created:[/green] "
            f"{backup_dir}"
        )

    except Exception as exc:
        console.print(
            f"[red]❌ Pre-restore backup failed:[/red] {exc}"
        )

        console.print(
            "[red]Restore aborted. No configuration was changed.[/red]"
        )

        raise typer.Exit(code=1)

    # ---------------------------------------------------------
    # 5. Apply configuration
    # ---------------------------------------------------------

    console.print(
        "\n[yellow]⚠️ Applying configuration to device...[/yellow]"
    )

    try:
        provider = get_provider(validation["platform"])

        result = provider.restore(
            target_device,
            validation["config"],
        )

    except Exception as exc:
        console.print(
            f"[red]❌ Restore failed:[/red] {exc}"
        )
        raise typer.Exit(code=1)

    # ---------------------------------------------------------
    # 6. Report result
    # ---------------------------------------------------------

    result_table = Table(title="Restore Result")

    result_table.add_column("Item")
    result_table.add_column("Value")

    result_table.add_row(
        "Device",
        result["device"],
    )

    result_table.add_row(
        "Commands Applied",
        str(result["commands"]),
    )

    result_table.add_row(
        "Pre-Restore Backup",
        str(backup_dir),
    )

    result_table.add_row(
        "Status",
        "✅ SUCCESS",
    )

    console.print(result_table)

    console.print(
        "\n[green]Restore completed successfully.[/green]"
    )


if __name__ == "__main__":
    app()
