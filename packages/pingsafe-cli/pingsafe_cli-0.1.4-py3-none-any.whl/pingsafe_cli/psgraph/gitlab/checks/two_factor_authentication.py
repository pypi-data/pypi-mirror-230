from __future__ import annotations

from typing import Any

from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult
from pingsafe_cli.psgraph.gitlab.base_gitlab_configuration_check import BaseGitlabCheck
from pingsafe_cli.psgraph.gitlab.schemas.groups import schema
from pingsafe_cli.psgraph.json_doc.enums import BlockType


class GroupsTwoFactorAuthentication(BaseGitlabCheck):
    def __init__(self) -> None:
        name = "Ensure all Gitlab groups require two factor authentication"
        id = "CKV_GITLAB_2"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: list[dict[str, Any]], entity_type: str) -> CheckResult | None:  # type:ignore[override]
        if schema.validate(conf):
            for group in conf:
                if group.get("require_two_factor_authentication") is False:
                    return CheckResult.FAILED
            return CheckResult.PASSED
        return None


check = GroupsTwoFactorAuthentication()
