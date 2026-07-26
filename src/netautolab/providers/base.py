from abc import ABC, abstractmethod


class Provider(ABC):
    """Base class for all NetAutoLab providers."""

    @abstractmethod
    def backup(self):
        """Backup device configuration."""
        raise NotImplementedError

    @abstractmethod
    def restore(self):
        """Restore device configuration."""
        raise NotImplementedError

    @abstractmethod
    def collect_facts(self):
        """Collect device facts."""
        raise NotImplementedError
