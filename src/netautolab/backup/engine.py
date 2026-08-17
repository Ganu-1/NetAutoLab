from pathlib import Path
from datetime import datetime
import json

from ..models import Device
from ..providers import get_provider
from .manifest import write_manifest


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


def backup_devices(
    devices: list[Device],
    backup_dir: Path,
) -> list[dict]:
    """
    Run configuration backup for all devices using their providers.
    """

    results = []

    for device in devices:
        try:
            provider = get_provider(device.platform)

            backup_file = provider.backup(
                device=device,
                destination=str(backup_dir / "configs"),
            )

            results.append(
                {
                    "device": device.name,
                    "platform": device.platform,
                    "status": "success",
                    "config": str(
                        Path(backup_file).relative_to(backup_dir)
                    ),
                }
            )

        except Exception as exc:
            results.append(
                {
                    "device": device.name,
                    "platform": device.platform,
                    "status": "failed",
                    "error": str(exc) or type(exc).__name__,
                }
            )

    write_manifest(
        backup_dir=backup_dir,
        backup_time=backup_dir.name,
        results=results,
    )

    return results
