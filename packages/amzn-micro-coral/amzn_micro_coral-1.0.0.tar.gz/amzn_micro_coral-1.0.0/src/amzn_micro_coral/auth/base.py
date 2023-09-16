from __future__ import annotations

from typing import TYPE_CHECKING

from abc import ABC

if TYPE_CHECKING:
    from typing import Callable
    from typing import Any

    from .dummy import Dummy
    from .midway import Midway
    from .sigv4 import SigV4


class CoralAuth(ABC):
    dummy: Callable[..., Dummy]
    midway: Callable[..., Midway]
    sigv4: Callable[..., SigV4]

    def gen_kwargs(self) -> dict[str, Any]:
        raise NotImplementedError()
