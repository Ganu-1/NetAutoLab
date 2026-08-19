from pathlib import Path

from ..inventory import get_all_hosts
from ..ssh import connect_device
from .storage import SnapshotError, load_snapshot


class RestoreValidationError(Exception):
    """Raised when restore validation fails."""


def validate_restore(
    snapshot_name: str,
    device_name: str,
) -> dict:
    """
    Validate a restore operation without modifying the target device.

    Returns a validation report containing:
        - snapshot information
        - target device information
        - configuration file
        - validation checks
    """

    # ---------------------------------------------------------
    # 1. Load snapshot
    # ---------------------------------------------------------

    try:
        snapshot = load_snapshot(snapshot_name)
    except SnapshotError as exc:
        raise RestoreValidationError(str(exc)) from exc

    manifest = snapshot["manifest"]
    snapshot_path = Path(snapshot["path"])

    # ---------------------------------------------------------
    # 2. Find device in snapshot
    # ---------------------------------------------------------

    snapshot_result = None

    for result in manifest.get("results", []):
        if result.get("device") == device_name:
            snapshot_result = result
            break

    if snapshot_result is None:
        raise RestoreValidationError(
            f"Device '{device_name}' is not present in snapshot "
            f"'{snapshot_name}'."
        )

    # ---------------------------------------------------------
    # 3. Verify backup was successful
    # ---------------------------------------------------------

    if snapshot_result.get("status") != "success":
        error = snapshot_result.get(
            "error",
            "Backup was not successful.",
        )

        raise RestoreValidationError(
            f"Snapshot configuration for '{device_name}' "
            f"is not restorable: {error}"
        )

    # ---------------------------------------------------------
    # 4. Verify configuration path
    # ---------------------------------------------------------

    config_relative = snapshot_result.get("config")

    if not config_relative:
        raise RestoreValidationError(
            f"No configuration file recorded for '{device_name}'."
        )

    config_file = snapshot_path / config_relative

    if not config_file.exists():
        raise RestoreValidationError(
            f"Configuration file does not exist: {config_file}"
        )

    if not config_file.is_file():
        raise RestoreValidationError(
            f"Configuration path is not a file: {config_file}"
        )

    # ---------------------------------------------------------
    # 5. Verify configuration is not empty
    # ---------------------------------------------------------

    if config_file.stat().st_size == 0:
        raise RestoreValidationError(
            f"Configuration file is empty: {config_file}"
        )

    # ---------------------------------------------------------
    # 6. Find current device in inventory
    # ---------------------------------------------------------

    devices = get_all_hosts()

    target_device = next(
        (
            device
            for device in devices
            if device.name == device_name
        ),
        None,
    )

    if target_device is None:
        raise RestoreValidationError(
            f"Device '{device_name}' is not present in the current inventory."
        )

    # ---------------------------------------------------------
    # 7. Verify platform matches
    # ---------------------------------------------------------

    snapshot_platform = snapshot_result.get("platform")

    if snapshot_platform != target_device.platform:
        raise RestoreValidationError(
            f"Platform mismatch for '{device_name}': "
            f"snapshot={snapshot_platform}, "
            f"inventory={target_device.platform}"
        )

    # ---------------------------------------------------------
    # 8. Verify SSH connectivity
    # ---------------------------------------------------------

    connection = None

    try:
        connection = connect_device(target_device)
    except Exception as exc:
        raise RestoreValidationError(
            f"Unable to connect to '{device_name}': {exc}"
        ) from exc
    finally:
        if connection is not None:
            connection.disconnect()

    # ---------------------------------------------------------
    # 9. Return validation report
    # ---------------------------------------------------------

    return {
        "valid": True,
        "snapshot": snapshot_name,
        "device": device_name,
        "platform": target_device.platform,
        "host": target_device.host,
        "config": str(config_file),
        "config_size": config_file.stat().st_size,
        "message": "Restore validation successful.",
    }


def preview_restore(
    snapshot_name: str,
    device_name: str,
) -> dict:
    """
    Preview a restore operation without modifying the device.

    Returns the validated restore information and configuration
    that would be applied to the target device.
    """

    validation = validate_restore(
        snapshot_name=snapshot_name,
        device_name=device_name,
    )

    config_file = Path(validation["config"])

    try:
        configuration = config_file.read_text(
            encoding="utf-8"
        )
    except OSError as exc:
        raise RestoreValidationError(
            f"Unable to read configuration file: {config_file}"
        ) from exc

    if not configuration.strip():
        raise RestoreValidationError(
            f"Configuration file is empty: {config_file}"
        )

    return {
        **validation,
        "configuration": configuration,
    }
