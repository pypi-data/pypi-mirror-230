"""Metadata information about the package."""
import importlib.metadata


def version():
    """Get the version of the SDK from the metadata."""
    return importlib.metadata.version(
        "validio-sdk"
    )  # This needs to match the distribution package name
