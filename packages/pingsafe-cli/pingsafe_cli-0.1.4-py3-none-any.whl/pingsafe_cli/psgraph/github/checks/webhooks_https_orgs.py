from __future__ import annotations

import re
from typing import Any

from pingsafe_cli.psgraph.common.models.enums import CheckResult, CheckCategories
from pingsafe_cli.psgraph.github.base_github_configuration_check import BaseGithubCheck, HTTP
from pingsafe_cli.psgraph.github.schemas.org_webhooks import schema as org_webhooks_schema
from pingsafe_cli.psgraph.json_doc.enums import BlockType


class WebhookHttpsOrg(BaseGithubCheck):
    def __init__(self) -> None:
        name = "Ensure GitHub organization webhooks are using HTTPS"
        id = "CKV_GITHUB_6"
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(
            id=id,
            name=name,
            categories=categories,
            supported_entities=["*"],
            block_type=BlockType.DOCUMENT
        )

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]] | None:  # type:ignore[override]
        ckv_metadata, conf = self.resolve_ckv_metadata_conf(conf=conf)
        if 'org_webhooks' in ckv_metadata.get('file_name', ''):
            if org_webhooks_schema.validate(conf):
                for item in conf:
                    if isinstance(item, dict):
                        item_config = item.get("config", {})
                        if not item_config:
                            continue
                        url = item_config.get('url', '')
                        insecure_ssl = item_config.get('insecure_ssl', '0')
                        secret = item_config.get('secret', '')
                        if re.match(HTTP, url):
                            return CheckResult.FAILED, item_config
                        if insecure_ssl != '0' and secret != '********':  # nosec
                            return CheckResult.FAILED, item_config
                return CheckResult.PASSED, conf
        return CheckResult.UNKNOWN, conf


check = WebhookHttpsOrg()
