import json
from pathlib import Path


BACKUP_ROOT = Path("backups")


class SnapshotError(Exception):
    """Raised when a backup snapshot cannot be loaded."""


def list_snapshots() -> list[dict]:
    """
    Return available backup snapshots.

    Snapshots are identified by directories containing manifest.json.
    """

    if not BACKUP_ROOT.exists():
        return []

    snapshots = []

    for snapshot_dir in sorted(
        BACKUP_ROOT.iterdir(),
        reverse=True,
    ):
        if not snapshot_dir.is_dir():
            continue

        manifest_file = snapshot_dir / "manifest.json"

        if not manifest_file.exists():
            continue

        try:
            manifest = json.loads(
                manifest_file.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError):
            continue

        snapshots.append(
            {
                "name": snapshot_dir.name,
                "path": snapshot_dir,
                "manifest": manifest,
            }
        )

    return snapshots


def load_snapshot(snapshot_name: str) -> dict:
    """
    Load a specific backup snapshot.
    """

    snapshot_dir = BACKUP_ROOT / snapshot_name

    if not snapshot_dir.exists():
        raise SnapshotError(
            f"Snapshot not found: {snapshot_name}"
        )

    if not snapshot_dir.is_dir():
        raise SnapshotError(
            f"Snapshot path is not a directory: {snapshot_name}"
        )

    manifest_file = snapshot_dir / "manifest.json"

    if not manifest_file.exists():
        raise SnapshotError(
            f"Manifest not found in snapshot: {snapshot_name}"
        )

    try:
        manifest = json.loads(
            manifest_file.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise SnapshotError(
            f"Invalid manifest: {snapshot_name}"
        ) from exc

    return {
        "name": snapshot_name,
        "path": snapshot_dir,
        "manifest": manifest,
    }
