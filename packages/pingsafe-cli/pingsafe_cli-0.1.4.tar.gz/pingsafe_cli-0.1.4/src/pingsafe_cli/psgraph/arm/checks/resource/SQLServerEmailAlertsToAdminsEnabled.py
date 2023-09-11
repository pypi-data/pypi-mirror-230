from typing import Dict, Any

from pingsafe_cli.psgraph.arm.base_resource_check import BaseResourceCheck
from pingsafe_cli.psgraph.common.models.enums import CheckResult, CheckCategories
from pingsafe_cli.psgraph.common.util.type_forcers import force_list

# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/securityalertpolicies


class SQLServerEmailAlertsToAdminsEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Email service and co-administrators' is 'Enabled' for MSSQL servers"
        id = "CKV_AZURE_27"
        supported_resources = ["Microsoft.Sql/servers/databases"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["resources"]
        resources = conf.get("resources") or []
        for idx, resource in enumerate(force_list(resources)):
            self.evaluated_keys = [
                f"resources/[{idx}]/type",
                f"resources/[{idx}]/properties/state",
                f"resources/[{idx}]/properties/emailAccountAdmins",
            ]
            if resource.get("type") in (
                "Microsoft.Sql/servers/databases/securityAlertPolicies",
                "securityAlertPolicies",
            ):
                properties = resource.get("properties")
                if isinstance(properties, dict):
                    state = properties.get("state")
                    if isinstance(state, str) and state.lower() == "enabled":
                        email_admins = properties.get("emailAccountAdmins")
                        if email_admins and email_admins.lower() == "enabled":
                            return CheckResult.PASSED

        return CheckResult.FAILED


check = SQLServerEmailAlertsToAdminsEnabled()
