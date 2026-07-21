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


def get_all_hosts() -> list[dict]:
    """
    Return all hosts from the inventory in a normalized format.
    """

    inventory = load_inventory()
    hosts = []

    groups = inventory.get("groups", {})

    for group_name, group_data in groups.items():

        platform = group_data.get("platform", "")
        username = group_data.get("username", "")
        password = group_data.get("password", "")

        for host_name, host_data in group_data.get("hosts", {}).items():

            hosts.append(
                {
                    "group": group_name,
                    "name": host_name,
                    "host": host_data.get("host", ""),
                    "platform": platform,
                    "username": username,
                    "password": password,
                }
            )

    return hosts
