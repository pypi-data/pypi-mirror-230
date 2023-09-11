from abc import abstractmethod

from pingsafe_cli.psgraph.common.checks.base_check import BaseCheck
from pingsafe_cli.psgraph.serverless.checks.package.registry import package_registry


class BasePackageCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities, guideline=None):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_entities,
                         block_type="serverless", guideline=guideline)
        package_registry.register(self)

    def scan_entity_conf(self, conf, entity_type):
        return self.scan_package_conf(conf)

    @abstractmethod
    def scan_package_conf(self, conf):
        raise NotImplementedError()
