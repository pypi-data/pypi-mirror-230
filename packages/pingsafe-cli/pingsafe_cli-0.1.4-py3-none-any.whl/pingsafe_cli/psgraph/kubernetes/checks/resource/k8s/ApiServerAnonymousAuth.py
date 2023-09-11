from typing import Dict, Any

from pingsafe_cli.psgraph.common.models.enums import CheckResult
from pingsafe_cli.psgraph.kubernetes.checks.resource.base_container_check import BaseK8sContainerCheck


class ApiServerAnonymousAuth(BaseK8sContainerCheck):
    def __init__(self) -> None:
        id = "CKV_K8S_68"
        name = "Ensure that the --anonymous-config argument is set to false"
        super().__init__(name=name, id=id)

    def scan_container_conf(self, metadata: Dict[str, Any], conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_container_keys = ["command"]
        if conf.get("command"):
            if "kube-apiserver" in conf["command"]:
                if "--anonymous-config=false" not in conf["command"]:
                    return CheckResult.FAILED

        return CheckResult.PASSED


check = ApiServerAnonymousAuth()
