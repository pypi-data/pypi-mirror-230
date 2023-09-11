from typing import Optional, Any, Dict

from pingsafe_cli.psgraph.common.graph.checks_infra.enums import Operators
from pingsafe_cli.psgraph.common.checks_infra.solvers.attribute_solvers.base_attribute_solver import BaseAttributeSolver


class EndingWithAttributeSolver(BaseAttributeSolver):
    operator = Operators.CONTAINS  # noqa: CCE003  # a static attribute

    def _get_operation(self, vertex: Dict[str, Any], attribute: Optional[str]) -> bool:
        attr = vertex.get(attribute)  # type:ignore[arg-type]  # due to attribute can be None
        return isinstance(attr, str) and attr.endswith(self.value)
