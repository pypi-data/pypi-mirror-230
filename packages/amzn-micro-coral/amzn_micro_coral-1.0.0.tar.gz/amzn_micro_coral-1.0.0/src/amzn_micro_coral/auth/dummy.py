from __future__ import annotations

from typing import Any

from .base import CoralAuth


class Dummy(CoralAuth):
    def gen_kwargs(self) -> dict[str, Any]:
        return {}
