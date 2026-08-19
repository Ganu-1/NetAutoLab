from difflib import unified_diff


def configuration_diff(
    snapshot_config: str,
    current_config: str,
) -> dict:
    """
    Compare a snapshot configuration with the current device configuration.

    The comparison is read-only and does not modify the device.

    Returns:
        A dictionary containing the unified diff and summary counts.
    """

    snapshot_lines = snapshot_config.splitlines()
    current_lines = current_config.splitlines()

    diff_lines = list(
        unified_diff(
            snapshot_lines,
            current_lines,
            fromfile="snapshot",
            tofile="current",
            lineterm="",
        )
    )

    added = 0
    removed = 0

    for line in diff_lines:
        if line.startswith("+++") or line.startswith("---"):
            continue

        if line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            removed += 1

    return {
        "changed": bool(diff_lines),
        "added": added,
        "removed": removed,
        "diff": diff_lines,
    }


from pathlib import Path

from ..inventory import get_all_hosts
from ..providers import get_provider
from .storage import SnapshotError, load_snapshot


class ConfigurationDiffError(Exception):
    """Raised when configuration diff cannot be performed."""


def diff_snapshot(
    snapshot_name: str,
    device_name: str,
) -> dict:
    """
    Compare a snapshot configuration with the current device configuration.

    This operation is read-only and does not modify the device.
    """

    # ---------------------------------------------------------
    # 1. Load snapshot
    # ---------------------------------------------------------

    try:
        snapshot = load_snapshot(snapshot_name)
    except SnapshotError as exc:
        raise ConfigurationDiffError(str(exc)) from exc

    manifest = snapshot["manifest"]
    snapshot_path = Path(snapshot["path"])

    # ---------------------------------------------------------
    # 2. Find device in snapshot
    # ---------------------------------------------------------

    snapshot_result = next(
        (
            result
            for result in manifest.get("results", [])
            if result.get("device") == device_name
        ),
        None,
    )

    if snapshot_result is None:
        raise ConfigurationDiffError(
            f"Device '{device_name}' is not present in snapshot "
            f"'{snapshot_name}'."
        )

    # ---------------------------------------------------------
    # 3. Verify snapshot backup
    # ---------------------------------------------------------

    if snapshot_result.get("status") != "success":
        error = snapshot_result.get(
            "error",
            "Backup was not successful.",
        )

        raise ConfigurationDiffError(
            f"Snapshot configuration for '{device_name}' "
            f"is not available: {error}"
        )

    # ---------------------------------------------------------
    # 4. Locate snapshot configuration
    # ---------------------------------------------------------

    config_relative = snapshot_result.get("config")

    if not config_relative:
        raise ConfigurationDiffError(
            f"No configuration file recorded for '{device_name}'."
        )

    snapshot_config_file = snapshot_path / config_relative

    if not snapshot_config_file.exists():
        raise ConfigurationDiffError(
            f"Configuration file does not exist: "
            f"{snapshot_config_file}"
        )

    try:
        snapshot_config = snapshot_config_file.read_text(
            encoding="utf-8"
        )
    except OSError as exc:
        raise ConfigurationDiffError(
            f"Unable to read snapshot configuration: "
            f"{snapshot_config_file}"
        ) from exc

    if not snapshot_config.strip():
        raise ConfigurationDiffError(
            f"Snapshot configuration is empty: "
            f"{snapshot_config_file}"
        )

    # ---------------------------------------------------------
    # 5. Find current device
    # ---------------------------------------------------------

    devices = get_all_hosts()

    device = next(
        (
            item
            for item in devices
            if item.name == device_name
        ),
        None,
    )

    if device is None:
        raise ConfigurationDiffError(
            f"Device '{device_name}' is not present "
            f"in the current inventory."
        )

    # ---------------------------------------------------------
    # 6. Verify platform
    # ---------------------------------------------------------

    snapshot_platform = snapshot_result.get("platform")

    if snapshot_platform != device.platform:
        raise ConfigurationDiffError(
            f"Platform mismatch for '{device_name}': "
            f"snapshot={snapshot_platform}, "
            f"inventory={device.platform}"
        )

    # ---------------------------------------------------------
    # 7. Get provider
    # ---------------------------------------------------------

    try:
        provider = get_provider(device.platform)
    except ValueError as exc:
        raise ConfigurationDiffError(str(exc)) from exc

    # ---------------------------------------------------------
    # 8. Collect current configuration
    # ---------------------------------------------------------

    try:
        current_config = provider.get_running_config(device)
    except Exception as exc:
        raise ConfigurationDiffError(
            f"Unable to retrieve current configuration "
            f"from '{device_name}': {exc}"
        ) from exc

    if not current_config.strip():
        raise ConfigurationDiffError(
            f"Current configuration from '{device_name}' is empty."
        )

    # ---------------------------------------------------------
    # 9. Compare configurations
    # ---------------------------------------------------------

    result = configuration_diff(
        snapshot_config=snapshot_config,
        current_config=current_config,
    )

    return {
        "snapshot": snapshot_name,
        "device": device_name,
        "platform": device.platform,
        "host": device.host,
        "config": str(snapshot_config_file),
        "snapshot_size": len(snapshot_config.encode("utf-8")),
        "current_size": len(current_config.encode("utf-8")),
        **result,
    }
