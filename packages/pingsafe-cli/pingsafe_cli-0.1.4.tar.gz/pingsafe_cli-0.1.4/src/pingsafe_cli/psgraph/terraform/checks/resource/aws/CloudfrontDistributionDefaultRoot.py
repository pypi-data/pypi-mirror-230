from pingsafe_cli.psgraph.common.models.consts import ANY_VALUE
from pingsafe_cli.psgraph.common.models.enums import CheckCategories
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudfrontDistributionDefaultRoot(BaseResourceValueCheck):

    def __init__(self):
        """
        NIST.800-53.r5 SC-7(11), NIST.800-53.r5 SC-7(16)
        CloudFront distributions should have a default root object configured
        """
        name = "Ensure Cloudfront distribution has a default root object configured"
        id = "CKV_AWS_305"
        supported_resources = ['aws_cloudfront_distribution']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "default_root_object"

    def get_expected_value(self):
        return ANY_VALUE


check = CloudfrontDistributionDefaultRoot()
