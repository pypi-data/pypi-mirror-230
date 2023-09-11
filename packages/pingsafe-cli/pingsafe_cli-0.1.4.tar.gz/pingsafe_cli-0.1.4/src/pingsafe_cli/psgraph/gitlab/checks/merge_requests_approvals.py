from __future__ import annotations

from typing import Any

from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult
from pingsafe_cli.psgraph.gitlab.base_gitlab_configuration_check import BaseGitlabCheck
from pingsafe_cli.psgraph.gitlab.schemas.project_approvals import schema as project_aprovals_schema
from pingsafe_cli.psgraph.json_doc.enums import BlockType


class MergeRequestRequiresApproval(BaseGitlabCheck):
    def __init__(self) -> None:
        name = "Merge requests should require at least 2 approvals"
        id = "CKV_GITLAB_1"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        if project_aprovals_schema.validate(conf):
            if conf.get("approvals_before_merge", 0) < 2:
                return CheckResult.FAILED
            return CheckResult.PASSED
        return None


check = MergeRequestRequiresApproval()
