
from pathlib import Path

from ..models import Device
from ..ssh import connect_device
from .base import Provider


class ArubaProvider(Provider):
    """Provider for ArubaOS-CX devices."""

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
        """Restore an Aruba CX configuration from a backup file."""

        source_path = Path(source)

        if not source_path.exists():
            raise FileNotFoundError(
                f"Restore configuration not found: {source_path}"
            )

        if not source_path.is_file():
            raise ValueError(
                f"Restore configuration is not a file: {source_path}"
            )

        configuration = source_path.read_text(
            encoding="utf-8",
        )

        if not configuration.strip():
            raise ValueError(
                f"Restore configuration is empty: {source_path}"
            )

        commands = []

        for line in configuration.splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("!"):
                continue

            if line == "Current configuration:":
                continue

            commands.append(line)

        if not commands:
            raise ValueError(
                f"No usable configuration commands found: {source_path}"
            )

        connection = None

        try:
            connection = connect_device(device)

            output = connection.send_config_set(
                commands,
                read_timeout=60,
            )

            save_output = connection.send_command(
                "write memory",
                read_timeout=60,
            )

            return {
                "device": device.name,
                "source": str(source_path),
                "commands": len(commands),
                "output": output,
                "save_output": save_output,
            }

        finally:
            if connection is not None:
                connection.disconnect()


    def collect_facts(self, device: Device):
        """Collect basic facts from an Aruba CX device."""

        connection = None

        try:
            connection = connect_device(device)

            version = connection.send_command(
                "show version",
                read_timeout=60,
            )

            hostname = connection.send_command(
                "show hostname",
                read_timeout=60,
            )

            return {
                "device": device.name,
                "platform": device.platform,
                "host": device.host,
                "hostname": hostname.strip(),
                "version": version,
            }

        finally:
            if connection is not None:
                connection.disconnect()
