from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from amzn_micro_coral.auth import CoralAuth


class CoralException(Exception):
    def __init__(self, coral_error: str, coral_message: str | None):
        super().__init__(f"{coral_error}: {coral_message or 'No message.'}")
        self.coral_error = coral_error
        self.coral_message = coral_message


@dataclass(frozen=True)
class CoralService:
    url: str
    auth: CoralAuth

    def post(self, operation: str, data: dict = {}, **kwargs) -> requests.Response:
        kwargs = dict(kwargs)
        kwargs["headers"] = kwargs.get("headers", {})
        kwargs["headers"]["X-Amz-Target"] = operation
        kwargs["headers"]["Content-Encoding"] = "amz-1.0"
        kwargs["headers"]["Content-Type"] = "application/json; charset=UTF-8"

        auth = self.auth.gen_kwargs()
        r = requests.post(url=self.url, data=json.dumps(data), **auth, **kwargs)
        try:
            result = r.json()
        except requests.exceptions.JSONDecodeError:
            raise RuntimeError(f"Encountered error when making request: {r.text}")
        if "__type" in result:
            raise CoralException(result["__type"], result.get("message"))
        return r
