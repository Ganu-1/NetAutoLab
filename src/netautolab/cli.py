import typer
from rich import print

from .version import __version__

app = typer.Typer(
    help="Professional Network Automation Learning Platform",
    add_completion=False,
)


@app.command()
def version():
    """Show NetAutoLab version."""
    print(f"NetAutoLab {__version__}")


@app.command()
def doctor():
    """Run environment diagnostics."""
    print("[green]Doctor engine coming soon![/green]")


if __name__ == "__main__":
    app()
