from __future__ import annotations

from typing import Any

from dataclasses import dataclass
import boto3
from requests_auth_aws_sigv4 import AWSSigV4

from amzn_micro_coral.auth.base import CoralAuth


def _aws_credentials(session: boto3.Session | None = None, region_name: str | None = None) -> dict:
    session_ = session or boto3.Session()
    credentials = session_.get_credentials().get_frozen_credentials()

    return {
        "aws_access_key_id": credentials.access_key,
        "aws_secret_access_key": credentials.secret_key,
        "aws_session_token": credentials.token,
        "region": region_name or session_.region_name,
    }


@dataclass(frozen=True)
class SigV4(CoralAuth):
    """
    SigV4 auth

    :param scheme: Usually 'aws4-hmac-sha256'
    :param service: Something to overcomplicate this whole process
    :param session: Overrides the default boto3 session
    :param region_name: Overrides the default AWS region
    """

    scheme: str
    service: str
    session: boto3.Session | None = None
    region_name: str | None = None

    def gen_kwargs(self) -> dict[str, Any]:
        return {"auth": AWSSigV4(self.service, **_aws_credentials(self.session, self.region_name))}
