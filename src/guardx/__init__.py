import importlib.metadata

from guardx.guardx import Guardx

# Package version
try:
    __version__ = importlib.metadata.version("guardx")
except Exception:
    __version__ = None

__all__ = ["Guardx", "__version__"]
