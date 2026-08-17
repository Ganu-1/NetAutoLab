from .aruba import ArubaProvider


PROVIDERS = {
    "aruba_aoscx": ArubaProvider,
}


def get_provider(platform: str):
    """Return the provider class for a platform."""

    try:
        provider_class = PROVIDERS[platform]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported platform: {platform}"
        ) from exc

    return provider_class()
