from pathlib import Path
from datetime import datetime
import json


BACKUP_ROOT = Path("backups")


def create_backup_structure():
    """
    Create a timestamped backup directory structure.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    backup_dir = BACKUP_ROOT / timestamp

    configs_dir = backup_dir / "configs"
    facts_dir = backup_dir / "facts"
    logs_dir = backup_dir / "logs"

    configs_dir.mkdir(parents=True, exist_ok=True)
    facts_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    manifest = {
        "backup_time": timestamp,
        "version": "0.2.0",
        "status": "Initialized",
        "devices": 0,
    }

    with open(
        backup_dir / "manifest.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(manifest, file, indent=4)

    return backup_dir
