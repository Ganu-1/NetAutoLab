from pathlib import Path

import yaml

INVENTORY_FILE = Path("inventory/lab.yml")


class InventoryError(Exception):
    """Raised when the inventory cannot be loaded."""


def load_inventory() -> dict:
    """Load the NetAutoLab inventory."""

    if not INVENTORY_FILE.exists():
        raise InventoryError(
            f"Inventory file not found: {INVENTORY_FILE}"
        )

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
