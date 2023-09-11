from __future__ import annotations

from typing import TYPE_CHECKING

from pingsafe_cli.psgraph.common.models.enums import CheckCategories, CheckResult
from pingsafe_cli.psgraph.dockerfile.base_dockerfile_check import BaseDockerfileCheck

if TYPE_CHECKING:
    from dockerfile_parse.parser import _Instruction


class AliasIsUnique(BaseDockerfileCheck):
    def __init__(self) -> None:
        """
        Ensure From Alias are unique for multistage builds.
        """
        name = "Ensure From Alias are unique for multistage builds."
        id = "CKV_DOCKER_11"
        supported_instructions = ("FROM",)
        categories = (CheckCategories.CONVENTION,)
        super().__init__(name=name, id=id, categories=categories, supported_instructions=supported_instructions)

    def scan_resource_conf(self, conf: list[_Instruction]) -> tuple[CheckResult, list[_Instruction] | None]:
        alias = []
        for instruction in conf:
            if " as " in instruction["value"]:
                temp = instruction["value"].split()
                alias += [temp[2]]

        if len(alias) == len(set(alias)):
            return CheckResult.PASSED, None
        else:
            return CheckResult.FAILED, [conf[0]]


check = AliasIsUnique()
