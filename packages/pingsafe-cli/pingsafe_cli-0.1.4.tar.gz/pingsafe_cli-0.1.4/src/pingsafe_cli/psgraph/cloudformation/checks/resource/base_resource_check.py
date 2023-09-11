from abc import abstractmethod
from collections.abc import Iterable
from typing import Callable, Optional, Dict, Any

from pingsafe_cli.psgraph.cloudformation.checks.resource.registry import cfn_registry
from pingsafe_cli.psgraph.common.checks.base_check import BaseCheck
from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult
from pingsafe_cli.psgraph.common.multi_signature import multi_signature


class BaseResourceCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: "Iterable[CheckCategories]",
        supported_resources: "Iterable[str]",
        guideline: Optional[str] = None,
    ) -> None:
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_resources,
            block_type="resource",
            guideline=guideline,
        )
        self.supported_resources = supported_resources
        cfn_registry.register(self)

    def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        self.entity_type = entity_type

        return self.scan_resource_conf(conf, entity_type)

    @multi_signature()
    @abstractmethod
    def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        raise NotImplementedError()

    @classmethod
    @scan_resource_conf.add_signature(args=["self", "conf"])
    def _scan_resource_conf_self_conf(cls, wrapped: Callable[..., CheckResult]) -> Callable[..., CheckResult]:
        def wrapper(self: BaseCheck, conf: Dict[str, Any], entity_type: Optional[str] = None) -> CheckResult:
            # keep default argument for entity_type so old codescanner, that doesn't set it, will work.
            return wrapped(self, conf)

        return wrapper
