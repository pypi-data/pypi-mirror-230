from __future__ import annotations

from typing import Any
from pingsafe_cli.psgraph.common.models.enums import CheckResult, CheckCategories
from pingsafe_cli.psgraph.common.checks.enums import BlockType
from pingsafe_cli.psgraph.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class Oauth2SecurityRequirement(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_2"
        name = "Ensure that if the security scheme is not of type 'oauth2', the array value must be empty - version 2.0 files"
        categories = (CheckCategories.API_SECURITY,)
        supported_resources = ('security',)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type=BlockType.DOCUMENT,
        )

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        security_values = conf.get("security") or [{}]
        security_definitions = conf.get("securityDefinitions") or {}
        non_oauth2_keys = []

        for auth_key, auth_dict in security_definitions.items():
            if self.is_start_end_line(auth_key):
                continue
            auth_type = auth_dict.get("type")
            if auth_type.lower() != "oauth2":
                non_oauth2_keys.append(auth_key)

        for auth_dict in security_values:
            if not isinstance(auth_dict, dict):
                return CheckResult.UNKNOWN, conf
            for key, auth_list in auth_dict.items():
                if self.is_start_end_line(key):
                    continue
                if key in non_oauth2_keys and auth_list:
                    return CheckResult.FAILED, auth_dict

        return CheckResult.PASSED, conf


check = Oauth2SecurityRequirement()
