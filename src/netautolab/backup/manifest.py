import json
from pathlib import Path


def write_manifest(
    backup_dir: Path,
    backup_time: str,
    results: list[dict],
) -> Path:
    """Write the final manifest for a backup snapshot."""

    successful = sum(
        1 for result in results
        if result.get("status") == "success"
    )

    failed = len(results) - successful

    manifest = {
        "backup_time": backup_time,
        "version": "0.2.0",
        "status": "Completed" if failed == 0 else "CompletedWithErrors",
        "devices": len(results),
        "successful": successful,
        "failed": failed,
        "results": results,
    }

    manifest_file = backup_dir / "manifest.json"

    manifest_file.write_text(
        json.dumps(manifest, indent=4),
        encoding="utf-8",
    )

    manifest_file.chmod(0o600)

    return manifest_file
