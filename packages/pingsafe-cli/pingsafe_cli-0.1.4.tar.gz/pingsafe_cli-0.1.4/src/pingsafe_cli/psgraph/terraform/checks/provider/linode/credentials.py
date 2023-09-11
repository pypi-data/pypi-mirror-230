import re
from typing import Dict, List, Any, Pattern

from pingsafe_cli.psgraph.common.models.enums import CheckResult, CheckCategories
from pingsafe_cli.psgraph.terraform.checks.provider.base_check import BaseProviderCheck
from pingsafe_cli.psgraph.common.models.consts import linode_token_pattern


class LinodeCredentials(BaseProviderCheck):
    def __init__(self) -> None:
        name = "Ensure no hard coded Linode tokens exist in provider"
        id = "CKV_LIN_1"
        supported_provider = ("linode",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_provider=supported_provider)

    def scan_provider_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if self.secret_found(conf, "token", linode_token_pattern):
            return CheckResult.FAILED
        return CheckResult.PASSED

    def secret_found(self, conf: Dict[str, List[Any]], field: str, pattern: Pattern[str]) -> bool:
        if field in conf.keys():
            value = conf[field][0]
            if re.match(pattern, value) is not None:
                conf[f'{self.id}_secret'] = value
                return True
        return False


check = LinodeCredentials()
