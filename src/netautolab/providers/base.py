from abc import ABC, abstractmethod

from ..models import Device


class Provider(ABC):
    """Base class for all NetAutoLab providers."""

    @abstractmethod
    def backup(self, device: Device, destination: str):
        """Backup device configuration."""
        raise NotImplementedError

    @abstractmethod
    def restore(self, device: Device, source: str):
        """Restore device configuration."""
        raise NotImplementedError

    @abstractmethod
    def collect_facts(self, device: Device):
        """Collect device facts."""
        raise NotImplementedError
