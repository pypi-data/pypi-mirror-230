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
from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

import numpy as np
from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlcommons.graph import Graph
from qctrlcommons.node.node_data import Pwc
from qctrlcommons.preconditions import check_argument

from boulderopal._validation import (
    ArrayDType,
    ScalarDType,
)


def _validate_addressing(addressing):
    """
    Validate an addressing input and return it as a tuple.
    """
    message = "The ions addressed must be an integer or a tuple of integers."
    try:
        check_argument(
            all(isinstance(ion, (int, np.integer)) for ion in addressing),
            message,
            {"addressing": addressing},
        )

    except TypeError as error:
        if isinstance(addressing, (int, np.integer)):
            return (addressing,)

        raise QctrlArgumentsValueError(message, {"addressing": addressing}) from error

    addressing = tuple(int(k) for k in addressing)
    check_argument(
        len(addressing) == len(set(addressing)),
        "The ions addressed must be unique.",
        {"addressing": addressing},
    )
    return addressing


@dataclass
class Drive:
    """
    A piecewise-constant complex-valued drive.

    Parameters
    ----------
    values : np.ndarray
        The values of the drive at each segment, in units of rad/s.
    addressing : int or tuple[int, ...]
        The indices of the ions addressed by the drive.

    See Also
    --------
    boulderopal.ions.OptimizableDrive :
        Abstract class describing a piecewise-constant optimizable drive.
    boulderopal.ions.ms_simulate :
        Simulate a Mølmer–Sørensen-type operation on a trapped ions system.
    """

    values: np.ndarray
    addressing: int | tuple[int, ...]

    def __post_init__(self):
        self.values = ArrayDType.COMPLEX(self.values, "values", ndim=1)
        self.addressing = _validate_addressing(self.addressing)

    def get_pwc(self, graph: Graph, duration: float) -> Pwc:
        """
        Return a Pwc representation of the drive.
        """
        return graph.pwc_signal(values=self.values, duration=duration)


class OptimizableDrive(ABC):
    """
    Abstract class for optimizable drives. You need to call the concrete classes below
    to create optimizable drives.

    See Also
    --------
    boulderopal.ions.ComplexOptimizableDrive :
        Class describing a piecewise-constant complex-valued optimizable drive.
    boulderopal.ions.RealOptimizableDrive :
        Class describing a piecewise-constant real-valued optimizable drive.
    boulderopal.ions.ms_optimize :
       Find optimal pulses to perform Mølmer–Sørensen-type operations on trapped ions systems.
    """

    name: str
    addressing: int | tuple[int, ...]

    @abstractmethod
    def get_pwc(self, graph: Graph, duration: float, robust: bool) -> Pwc:
        """
        Return a Pwc representation of the optimizable drive.
        """
        raise NotImplementedError


@dataclass
class ComplexOptimizableDrive(OptimizableDrive):
    """
    A piecewise-constant complex-valued optimizable drive.
    The main function will try to find the optimal values for it.

    Parameters
    ----------
    count : int
        The number of segments in the piecewise-constant drive.
    maximum_rabi_rate : float
        The maximum value that the modulus of the drive can take at each segment,
        in units of rad/s.
    addressing : int or tuple[int, ...]
        The indices of the ions addressed by the drive.
    name : str, optional
        The identifier of the drive.
        Defaults to "drive".

    See Also
    --------
    boulderopal.ions.Drive : Class describing non-optimizable drives.
    boulderopal.ions.RealOptimizableDrive : Class describing optimizable real-valued drives.
    boulderopal.ions.ms_optimize :
        Find optimal pulses to perform Mølmer–Sørensen-type operations on trapped ions systems.
    """

    count: int
    maximum_rabi_rate: float
    addressing: int | tuple[int, ...]
    name: str = "drive"

    def __post_init__(self):
        self.count = ScalarDType.INT(self.count, "count", min_=0)
        self.maximum_rabi_rate = ScalarDType.REAL(
            self.maximum_rabi_rate, "maximum_rabi_rate", min_=0
        )
        self.addressing = _validate_addressing(self.addressing)

    def get_pwc(self, graph: Graph, duration: float, robust: bool) -> Pwc:
        if not robust:
            return graph.complex_optimizable_pwc_signal(
                segment_count=self.count,
                duration=duration,
                maximum=self.maximum_rabi_rate,
                name=self.name,
            )

        # Create a symmetrized drive signal (Milne et al., Phys. Rev. Applied, 2020).
        free_segment_count = (self.count + 1) // 2
        moduli = graph.optimization_variable(
            count=free_segment_count, lower_bound=0, upper_bound=self.maximum_rabi_rate
        )
        phases = graph.optimization_variable(
            count=free_segment_count,
            lower_bound=0,
            upper_bound=2 * np.pi,
            is_lower_unbounded=True,
            is_upper_unbounded=True,
        )

        if self.count % 2 == 0:
            moduli_reversed = graph.reverse(moduli, [0])
            phases_reversed = graph.reverse(phases, [0])

        else:
            moduli_reversed = graph.reverse(moduli[:-1], [0])
            phases_reversed = graph.reverse(phases[:-1], [0])

        return graph.complex_pwc_signal(
            moduli=graph.concatenate([moduli, moduli_reversed], 0),
            phases=graph.concatenate([phases, 2 * phases[-1] - phases_reversed], 0),
            duration=duration,
            name=self.name,
        )


@dataclass
class RealOptimizableDrive(OptimizableDrive):
    """
    A piecewise-constant real-valued optimizable drive.
    The main function will try to find the optimal values for it.

    Parameters
    ----------
    count : int
        The number of segments in the piecewise-constant drive.
    minimum_rabi_rate : float
        The minimum value that the drive can take at each segment, in units of rad/s.
    maximum_rabi_rate : float
        The maximum value that the drive can take at each segment, in units of rad/s.
    addressing : int or tuple[int, ...]
        The indices of the ions addressed by the drive.
    name : str, optional
        The identifier of the drive.
        Defaults to "drive".

    See Also
    --------
    boulderopal.ions.ComplexOptimizableDrive : Class describing optimizable complex-valued drives.
    boulderopal.ions.Drive : Class describing non-optimizable drives.
    boulderopal.ions.ms_optimize :
        Find optimal pulses to perform Mølmer–Sørensen-type operations on trapped ions systems.
    """

    count: int
    minimum_rabi_rate: float
    maximum_rabi_rate: float
    addressing: int | tuple[int, ...]
    name: str = "drive"

    def __post_init__(self):
        self.count = ScalarDType.INT(self.count, "count", min_=0)
        self.minimum_rabi_rate = ScalarDType.REAL(
            self.minimum_rabi_rate, "minimum_rabi_rate"
        )
        self.maximum_rabi_rate = ScalarDType.REAL(
            self.maximum_rabi_rate, "maximum_rabi_rate"
        )
        check_argument(
            self.minimum_rabi_rate < self.maximum_rabi_rate,
            "The maximum Rabi rate must be larger than the minimum.",
            {
                "minimum_rabi_rate": self.minimum_rabi_rate,
                "maximum_rabi_rate": self.maximum_rabi_rate,
            },
        )
        self.addressing = _validate_addressing(self.addressing)

    def get_pwc(self, graph: Graph, duration: float, robust: bool) -> Pwc:
        if not robust:
            return graph.real_optimizable_pwc_signal(
                segment_count=self.count,
                duration=duration,
                maximum=self.maximum_rabi_rate,
                minimum=self.minimum_rabi_rate,
                name=self.name,
            )

        # Create a symmetrized drive signal (Milne et al., Phys. Rev. Applied, 2020).
        free_segment_count = (self.count + 1) // 2
        values = graph.optimization_variable(
            count=free_segment_count,
            lower_bound=self.minimum_rabi_rate,
            upper_bound=self.maximum_rabi_rate,
        )

        if self.count % 2 == 0:
            values_reversed = graph.reverse(values, [0])

        else:
            values_reversed = graph.reverse(values[:-1], [0])

        return graph.pwc_signal(
            values=graph.concatenate([values, values_reversed], 0),
            duration=duration,
            name=self.name,
        )
