from pathlib import Path

from ..models import Device
from ..ssh import connect_device
from .base import Provider


class ArubaProvider(Provider):
    """Provider for Aruba devices."""

    def backup(self, device: Device, destination: str):
        """Backup the running configuration of an Aruba CX device."""

        destination_path = Path(destination)
        destination_path.mkdir(parents=True, exist_ok=True)

        backup_file = destination_path / f"{device.name}.cfg"

        connection = None

        try:
            connection = connect_device(device)

            configuration = connection.send_command(
                "show running-config",
                read_timeout=60,
            )

            backup_file.write_text(
                configuration,
                encoding="utf-8",
            )

            backup_file.chmod(0o600)

            return backup_file

        finally:
            if connection is not None:
                connection.disconnect()

    def restore(self, device: Device, source: str):
        raise NotImplementedError

    def collect_facts(self, device: Device):
        raise NotImplementedError
