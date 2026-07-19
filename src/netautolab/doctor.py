import platform
import shutil
import sys

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def run() -> int:
    checks = [
        ("Operating System", f"{platform.system()} {platform.release()}", True),
        ("Python", platform.python_version(), True),
        (
            "Virtual Environment",
            "Active" if sys.prefix != sys.base_prefix else "Inactive",
            sys.prefix != sys.base_prefix,
        ),
        (
            "Git",
            "Installed" if command_exists("git") else "Missing",
            command_exists("git"),
        ),
        (
            "SSH",
            "Installed" if command_exists("ssh") else "Missing",
            command_exists("ssh"),
        ),
        (
            "Docker",
            "Installed" if command_exists("docker") else "Missing",
            command_exists("docker"),
        ),
        (
            "Ansible",
            "Installed" if command_exists("ansible") else "Missing",
            command_exists("ansible"),
        ),
    ]

    table = Table(title="NetAutoLab Doctor")

    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")

    passed = 0

    for component, details, ok in checks:
        if ok:
            status = "[green]✔[/green]"
            passed += 1
        else:
            status = "[red]✘[/red]"

        table.add_row(component, status, details)

    console.print(table)

    console.print(
        f"\n[bold cyan]Overall Health:[/bold cyan] {passed}/{len(checks)} checks passed"
    )

    return 0 if passed == len(checks) else 1
