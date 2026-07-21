from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

DEVICE_TYPE_MAP = {
    "aruba_aoscx": "aruba_aoscx",
    "linux": "linux",
}


def test_connection(host, platform, username, password):
    """
    Test SSH connectivity to a device.

    Returns:
        (success: bool, message: str)
    """

    device_type = DEVICE_TYPE_MAP.get(platform)

    if device_type is None:
        return False, f"Unsupported platform: {platform}"

    try:
        connection = ConnectHandler(
            device_type=device_type,
            host=host,
            username=username,
            password=password,
        )

        connection.disconnect()
        return True, "Connected"

    except NetmikoAuthenticationException:
        return False, "Authentication Failed"

    except NetmikoTimeoutException:
        return False, "Connection Timed Out"

    except Exception as exc:
        return False, str(exc)
