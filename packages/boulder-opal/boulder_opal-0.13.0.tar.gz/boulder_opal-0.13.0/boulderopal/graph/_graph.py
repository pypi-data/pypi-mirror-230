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
Functionality related to the computational-flow graph object.

The Graph object and its associated data types (Tensor, Pwc, ...) are re-imported here to
allow their access directly from the client package.
"""

from qctrlcommons.graph import Graph

# List of nodes that won't be migrated to the new Boulder Opal Client.
_OBSOLETE_NODES = [
    "random_choices",
    "random_colored_noise_stf_signal",
    "random_normal",
    "random_uniform",
]
_OBSOLETE_NODES += [
    "ms_dephasing_robust_cost",
    "ms_displacements",
    "ms_infidelity",
    "ms_phases",
    "ms_phases_multitone",
]

# Remove obsolete nodes manually from the commons graph during the migration
# period. After the old Q-CTRL Client is retired and the obsolete nodes are
# removed from commons, delete this code.
for node_name in _OBSOLETE_NODES:
    if hasattr(Graph, node_name):
        delattr(Graph, node_name)
