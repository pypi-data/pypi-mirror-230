from pingsafe_cli.psgraph.common.pingsafe.check_type import CheckType
from pingsafe_cli.psgraph.common.checks.object_registry import Registry as BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__(CheckType.OPENAPI)

    def get_key(self, entity_type: str, entity_name: str, check_id: str, file_path: str) -> str:
        return f'{file_path}.{entity_name}.{check_id}'
