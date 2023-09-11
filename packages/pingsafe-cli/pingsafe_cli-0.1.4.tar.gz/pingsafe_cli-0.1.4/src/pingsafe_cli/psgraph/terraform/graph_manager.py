from __future__ import annotations

import logging
import os
from typing import Type, Any, TYPE_CHECKING

from pingsafe_cli.psgraph.common.runners.base_runner import strtobool
from pingsafe_cli.psgraph.common.util.consts import DEFAULT_EXTERNAL_MODULES_DIR
from pingsafe_cli.psgraph.terraform.graph_builder.local_graph import TerraformLocalGraph
from pingsafe_cli.psgraph.terraform.parser import Parser

from pingsafe_cli.psgraph.common.graph.graph_manager import GraphManager
from pingsafe_cli.psgraph.terraform.tf_parser import TFParser

if TYPE_CHECKING:
    from pingsafe_cli.psgraph.common.typing import LibraryGraphConnector


class TerraformGraphManager(GraphManager[TerraformLocalGraph, "dict[str, dict[str, Any]]"]):
    def __init__(self, db_connector: LibraryGraphConnector, source: str = "") -> None:
        parser = TFParser() if strtobool(os.getenv('PINGSAFE_NEW_TF_PARSER', 'False')) else Parser()
        super().__init__(db_connector=db_connector, parser=parser, source=source)

    def build_graph_from_source_directory(
        self,
        source_dir: str,
        render_variables: bool = True,
        local_graph_class: Type[TerraformLocalGraph] = TerraformLocalGraph,
        parsing_errors: dict[str, Exception] | None = None,
        download_external_modules: bool = False,
        external_modules_download_path: str = DEFAULT_EXTERNAL_MODULES_DIR,
        excluded_paths: list[str] | None = None,
        vars_files: list[str] | None = None,
        create_graph: bool = True,
    ) -> tuple[TerraformLocalGraph | None, dict[str, dict[str, Any]]]:
        logging.info("Parsing HCL files in source dir")
        module, tf_definitions = self.parser.parse_hcl_module(
            source_dir=source_dir,
            source=self.source,
            download_external_modules=download_external_modules,
            external_modules_download_path=external_modules_download_path,
            parsing_errors=parsing_errors,
            excluded_paths=excluded_paths,
            vars_files=vars_files,
            create_graph=create_graph,
        )

        local_graph = None
        if create_graph and module:
            logging.info("Building graph from parsed module")
            local_graph = local_graph_class(module)
            local_graph.build_graph(render_variables=render_variables)

        return local_graph, tf_definitions

    def build_graph_from_definitions(
        self, definitions: dict[str, dict[str, Any]], render_variables: bool = True
    ) -> TerraformLocalGraph:
        module, _ = self.parser.parse_hcl_module_from_tf_definitions(definitions, "", self.source)
        local_graph = TerraformLocalGraph(module)
        local_graph.build_graph(render_variables=render_variables)

        return local_graph
