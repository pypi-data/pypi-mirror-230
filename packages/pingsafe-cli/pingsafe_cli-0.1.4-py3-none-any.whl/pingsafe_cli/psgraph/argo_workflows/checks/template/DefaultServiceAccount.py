from __future__ import annotations

from typing import Any

from pingsafe_cli.psgraph.argo_workflows.checks.base_argo_workflows_check import BaseArgoWorkflowsCheck
from pingsafe_cli.psgraph.common.models.enums import CheckResult, CheckCategories
from pingsafe_cli.psgraph.yaml_doc.enums import BlockType


class DefaultServiceAccount(BaseArgoWorkflowsCheck):
    def __init__(self) -> None:
        name = "Ensure Workflow pods are not using the default ServiceAccount"
        id = "CKV_ARGO_1"
        super().__init__(
            name=name,
            id=id,
            categories=(CheckCategories.IAM,),
            supported_entities=("spec",),
            block_type=BlockType.OBJECT,
        )

    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]]:
        if "serviceAccountName" in conf.keys() and conf["serviceAccountName"] != "default":
            return CheckResult.PASSED, conf

        return CheckResult.FAILED, conf


check = DefaultServiceAccount()
