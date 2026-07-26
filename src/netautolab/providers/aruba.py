from .base import Provider


class ArubaProvider(Provider):
    """Provider for Aruba devices."""

    def backup(self):
        raise NotImplementedError

    def restore(self):
        raise NotImplementedError

    def collect_facts(self):
        raise NotImplementedError
