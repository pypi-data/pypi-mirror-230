from pingsafe_cli.psgraph.common.models.enums import CheckResult, CheckCategories
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ELBv2AccessLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the ELBv2 (Application/Network) has access logging enabled"
        id = "CKV_AWS_91"
        supported_resources = ["aws_lb", "aws_alb"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "access_logs/0/enabled/0"

    def scan_resource_conf(self, conf):
        if conf.get("load_balancer_type") == ["gateway"]:
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)


check = ELBv2AccessLogs()
