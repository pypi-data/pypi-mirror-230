# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
"""
Functionality related to the Q-CTRL graph structure.

The commons objects are re-imported here to allow all access to the objects to happen directly from
the `qctrl` package.
"""

import sys
from functools import partial as _partial

# We import Graph to expose it directly from this module.
# pylint: disable=unused-import
from qctrlcommons.graph import Graph as _BaseGraph
from qctrlcommons.node.composite.registry import (
    COMPOSITE_NODE_REGISTRY as _COMPOSITE_NODES,
)
from qctrlcommons.node.registry import NODE_REGISTRY as _NODE_REGISTRY
from qctrlcommons.node.registry import TYPE_REGISTRY as _TYPE_REGISTRY

from qctrl import toolkit as _toolkit
from qctrl.builders.namespaces import ToolkitCategory as _ToolkitCategory
from qctrl.builders.namespaces import build_and_bind_toolkit as _build_and_bind_toolkit
from qctrl.utils import PackageRegistry as _PackageRegistry

_module = sys.modules[__name__]
for _type_cls in _TYPE_REGISTRY:
    setattr(_module, _type_cls.__name__, _type_cls)

_OBSOLETE_NODES = [
    "random_choices",
    "random_colored_noise_stf_signal",
    "random_normal",
    "random_uniform",
    "ms_dephasing_robust_cost",
    "ms_displacements",
    "ms_infidelity",
    "ms_phases",
    "ms_phases_multitone",
]


# pylint: disable=too-few-public-methods
class Graph(_BaseGraph):

    """
    Utility class for representing and building a Q-CTRL data flow graph.
    """

    def __init__(self):
        super().__init__()
        _build_and_bind_toolkit(self, _ToolkitCategory.NODES, _toolkit)
        for _name in _OBSOLETE_NODES:
            if not hasattr(self, _name):
                setattr(
                    self,
                    _name,
                    _partial(
                        _NODE_REGISTRY.get_node_cls(_name).create_graph_method(), self
                    ),
                )

    def _add_composite_nodes(self):
        # Adding this method overrides the method from the _BaseGraph
        # preventing the composite nodes from being added.
        # This is done so that the namespacing in the graph object performed in commons
        # (due to the new client) does not affect the legacy client toolkit namespaces.
        pass


def _func(name, *args, **kwargs):  # pylint:disable=unused-argument
    print(
        f"Can not access node {name} from the Graph object directly in the legacy Q-CTRL package. "
        f"Use `graph.utils.{name}` instead."
    )


for _node in _COMPOSITE_NODES:
    setattr(Graph, _node.__name__, _partial(_func, _node.__name__))
