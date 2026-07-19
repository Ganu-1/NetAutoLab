from pathlib import Path

import yaml

CONFIG_FILE = Path("config/default.yaml")


class ConfigError(Exception):
    """Raised when the configuration cannot be loaded."""


def load_config() -> dict:
    """Load the NetAutoLab configuration."""

    if not CONFIG_FILE.exists():
        raise ConfigError(f"Configuration file not found: {CONFIG_FILE}")

    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
