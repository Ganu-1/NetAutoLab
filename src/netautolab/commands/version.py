from rich import print

from ..version import __version__


def register(app):
    @app.command()
    def version():
        """Show NetAutoLab version."""
        print(f"NetAutoLab {__version__}")
