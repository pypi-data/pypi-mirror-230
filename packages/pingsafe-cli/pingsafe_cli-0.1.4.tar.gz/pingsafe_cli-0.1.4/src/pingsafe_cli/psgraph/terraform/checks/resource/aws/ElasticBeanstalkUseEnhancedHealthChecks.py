from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult
from pingsafe_cli.psgraph.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ElasticBeanstalkUseEnhancedHealthChecks(BaseResourceCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 CA-7, NIST.800-53.r5 SI-2
        """
        name = "Ensure Elastic Beanstalk environments have enhanced health reporting enabled"
        id = "CKV_AWS_312"
        supported_resources = ('aws_elastic_beanstalk_environment',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        settings = conf.get("setting")
        if settings and isinstance(settings, list):
            if isinstance(settings[0], list):
                settings = settings[0]
            for setting in settings:
                namespace = setting.get("namespace")
                if isinstance(namespace, list) and namespace[0] == "aws:elasticbeanstalk:healthreporting:system":
                    setting_val = setting.get("value")
                    if isinstance(setting_val, list) and setting_val[0] == "enhanced":
                        return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticBeanstalkUseEnhancedHealthChecks()
