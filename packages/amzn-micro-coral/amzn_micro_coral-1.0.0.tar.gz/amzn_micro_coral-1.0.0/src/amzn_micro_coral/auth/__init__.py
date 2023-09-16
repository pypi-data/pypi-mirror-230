from .base import CoralAuth
from .dummy import Dummy
from .midway import Midway
from .sigv4 import SigV4


__all__ = [
    "CoralAuth",
    "Midway",
    "SigV4",
]

# lol
CoralAuth.dummy = lambda *args, **kwargs: Dummy(*args, **kwargs)
CoralAuth.midway = lambda *args, **kwargs: Midway(*args, **kwargs)
CoralAuth.sigv4 = lambda *args, **kwargs: SigV4(*args, **kwargs)
