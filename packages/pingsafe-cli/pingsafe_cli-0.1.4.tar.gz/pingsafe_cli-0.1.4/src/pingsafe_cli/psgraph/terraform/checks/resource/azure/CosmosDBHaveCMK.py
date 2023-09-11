from pingsafe_cli.psgraph.common.models.consts import ANY_VALUE
from pingsafe_cli.psgraph.common.models.enums import CheckCategories
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CosmosDBHaveCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Cosmos DB accounts have customer-managed keys to encrypt data at rest"
        id = "CKV_AZURE_100"
        supported_resources = ['azurerm_cosmosdb_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'key_vault_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = CosmosDBHaveCMK()
