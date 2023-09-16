"""
.. module:: coral.http_auth
  :synopsis: HTTP authentication support classes

Copyright:: 2012 Amazon.com, Inc. or its affiliates.
All Rights Reserved.
"""

# imported modules:

import logging
import time
from base64 import b64encode
from collections import OrderedDict
from pathlib import Path

import requests
from requests.auth import AuthBase, HTTPBasicAuth, HTTPDigestAuth, HTTPProxyAuth
from requests_kerberos import OPTIONAL, REQUIRED, HTTPKerberosAuth

# constant definitions
CORAL_SSO_MILLISECOND_HEURISTIC = 1000
TOKEN_EXPIRY_WINDOW_SECONDS = 24 * 7 * 60 * 60
EXPIRE_TIME = 10 * 60
DEFAULT_HOST_CACHE_SIZE = 100
CA_ROOT_FILE = Path(__file__).parent / "ca_bundle.pem"

__all__ = ["HTTPBasicAuth", "HTTPProxyAuth", "HTTPDigestAuth", "HTTPSpnegoAuth"]

# logging configuration
log = logging.getLogger(__name__)


class SentryException(Exception):
    pass


class LoginResponseSentryException(SentryException):
    pass


class NotAuthSentryException(SentryException):
    pass


class NoHostSentryException(SentryException):
    pass


class HTTPSpnegoAuth(HTTPKerberosAuth):
    _service_name: str
    _auth_type: str

    def __init__(
        self,
        # service_name="HTTP",
        # auth_type="spnego",
        mutual_authentication=OPTIONAL,
    ):
        """Instantiates the SpnegoAuth object. It can raise an `ImportError` if
        the spnego module cannot be loaded.
        :raises ImportError: if spnego module cannot be loaded."""

        super().__init__(mutual_authentication=mutual_authentication)


class HTTPSentryAuth(AuthBase):
    def __init__(self, cache_size=DEFAULT_HOST_CACHE_SIZE):
        """Instantiates the HTTPSentryAuth object."""

        self._host_cache = OrderedDict()

        # We need kerb auth to talk to sentry token vendor
        self._kerbAuth = HTTPSpnegoAuth("HTTP@sentry.amazon.com")

    def __call__(self, request):
        host = request.headers["Host"]
        host_cache_entry = self._host_cache.get(host)

        # First time for this host?
        if not host_cache_entry:
            # host not in the cache
            # inserting a new entry in the cache
            # if the cache size is going to be over the limit
            # remove the first inserted entry
            if len(self._host_cache) == DEFAULT_HOST_CACHE_SIZE:
                log.debug("cache overflow: purging oldest cache entry")
                self._host_cache.popitem(0)  # type: ignore
            host_cache_entry = HostSentryCacheEntry(host)
            log.debug("inserting a new cache entry for host {0}".format(host))
            self._host_cache[host] = host_cache_entry

        # Is our entry expiring soon?
        if host_cache_entry.is_expiring():
            log.debug("cache expiring for host {0}".format(host))
            self._get_redirect_token_from_host(host_cache_entry)

        # Requests silently ignores prepare_cookies if a PreparedRequest already has a Cookie header; removing this allows the prepare_cookies to re-merge with the session cookies.
        if "Cookie" in request.headers:
            del request.headers["Cookie"]

        # Merge in cookies for the host from the host cache entry
        request.prepare_cookies(host_cache_entry.session.cookies)  # type: ignore

        return request

    def _get_redirect_token_from_host(self, host_cache_entry):
        log.debug("Host entry cache expired, starting a new session.")
        host_cache_entry.start_new_session()

        # Generate sentry url
        loginUrl = "https://%s/sso/login" % host_cache_entry.host

        # Ask for sso login details
        log.info("Requesting new SSO details.")
        login_response = host_cache_entry.session.request(
            "GET", loginUrl, verify=CA_ROOT_FILE, allow_redirects=False
        )

        if not login_response.ok:
            log.warning(
                "Got status code: {0} from SSO login handler:{1} ".format(
                    login_response.status_code, login_response.content
                )
            )
            raise LoginResponseSentryException(
                "Got status code: {0} from SSO login handler:{1} ".format(
                    login_response.status_code, login_response.content
                )
            )

        # Get response as json
        json_data = login_response.json()

        # get the token from sentry
        self._get_token_from_sentry_vendor(host_cache_entry, json_data["authn_endpoint"], loginUrl)

    def _get_token_from_sentry_vendor(self, host_cache_entry, authUrl, loginUrl):

        log.info("Requesting the new token from Sentry.")
        sentry_vendor_reply = host_cache_entry.session.request(
            "GET", authUrl, verify=CA_ROOT_FILE, allow_redirects=False, auth=self._kerbAuth
        )

        if not sentry_vendor_reply.ok:
            log.warning(
                "Got status code: {0} from SSO login handler {1}".format(
                    sentry_vendor_reply.status_code, sentry_vendor_reply.content
                )
            )
            raise LoginResponseSentryException(
                "Got status code: {0} from SSO login handler: {1}".format(
                    sentry_vendor_reply.status_code, sentry_vendor_reply.content
                )
            )

        id_token = sentry_vendor_reply.content

        # Now we need to get the cookie set
        origin_reply = host_cache_entry.session.request(
            "GET",
            loginUrl,
            verify=CA_ROOT_FILE,
            allow_redirects=False,
            params={"id_token": id_token},
        )

        # Get response as json
        json_data = origin_reply.json()

        if not json_data["is_authenticated"]:
            print(json_data)
            log.warning("Sentry was not authenticated after final redirect.")
            raise NotAuthSentryException("Sentry was not authenticated after final redirect.")

        host_cache_entry.update_expires(json_data["expires_at"])


class HostSentryCacheEntry:
    def __init__(self, host):
        if host is None or not host:
            log.warning("No host specified while checking cache expires or starting a new session.")
            raise NoHostSentryException("Host must be specified.")

        self._expires = 0
        self.host = host
        self.session = None

    def start_new_session(self):
        self.session = requests.Session()

    def update_expires(self, expires):
        """Coral SSO handler returns time in seconds.
        it receives that information from sentry and
        from the sentry token contents wiki page
        http://tiny/1aaubvf5y/wamazindeSentRegiHand)
        it is expressed in seconds."""

        self._expires = expires

    def is_expiring(self):
        # Are we expiring EXPIRE_TIME minutes from now?
        return (self._expires - time.time()) < EXPIRE_TIME
