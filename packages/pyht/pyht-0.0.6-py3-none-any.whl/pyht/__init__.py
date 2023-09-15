# Don't manually change, let poetry-dynamic-versioning handle it.
__version__ = "0.0.6"


from .client import Client

__all__ = ["Client"]
