from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from pingsafe_cli.psgraph.bitbucket.registry import registry
from pingsafe_cli.psgraph.common.checks.base_check import BaseCheck

if TYPE_CHECKING:
    from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult


class BaseBitbucketCheck(BaseCheck):
    def __init__(
        self,
        name: str,
        id: str,
        categories: Iterable[CheckCategories],
        supported_entities: Iterable[str],
        block_type: str,
        path: str | None = None,
        guideline: str | None = None,
    ):
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
            guideline=guideline,
        )
        self.path = path
        registry.register(self)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]] | None:  # type:ignore[override]  # multi_signature decorator is problematic
        self.entity_type = entity_type

        return self.scan_conf(conf)

    @abstractmethod
    def scan_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any]] | None:
        pass
