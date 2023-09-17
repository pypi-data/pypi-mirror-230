import platform
from functools import lru_cache


@lru_cache(maxsize=1)
def get_runtime_environment() -> dict:
    """Get information about the langchaincoexpert runtime environment."""
    # Lazy import to avoid circular imports
    from langchaincoexpert import __version__

    return {
        "library_version": __version__,
        "library": "langchaincoexpert",
        "platform": platform.platform(),
        "runtime": "python",
        "runtime_version": platform.python_version(),
    }
