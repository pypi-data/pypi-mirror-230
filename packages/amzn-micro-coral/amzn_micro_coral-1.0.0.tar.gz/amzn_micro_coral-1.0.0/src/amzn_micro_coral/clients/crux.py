from __future__ import annotations

import subprocess
from dataclasses import dataclass
from functools import cached_property
import re
from pathlib import Path

from typing import Any
from typing import Literal

from amzn_micro_coral import CoralService
from amzn_micro_coral import CoralAuth
from amzn_micro_coral import auth


# From: https://builderhub.corp.amazon.com/docs/crux/api-guide/datatypes-simple-com.amazon.critic.html#com-amazon-critic-revision-status
REVISION_STATUS = ["CANCELED", "OPEN", "PENDING", "SHIPPED"]
RevisionStatus = Literal["CANCELED", "OPEN", "PENDING", "SHIPPED"]

CR_COMMAND = "cr"

crux_service = CoralService(
    url="https://critic-service-sso.corp.amazon.com/",
    auth=auth.Midway(),
)


class CruxCliError(Exception):
    def __init__(self, cmd: list[str], stdout: str = "", stderr: str = "") -> None:
        super().__init__(self, f"Failed to run: '{' '.join(cmd)}': {stderr}")


class CruxError(Exception):
    pass


@dataclass(frozen=True)
class CruxService(CoralService):
    """
    Barebones implementation of a CoralService that interacts with CRUX.

    Includes some helper methods for grabbing metadata from the CRUX service
    as well as a convenient class wrapper grabbing CR metadata.
    """

    url: str = "https://critic-service-sso.corp.amazon.com/"
    auth: CoralAuth = CoralAuth.midway()

    def _parse_cr_output(self, out: str) -> CodeReview | None:
        m = re.search(r"https://code\.amazon\.com/reviews/(CR-[0-9]+)(?:/revisions/([0-9]+))?", out)
        if m is not None:
            cr_id = m.group(1)
            cr_rev = m.group(2) or "1"
            return CodeReview(self, cr_id, int(cr_rev))
        else:
            return None

    def submit(
        self,
        cwd: Path | None = None,
        update_review: str | None = None,
        new_review: bool = False,
        vs: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        reviewers: str | None = None,
        publish: bool = False,
    ) -> CodeReview:
        cmd = [CR_COMMAND]

        if update_review is not None:
            cmd += ["--update_review", update_review]
        if new_review:
            cmd += ["--new-review"]
        if vs is not None:
            cmd += ["--vs", vs]
        if summary is not None:
            cmd += ["--summary", summary]
        if description is not None:
            cmd += ["--description", description]
        if reviewers is not None:
            cmd += ["--reviewers", reviewers]
        if publish:
            cmd += ["--publish"]

        try:
            out_raw = subprocess.check_output(cmd)
            out = out_raw.decode()
        except subprocess.CalledProcessError as e:
            raise CruxCliError(cmd) from e

        if out.startswith("Your package is unmodified."):
            raise CruxError("Your package is unmodified.")

        cr = self._parse_cr_output(out)
        if cr is None:
            raise CruxError(f"Unexpected output:\n{out}")

        return cr


@dataclass(frozen=True)
class CodeReview:
    _service: CruxService
    id: str
    revision: int = 1

    @property
    def url(self) -> str:
        return f"https://code.amazon.com/reviews/{self.id}/revisions/{self.revision}"

    @cached_property
    def _revision_data(self) -> dict:
        # see: https://builderhub.corp.amazon.com/docs/crux/api-guide/datatypes-complex-com.amazon.critic.html#com-amazon-critic-get-revision-response
        return self._service.post(
            "CriticService.GetRevision",
            {
                "reviewRevision": {
                    "cr": self.id,
                    "revision": self.revision,
                },
            },
        ).json()

    @cached_property
    def dry_run_status(self) -> str | None:
        analyzers = self._revision_data["analyzers"]
        for analyzer in analyzers:
            if analyzer["partner_id"] == "Dry Run Build":
                return analyzer["status"]
        return None

    @cached_property
    def status(self) -> RevisionStatus:
        return self._revision_data["status"]  # type: ignore

    def _reset_cache(self) -> None:
        if "_revision_data" in self.__dict__:
            del self.__dict__["_revision_data"]
        if "dry_run_status" in self.__dict__:
            del self.__dict__["dry_run_status"]
        if "status" in self.__dict__:
            del self.__dict__["status"]

    def update(
        self,
        summary: str | None = None,
        description: str | None = None,
        requester: str | None = None,
        publish: bool = False,
    ) -> None:
        request: dict[str, Any] = {
            "reviewRevision": {
                "cr": self.id,
                "revision": self.revision,
            },
        }
        if summary is not None:
            request["summary"] = summary
        if description is not None:
            request["description"] = description
        if requester is not None:
            req_type, req_id = tuple(requester.split(":", 2))
            request["requester"] = {"id": req_id, "type": req_type}
        if publish:
            request["performRevisionPublish"] = True

        result = self._service.post("CriticService.UpdateReviewInfo", request)
        self._reset_cache()

    def publish(self) -> None:
        self.update(publish=True)
