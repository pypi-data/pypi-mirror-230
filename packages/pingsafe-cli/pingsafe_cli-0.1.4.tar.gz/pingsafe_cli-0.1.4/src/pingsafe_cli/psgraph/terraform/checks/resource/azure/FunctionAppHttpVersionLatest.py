from pingsafe_cli.psgraph.common.models.enums import CheckCategories
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class FunctionAppHttpVersionLatest(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'HTTP Version' is the latest, if used to run the Function app"
        id = "CKV_AZURE_67"
        supported_resources = ['azurerm_function_app', 'azurerm_function_app_slot']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'site_config/[0]/http2_enabled'


check = FunctionAppHttpVersionLatest()
