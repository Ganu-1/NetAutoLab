import platform
import subprocess


def ping(host: str) -> bool:
    """Return True if a host responds to ICMP ping."""

    count_flag = "-n" if platform.system().lower() == "windows" else "-c"

    result = subprocess.run(
        ["ping", count_flag, "1", host],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0
