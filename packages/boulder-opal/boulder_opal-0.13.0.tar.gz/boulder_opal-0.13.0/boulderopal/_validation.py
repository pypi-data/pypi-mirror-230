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
Validation utilities for Boulder Opal APIs.
"""

from __future__ import annotations

import sys
from collections import (
    deque,
    namedtuple,
)
from enum import Enum
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    Optional,
    Type,
    TypeVar,
    Union,
)

import numpy as np
from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlcommons.node.registry import NODE_REGISTRY
from qctrlcommons.node.wrapper import (
    NodeData,
    Operation,
)
from qctrlcommons.preconditions import check_argument

if TYPE_CHECKING:
    from boulderopal import Graph

if sys.version_info >= (3, 10):
    from typing import (
        Concatenate,
        ParamSpec,
    )
else:
    from typing_extensions import (
        Concatenate,
        ParamSpec,
    )


def validate_output_node_names(node_names: str | list[str], graph: Graph) -> list[str]:
    """
    Validate the names of the output nodes for fetching from a graph.

    If any node is not in the graph, raise an error. Otherwise, normalize the names to a list of
    strings.

    Parameters
    ---------
    node_names : str or list[str]
        Name of the nodes to be fetched.
    graph : Graph
        The graph where the nodes are supposed to be fetched from.

    Returns
    -------
    list[str]
        A list of valid node names.
    """

    if isinstance(node_names, str):
        node_names = [node_names]

    check_argument(
        isinstance(node_names, list)
        and all(isinstance(name, str) for name in node_names),
        "The output node names must be a string or a list of strings.",
        {"output_node_names": node_names},
    )

    check_argument(
        len(node_names) >= 1,
        "The output node names must have at least one element.",
        {"output_node_names": node_names},
    )

    for name in node_names:
        check_node_in_graph(
            name,
            graph,
            f"The requested output node name '{name}' is not present in the graph.",
        )

    return node_names


def check_node_in_graph(node: str, graph: Graph, message: str):
    """
    Check if a node is in the Graph.

    Parameters
    ----------
    node : str
        The name of the node.
    graph : Graph
        The Graph to be validated.
    message : str
        The error message.
    """
    check_argument(
        node in graph.operations, message, {"graph": graph}, extras={"node name": node}
    )


def check_optimization_node_in_graph(graph: Graph):
    """
    Check optimization graph at least has one optimization node.
    """
    for operation in graph.operations.values():
        if NODE_REGISTRY.get_node_cls(operation.operation_name).optimizable_variable:
            return
    raise QctrlArgumentsValueError(
        "At least one optimization variable is required in the optimization graph.",
        {"graph": graph},
    )


def check_cost_node(node: str, graph: Graph):
    """
    Check cost node:
        - if the node is in the graph.
        - if the node is a scalar Tensor.
    """
    check_argument(
        isinstance(node, str),
        "The cost node name must be a string.",
        {"cost_node_name": node},
    )
    check_node_in_graph(node, graph, "A cost node must be present in the graph.")
    check_argument(
        graph.operations[node].is_scalar_tensor,
        "The cost node must be a scalar Tensor.",
        {"cost": node},
        extras={"cost node operation": graph.operations[node]},
    )


def check_cost_node_for_optimization_graph(
    graph: Graph,
    cost_node_name: str,
    output_node_names: list[str],
    check_gradient_nodes: bool = True,
):
    """
    Traverse the graph from the cost node, and check:
        1. All connected the nodes should support gradient if `check_gradient_nodes` is True.
        2. Any optimizable node to be fetched should connect to the cost node.
    """

    connected_optimization_node_names = set()

    def _validate_node_from_operation(operation):
        node = NODE_REGISTRY.get_node_cls(operation.operation_name)
        if check_gradient_nodes:
            check_argument(
                node.supports_gradient,
                f"The {operation.operation_name} node does not support gradient.",
                {"graph": graph},
            )
        if node.optimizable_variable:
            connected_optimization_node_names.add(operation.name)

    def _get_parent_operations(node: str) -> Iterable[Operation]:
        """
        Go through inputs of the nodes, which might include Python primitive iterables.
        Find all NodeData and flat them as a single iterable.
        """

        def _get_input_items(input_):
            if isinstance(input_, NodeData):
                return [input_.operation]
            if isinstance(input_, (list, tuple)):
                return chain.from_iterable(_get_input_items(item) for item in input_)
            if isinstance(input_, dict):
                return chain.from_iterable(
                    _get_input_items(item) for item in input_.values()
                )
            return []

        return chain.from_iterable(
            _get_input_items(input_)
            for input_ in graph.operations[node].kwargs.values()
        )

    visited_nodes: set[str] = set()
    nodes_to_check: deque = deque()

    # cost node is where we start with.
    _validate_node_from_operation(graph.operations[cost_node_name])
    visited_nodes.add(cost_node_name)
    nodes_to_check.appendleft(cost_node_name)

    while nodes_to_check:
        node = nodes_to_check.pop()

        for operation in _get_parent_operations(node):
            if operation.name not in visited_nodes:
                _validate_node_from_operation(operation)
                visited_nodes.add(operation.name)
                nodes_to_check.appendleft(operation.name)

    # Graph traverse is done and all connected optimization nodes are recorded.
    # Now check output nodes.
    for output_node in output_node_names:
        op_name = graph.operations[output_node].operation_name
        if NODE_REGISTRY.get_node_cls(op_name).optimizable_variable:
            check_argument(
                output_node in connected_optimization_node_names,
                "The requested optimization node in `output_node_names` is not connected "
                "to the cost node.",
                {"output_node_names": output_node_names},
                extras={"disconnected output node name": output_node},
            )


def check_initial_value_for_optimization_node(graph: Graph):
    """
    Check optimization node has valid non-default initial values.
    """

    initial_value_info = {}

    for name, operation in graph.operations.items():
        node = NODE_REGISTRY.get_node_cls(operation.operation_name)
        if (
            node.optimizable_variable
            and operation.kwargs.get("initial_values") is not None
        ):
            initial_value_info[name] = operation.kwargs["initial_values"]

    initial_values = list(initial_value_info.values())
    if len(initial_values) != 0:
        for val in initial_values[1:]:
            if not isinstance(val, type(initial_values[0])):
                raise QctrlArgumentsValueError(
                    "Non-default initial values of optimization variables in the graph"
                    " must all either be an array or a list of arrays.",
                    {"graph": graph},
                    extras=initial_value_info,
                )

        if isinstance(initial_values[0], list):
            for val in initial_values[1:]:
                if len(val) != len(initial_values[0]):
                    raise QctrlArgumentsValueError(
                        "Lists of initial values of optimization variables must have "
                        "the same length.",
                        {"graph": graph},
                        extras=initial_value_info,
                    )


T = TypeVar("T", bound=Enum)


def validate_enum(enum_: Type[T], item: T | str) -> str:
    """
    Check whether the item is a valid option in enum_. If so, return the name of that option.
    Otherwise, raise an error.

    Parameters
    ----------
    enum_ : T
        An Enum where we expect the option value to be a str.
    item : T or str
        The item to be checked with enum_.

    Returns
    -------
    str
        The name of a valid enum option.
    """
    if isinstance(item, enum_):
        return item.name
    try:
        return getattr(enum_, item).name  # type: ignore
    except (TypeError, AttributeError) as err:
        raise QctrlArgumentsValueError(
            "Only the following options are allowed: " f"{list(enum_.__members__)} ",
            arguments={"item": item},
        ) from err


def _is_integer(val):
    return isinstance(val, ScalarDType.INT.value.types)


def _is_real(val):
    return _is_integer(val) or isinstance(val, ScalarDType.REAL.value.types)


def _is_complex(val):
    return _is_real(val) or isinstance(val, ScalarDType.COMPLEX.value.types)


def _is_number(val):
    return _is_real(val) or _is_complex(val)


def _number_converter(val):
    if _is_integer(val):
        return int(val)
    if _is_real(val):
        return float(val)
    return complex(val)


# types: supported types defined by Python and Numpy for a given dtype
# checker: a callable to check the input scalar
# converter: a callable to convert the scalar to the corresponding Python primitive type
_ScalarDTypeValidator = namedtuple(
    "_ScalarDTypeValidator", ["types", "checker", "converter"]
)

_SCALAR = TypeVar(
    "_SCALAR", bound=Union[int, float, complex, np.integer, np.float_, np.complex_]
)


class ScalarDType(Enum):
    """
    Store dtypes to validate both Python and NumPy types.
    """

    INT = _ScalarDTypeValidator((int, np.integer), _is_integer, int)
    REAL = _ScalarDTypeValidator((float, np.float_), _is_real, float)
    COMPLEX = _ScalarDTypeValidator((complex, np.complex_), _is_complex, complex)
    NUMBER = _ScalarDTypeValidator(None, _is_number, _number_converter)

    def __call__(
        self,
        value: _SCALAR,
        name: str,
        min_: Optional[Any] = None,
        max_: Optional[Any] = None,
        min_inclusive: bool = False,
        max_inclusive: bool = False,
    ) -> _SCALAR:
        """
        Validate a given scalar by the dtype.
        If valid, return the value as a primitive Python numeric type.
        """
        check_argument(
            self.value.checker(value),
            f"The {name} must be a {self.name.lower()}.",
            {name: value},
        )

        if min_ is not None:
            check_argument(
                value > min_ or (min_inclusive and value == min_),
                f"The {name} must be greater than {'or equal to' if min_inclusive  else ''} "
                f"{min_}.",
                {name: value},
            )
        if max_ is not None:
            check_argument(
                value < max_ or (max_inclusive and value == max_),
                f"The {name} must be smaller than {'or equal to' if max_inclusive  else ''} "
                f"{max_}.",
                {name: value},
            )
        return self.value.converter(value)


# valid_dtype_kinds: valid values for the array's dtype.kind.
# dtype: data type of the returned validated NumPy array
_ArrayDTypeValidator = namedtuple(
    "_ArrayDTypeValidator", ["valid_dtype_kinds", "dtype"]
)


class ArrayDType(Enum):
    """
    Store dtypes to validate array-likes.
    """

    INT = _ArrayDTypeValidator("iu", np.integer)
    REAL = _ArrayDTypeValidator("iuf", np.float_)
    COMPLEX = _ArrayDTypeValidator("iufc", np.complex_)

    def __call__(
        self,
        value: Any,
        name: str,
        ndim: Optional[int] = None,
        shape: Optional[tuple] = None,
        min_: Optional[Any] = None,
        max_: Optional[Any] = None,
        min_inclusive: bool = False,
        max_inclusive: bool = False,
    ) -> np.ndarray:
        """
        Validate a given array-like by the dtype.
        If valid, return the value as a NumPy array with the corresponding dtype.
        """
        array_val = np.asarray(value)

        check_argument(
            array_val.dtype.kind in self.value.valid_dtype_kinds,
            f"The {name} must be a {self.name.lower()} array.",
            {name: value},
        )

        if ndim is not None:
            check_argument(
                array_val.ndim == ndim,
                f"The {name} must be a {ndim}D array.",
                {name: value},
            )
        if shape is not None:
            check_argument(
                array_val.shape == shape,
                f"The {name} must be an array with shape {shape}.",
                {name: value},
            )

        if min_ is not None:
            check_argument(
                np.all(array_val > min_)
                or (min_inclusive and np.all(array_val >= min_)),
                f"The values in the {name} must be greater than "
                f"{'or equal to' if min_inclusive  else ''} {min_}.",
                {name: value},
            )
        if max_ is not None:
            check_argument(
                np.all(array_val < max_)
                or (max_inclusive and np.all(array_val <= max_)),
                f"The values in the {name} must be smaller than "
                f"{'or equal to' if max_inclusive  else ''} {max_}.",
                {name: value},
            )
        # Special handler for int typed array to address the signed and unsigned cases.
        # That is, we preserve the integer dtype from users.
        if self is ArrayDType.INT and array_val.dtype.kind in "iu":
            return array_val
        try:
            return array_val.astype(self.value.dtype, casting="safe")
        except TypeError as err:
            raise QctrlArgumentsValueError(
                f"Expected {name} as an array of {self.name.lower()} dtype, "
                f"but got {array_val.dtype}.",
                {name: value},
            ) from err


_VAL = TypeVar("_VAL")
P = ParamSpec("P")


def nullable(
    validator: Callable[Concatenate[_VAL, P], _VAL],
    value: Optional[_VAL],
    *args: P.args,
    **kwargs: P.kwargs,
) -> Optional[_VAL]:
    """
    Validate a parameter that can be None.

    When the parameter holds a non-null value, the validator callable is used to check the value.
    The validator takes the value as the first argument and some other options as defined by P, it
    returns the same type as the input value (strictly speaking, the returned type is something
    that can be converted from the input one. But in reality, we expect  we expect them to be
    interchangeable). The P annotation here allows mypy to also check the types for the
    resting arguments of the validator.
    """
    if value is None:
        return value
    return validator(value, *args, **kwargs)
