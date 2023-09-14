from typing import Union

from dbt_artifacts_parser.parsers.manifest.manifest_v8 import (
    AnalysisNode,
    GenericTestNode,
    HookNode,
    ManifestV8,
    ModelNode,
    RPCNode,
    SeedNode,
    SingularTestNode,
    SnapshotNode,
    SourceDefinition,
    SqlNode,
)

NodeTypes = Union[
    AnalysisNode,
    SingularTestNode,
    HookNode,
    ModelNode,
    RPCNode,
    SqlNode,
    GenericTestNode,
    SnapshotNode,
    SeedNode,
]

SourceTypes = Union[SourceDefinition]
