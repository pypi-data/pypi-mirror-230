from __future__ import annotations

from typing import Any

import os
import tempfile
from dataclasses import dataclass
from http.cookiejar import LoadError, MozillaCookieJar
from pathlib import Path

import requests
from cached_property import cached_property_with_ttl
from requests_kerberos import OPTIONAL, REQUIRED, HTTPKerberosAuth

from amzn_micro_coral.auth import CoralAuth
from amzn_micro_coral.util.http_sentry_auth import HTTPSentryAuth


class ExpiredMidwayCookieException(Exception):
    def __init__(self):
        super().__init__("Your Midway cookie is expired. Run `mwinit`.")


# https://stackoverflow.com/a/53384267
def load_cookie() -> MozillaCookieJar:
    """Loads Midway cookie. Have to use this approach due to Python bug."""
    # TODO: Add interactive stage where we run mwinit -o if the token
    #       is not current
    tmpcookiefile = tempfile.NamedTemporaryFile(mode="w", delete=False)
    tmpcookiefile.write("# HTTP Cookie File")
    with open(Path("~/.midway/cookie").expanduser()) as f:
        for line in f:
            if line.startswith("#HttpOnly_"):
                line = line[len("#HttpOnly_") :]
            tmpcookiefile.write(line)
    tmpcookiefile.flush()
    tmpcookiefile.close()
    cookiejar = MozillaCookieJar(tmpcookiefile.name)
    try:
        cookiejar.load()
    except LoadError:
        raise RuntimeError("Could not load Midway file! Have you run mwinit?")
    has_valid_cookie = False
    for cookie in cookiejar:
        if (
            cookie.domain == "midway-auth.amazon.com"
            and cookie.name == "session"
            and cookie.path == "/"
        ):
            has_valid_cookie = True
    if not has_valid_cookie:
        raise ExpiredMidwayCookieException()
    os.remove(tmpcookiefile.name)
    return cookiejar


KERB_AUTH = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
SENTRY_AUTH = HTTPSentryAuth()


def request_kwargs(sentry: bool = False) -> dict:
    return {
        "cookies": load_cookie(),
        "auth": SENTRY_AUTH if sentry else KERB_AUTH,
    }


@dataclass(frozen=True)
class Midway(CoralAuth):
    sentry: bool = False

    def gen_kwargs(self) -> dict[str, Any]:
        return request_kwargs(sentry=self.sentry)
