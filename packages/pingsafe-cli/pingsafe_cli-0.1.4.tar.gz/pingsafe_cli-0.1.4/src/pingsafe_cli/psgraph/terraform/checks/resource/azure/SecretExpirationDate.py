from pingsafe_cli.psgraph.common.models.enums import CheckCategories
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from pingsafe_cli.psgraph.common.models.consts import ANY_VALUE


class SecretExpirationDate(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that the expiration date is set on all secrets"
        id = "CKV_AZURE_41"
        supported_resources = ['azurerm_key_vault_secret']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'expiration_date'

    def get_expected_value(self):
        return ANY_VALUE


check = SecretExpirationDate()
