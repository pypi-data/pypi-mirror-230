from pingsafe_cli.psgraph.common.models.enums import CheckResult, CheckCategories
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PostgreSQLMinTLSVersion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure PostgreSQL is using the latest version of TLS encryption"
        id = "CKV_AZURE_147"
        supported_resources = ['azurerm_postgresql_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "ssl_minimal_tls_version_enforced"

    def get_expected_value(self):
        return 'TLS1_2'


check = PostgreSQLMinTLSVersion()
