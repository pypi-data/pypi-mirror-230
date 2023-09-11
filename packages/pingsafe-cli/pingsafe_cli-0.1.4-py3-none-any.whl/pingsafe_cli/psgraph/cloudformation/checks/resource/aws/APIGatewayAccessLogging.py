from pingsafe_cli.psgraph.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from pingsafe_cli.psgraph.common.models.enums import CheckCategories
from pingsafe_cli.psgraph.common.models.consts import ANY_VALUE


class APIGatewayAccessLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure API Gateway has Access Logging enabled"
        id = "CKV_AWS_76"
        supported_resources = ['AWS::ApiGateway::Stage', "AWS::Serverless::Api"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/AccessLogSetting/DestinationArn'

    def get_expected_value(self):
        return ANY_VALUE


check = APIGatewayAccessLogging()
