from dataclasses import dataclass


@dataclass(slots=True)
class Device:
    """Represents a network device."""

    name: str
    host: str
    platform: str
    username: str
    password: str

