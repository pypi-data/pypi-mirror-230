# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from pathlib import Path

import yaml

from .._constants import ComponentSource
from ._base_compiler import BaseCompiler

# pylint: disable=protected-access


class PromptflowComponentCompiler(BaseCompiler):
    """A compiler to compile v1.5 components"""

    # Unlike regular components, promptflow component will be generated with promptflow build
    # the "component yaml" will be generated in the same process
    # So we simply bypass the _update_compile_content and _dump_component_yaml

    def _update_compile_content(self):
        pass

    def _dump_component_yaml(self, dest_folder: Path):
        pass

    def _copy_snapshot(self, dest_folder: Path):
        try:
            from promptflow import PFClient

            pf = PFClient()
        except ImportError as e:
            raise ImportError(
                "Please install mldesigner with promptflow to compile a flow: "
                "pip install mldesigner[promptflow]: %s" % str(e)
            ) from e

        flow_dag_path = Path(self._component.base_path, getattr(self._component, "flow"))
        # TODO: prepare a separate private interface for this in promptflow
        pf.flows.build(
            flow=flow_dag_path,
            output=dest_folder,
            flow_only=True,
        )

        # TODO: use promptflow.runs.build to compile run.yaml?
        # support compile run.yaml
        if self._component._source != ComponentSource.YAML_COMPONENT:
            return
        source_path = Path(self._component._source_path)
        if source_path.samefile(flow_dag_path):
            return
        with open(dest_folder / source_path.name, "w", encoding="utf-8") as run_yaml_file:
            run_obj = yaml.safe_load(source_path.read_text(encoding="utf-8"))
            run_obj["flow"] = "."
            yaml.dump(run_obj, run_yaml_file, sort_keys=False)
