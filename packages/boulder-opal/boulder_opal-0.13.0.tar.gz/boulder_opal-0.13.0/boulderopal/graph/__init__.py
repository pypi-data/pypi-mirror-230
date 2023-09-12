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

# Make private alias for all imports to clean up the autocomplete for the graph module.
import sys as _sys

from qctrlcommons.node.composite.namespace import NAMESPACE_ATTR as _ns
from qctrlcommons.node.composite.registry import (
    COMPOSITE_NAMESPACE_REGISTRY as _ns_registry,
)
from qctrlcommons.node.registry import PRIMARY_NAMESPACE_DOCS as _primary_namespace_docs
from qctrlcommons.node.registry import TYPE_REGISTRY as _type_registry

from boulderopal.graph._execute_graph import (
    ExecutionMode,
    execute_graph,
)
from boulderopal.graph._graph import Graph

# Binding the Graph related types to the current module, this is useful
# for building docs for the Graph class.
_module = _sys.modules[__name__]
for _type_cls in _type_registry:
    setattr(_module, _type_cls.__name__, _type_cls)


for _primary_namespace in _primary_namespace_docs:
    # Create namespace.
    setattr(_module, _primary_namespace.namespace_name, _primary_namespace)

    # Bind namespace methods.
    for _node_name, _node_method in _primary_namespace.sub_nodes.items():
        setattr(
            getattr(_module, _primary_namespace.namespace_name),
            _node_name,
            _node_method,
        )


# Set composite namespaces to Graph.
# This import-time binding is only useful for building the docs.
# The actual composite namespace object is created during the
# Graph object initialization time.
for _composite_namespace in _ns_registry:
    setattr(_module, getattr(_composite_namespace, _ns), _composite_namespace)


__all__ = ["ExecutionMode", "Graph", "execute_graph"]
