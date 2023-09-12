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

from typing import Optional

import numpy as np
from qctrlcommons.preconditions import check_argument

from boulderopal._validation import (
    ArrayDType,
    ScalarDType,
    nullable,
)
from boulderopal.graph import (
    Graph,
    execute_graph,
)
from boulderopal.ions._drives import (
    Drive,
    OptimizableDrive,
)
from boulderopal.optimization import run_optimization


def _validate_system_parameters(
    lamb_dicke_parameters: np.ndarray,
    relative_detunings: np.ndarray,
    target_phases: Optional[np.ndarray],
) -> int:
    """
    Validate the arrays describing an ion system
    and return the number of ions.
    """

    ion_count = lamb_dicke_parameters.shape[-1]

    check_argument(
        lamb_dicke_parameters.shape == (3, ion_count, ion_count)
        and relative_detunings.shape == (3, ion_count),
        "The shape of the Lamb–Dicke parameters array must be (3, N, N), "
        "and the shape of the relative detunings array must be (3, N), "
        "where N is the number of ions.",
        {
            "lamb_dicke_parameters": lamb_dicke_parameters,
            "relative_detunings": relative_detunings,
        },
        extras={
            "lamb_dicke_parameters.shape": lamb_dicke_parameters.shape,
            "relative_detunings.shape": relative_detunings.shape,
        },
    )

    if target_phases is not None:
        check_argument(
            target_phases.shape == (ion_count, ion_count),
            "The shape of the target phases array must be (N, N), "
            "where N is the number of ions.",
            {"target_phases": target_phases},
            extras={"ion count": ion_count, "target_phases.shape": target_phases.shape},
        )

    return ion_count


def _check_drives_addressing(drives, ion_count):
    """
    Check the input drives are a list and that the ions they address are valid.
    """

    check_argument(
        isinstance(drives, list),
        "You must provide a list of drives.",
        {"drives": drives},
    )

    all_addressing = []
    for idx, drive in enumerate(drives):
        check_argument(
            all(0 <= ion < ion_count for ion in drive.addressing),
            "The addressed ions must be between 0 (inclusive) "
            "and the number of ions (exclusive).",
            {"drives": drives},
            extras={
                f"drives[{idx}].addressing": drive.addressing,
                "ion count": ion_count,
            },
        )
        all_addressing += drive.addressing

    check_argument(
        len(all_addressing) == len(set(all_addressing)),
        "Each ion can only be addressed by a single drive.",
        {"drives": drives},
    )


def _get_ion_drives(pwc_addressing_pairs, ion_count, graph, duration):
    """
    From a list of (Pwc, list(int)) tuples (drives and ions addressed by them),
    return a list of length ion_count the drive addressing each ion
    or a PWC with value 0 if the ion is not addressed by any drive.
    """
    ion_drives = []
    for idx in range(ion_count):
        for pwc, addressing in pwc_addressing_pairs:
            # Add the first drive that addresses the ion as we assume
            # each ion can only be addressed by a single drive.
            if idx in addressing:
                ion_drives.append(pwc)
                break
        else:
            ion_drives.append(graph.constant_pwc(constant=0.0, duration=duration))

    return ion_drives


_MS_NODE_NAMES = ["sample_times", "phases", "displacements", "infidelities"]


def ms_simulate(
    drives: list[Drive],
    duration: float,
    lamb_dicke_parameters: np.ndarray,
    relative_detunings: np.ndarray,
    target_phases: Optional[np.ndarray] = None,
    sample_count: int = 128,
) -> dict:
    r"""
    Simulate a Mølmer–Sørensen-type operation on a system composed of ions.

    This function builds a graph describing the Mølmer–Sørensen operation
    and calls boulderopal.execute_graph to simulate the ion dynamics.

    Parameters
    ----------
    drives : list[~ions.Drive]
        A list of drives addressing the ions.
        Each ion can only be addressed by a single drive,
        but there may be ions not addressed by any drive.
    duration : float
        The duration, in seconds, of the dynamics to be simulated, :math:`T`.
        It must be greater than zero.
    lamb_dicke_parameters : np.ndarray
        A 3D array of shape ``(3, N, N)``, where :math:`N` is the number of
        ions in the system, specifying the laser-ion coupling strength,
        :math:`\{\eta_{jkl}\}`. The three dimensions indicate, respectively,
        the axis, the collective mode number, and the ion.
    relative_detunings : np.ndarray
        A 2D array of shape ``(3, N)`` specifying the difference, in Hz, between
        each motional mode frequency and the laser detuning
        (with respect to the qubit transition frequency :math:`\omega_0`),
        :math:`\{\delta_{jk} = \nu_{jk} - \delta\}`. The two dimensions indicate,
        respectively, the axis and the collective mode number.
    target_phases : np.ndarray or None, optional
        A 2D array of shape ``(N, N)`` with the target relative phases between
        ion pairs, :math:`\{\Psi_{kl}\}`, as a strictly lower triangular matrix.
        Its :math:`(k, l)`-th element indicates the total relative phase target
        for ions :math:`k` and :math:`l`, with :math:`k > l`.
        If not provided, the function does not return the operational infidelities.
    sample_count : int, optional
        The number of times :math:`T` between 0 and `duration` (included)
        at which the evolution is sampled.
        Defaults to 128.

    Returns
    -------
    dict
        The result of the `execute_graph` call.
        Its ``output`` item is a dictionary containing information about
        the evolution of the system, with the following keys:

            ``sample_times``
                The times at which the evolution is sampled, as an array of shape ``(T,)``.
            ``phases``
                Acquired phases :math:`\{\Phi_{jk}(t_i) = \phi_{jk}(t_i) + \phi_{kj}(t_i)\}`
                for each sample time and for all ion pairs, as a strictly lower triangular
                matrix of shape ``(T, N, N)``.
                :math:`\Phi_{jk}` records the relative phase between ions :math:`j`
                and :math:`k`; matrix elements where :math:`j \leq k` are zero.
            ``displacements``
                Displacements :math:`\{\eta_{pj}\alpha_{pj}(t_i)\}` for all mode-ion
                combinations, as an array of shape ``(T, 3, N, N)``.
                The four dimensions indicate the sample time, the axis,
                the collective mode number, and the ion.
            ``infidelities``
                A 1D array of length ``T`` representing the operational infidelities of
                the Mølmer–Sørensen gate at each sample time, :math:`\mathcal{I}(t_i)`.
                Only returned if target relative phases are provided.

    See Also
    --------
    boulderopal.ions.Drive :
        Class describing non-optimizable drives.
    boulderopal.ions.ms_optimize :
        Find optimal pulses to perform Mølmer–Sørensen-type operations on trapped ions systems.
    boulderopal.ions.obtain_ion_chain_properties :
        Calculate the properties of an ion chain.

    Notes
    -----
    The internal and motional Hamiltonian of :math:`N` ions is

    .. math::
        H_0 = \sum_{p = 1}^{3N} \hbar\nu_p \left(a_p^\dagger a_p + \frac{1}{2}\right)
            + \sum_{j = 1}^N \frac{\hbar \omega_0}{2} \sigma_{z,j} ,

    where the axis dimension and collective mode dimension are combined into a single index
    :math:`p` for simplicity, :math:`a_p` is the annihilation operator for the mode :math:`p`,
    and :math:`\sigma_{z,j}` is the Pauli :math:`Z` operator for the ion :math:`j`.
    The interaction Hamiltonian for Mølmer–Sørensen-type
    operations in the rotating frame with respect to :math:`H_0` is:

    .. math::
        H_I(t) = i\hbar\sum_{j = 1}^N \sigma_{x, j} \sum_{p = 1}^{3N} (-\beta_{pj}^*(t)a_p +
                \beta_{pj}(t) a_p^\dagger) ,

    where :math:`\sigma_{x, j}` is the Pauli :math:`X` operator for the ion :math:`j` and
    :math:`\beta_{pj}(t) = \eta_{pj} \frac{\gamma_j(t)}{2} e^{i\delta_p t}`,
    indicating the coupling of the ion :math:`j` to the motional mode :math:`p`,
    where :math:`\{\gamma_j\}` is the total drive acting on ion :math:`j`.

    The corresponding unitary operation is given by [1]_

    .. math::
        U(t) = \exp\left[ \sum_{j=1}^N \sigma_{x, j} B_j(t)
                + i\sum_{j=1}^N\sum_{k=1}^{j - 1} (\phi_{jk}(t) + \phi_{kj}(t))
                \sigma_{x, j} \sigma_{x, k} \right] ,

    where

    .. math::
        B_j(t) &\equiv \sum_{p = 1}^{3N}  \left(\eta_{pj}\alpha_{pj}(t)a_p^\dagger
            - \eta_{pj}^{\ast}\alpha_{pj}^\ast(t)a_p \right) ,

        \phi_{jk}(t) &\equiv \mathrm{Im} \left[ \sum_{p=1}^{3N} \int_{0}^{t} d \tau_1
            \int_{0}^{\tau_1} d \tau_2 \beta_{pj}(\tau_1)\beta_{pk}^{\ast}(\tau_2) \right] ,

    and

    .. math::
        \alpha_{pj}(t) = \int_0^t d\tau \frac{\gamma_j(\tau)}{2} e^{i \delta_p \tau} .

    The operational infidelity of the Mølmer–Sørensen gate is defined as [1]_:

    .. math::
        \mathcal{I} = 1 - \left| \left( \prod_{\substack{k=1 \\ l<k}}^N \cos (
            \phi_{kl} - \psi_{kl}) \right)
            \left( 1 - \sum_{j=1}^3 \sum_{k,l=1}^N \left[ |\eta_{jkl}|^2
            |\alpha_{jkl}|^2 \left(\bar{n}_{jk}+\frac{1}{2} \right) \right] \right) \right|^2 .

    References
    ----------
    .. [1] `C. D. B. Bentley, H. Ball, M. J. Biercuk, A. R. R. Carvalho,
            M. R. Hush, and H. J. Slatyer, Advanced Quantum Technologies 3, 2000044 (2020).
            <https://doi.org/10.1002/qute.202000044>`_
    """

    duration = ScalarDType.REAL(duration, "duration", min_=0)

    lamb_dicke_parameters = ArrayDType.REAL(
        lamb_dicke_parameters, "lamb_dicke_parameters", ndim=3
    )
    relative_detunings = ArrayDType.REAL(
        relative_detunings, "relative_detunings", ndim=2
    )
    target_phases = nullable(ArrayDType.REAL, target_phases, "target_phases", ndim=2)
    ion_count = _validate_system_parameters(
        lamb_dicke_parameters, relative_detunings, target_phases
    )

    check_argument(
        all(isinstance(drive, Drive) for drive in drives),
        "All drives must be non-optimizable.",
        {"drives": drives},
    )

    _check_drives_addressing(drives, ion_count)

    graph = Graph()

    drive_pwcs = [
        (drive.get_pwc(graph, duration), drive.addressing) for drive in drives
    ]
    ion_drives = _get_ion_drives(drive_pwcs, ion_count, graph, duration)

    sample_times = np.linspace(0.0, duration, sample_count)
    graph.tensor(sample_times, name="sample_times")

    phases = graph.ions.ms_phases(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
        name=_MS_NODE_NAMES[1],
    )

    displacements = graph.ions.ms_displacements(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
        name=_MS_NODE_NAMES[2],
    )

    if target_phases is not None:
        graph.ions.ms_infidelity(
            phases=phases,
            displacements=displacements,
            target_phases=target_phases,
            name=_MS_NODE_NAMES[3],
        )
        output_node_names = _MS_NODE_NAMES
    else:
        output_node_names = _MS_NODE_NAMES[:3]

    return execute_graph(graph=graph, output_node_names=output_node_names)


def ms_optimize(
    drives: list[OptimizableDrive],
    duration: float,
    lamb_dicke_parameters: np.ndarray,
    relative_detunings: np.ndarray,
    target_phases: np.ndarray,
    sample_count: int = 128,
    robust: bool = False,
    **optimization_kwargs,
) -> dict:
    r"""
    Find optimal pulses to perform a target Mølmer–Sørensen-type operation
    on a system composed of ions.

    This function builds a graph describing the Mølmer–Sørensen operation
    and calls boulderopal.run_optimization to minimize the target cost.

    Parameters
    ----------
    drives : list[OptimizableDrive]
        A list of optimizable drives addressing the ions.
        Each ion can only be addressed by a single drive,
        but there may be ions not addressed by any drive.
    duration : float
        The duration, in seconds, of the dynamics to be optimized, :math:`T`.
        It must be greater than zero.
    lamb_dicke_parameters : np.ndarray
        A 3D array of shape ``(3, N, N)``, where :math:`N` is the number of
        ions in the system, specifying the laser-ion coupling strength,
        :math:`\{\eta_{jkl}\}`. The three dimensions indicate, respectively,
        the axis, the collective mode number, and the ion.
    relative_detunings : np.ndarray
        A 2D array of shape ``(3, N)`` specifying the difference, in Hz, between
        each motional mode frequency and the laser detuning
        (with respect to the qubit transition frequency :math:`\omega_0`),
        :math:`\{\delta_{jk} = \nu_{jk} - \delta\}`. The two dimensions indicate,
        respectively, the axis and the collective mode number.
    target_phases : np.ndarray
        A 2D array of shape ``(N, N)`` with the target relative phases between
        ion pairs, :math:`\{\Psi_{kl}\}`, as a strictly lower triangular matrix.
        Its :math:`(k, l)`-th element indicates the total relative phase target
        for ions :math:`k` and :math:`l`, with :math:`k > l`.
    sample_count : int, optional
        The number of times :math:`T` between 0 and `duration` (both included)
        at which the evolution is sampled.
        Defaults to 128.
    robust : bool, optional
        If set to False, the cost corresponds to the infidelity at the end of the gate.
        If set to True, the cost is the final infidelity plus a dephasing-robust cost term.
        Defaults to False.
    **optimization_kwargs
        Additional parameters to pass to boulderopal.run_optimization.

    Returns
    -------
    dict
        The result of the `run_optimization` call.
        Its ``output`` item is a dictionary containing information about
        the optimized drive and the evolution of the system, with the following keys:

            optimized drives
                The piecewise-constant optimized drives implementing the gate.
                The keys are the names of the `drives` provided to the function.
            ``sample_times``
                The times at which the evolution is sampled, as an array of shape ``(T,)``.
            ``phases``
                Acquired phases :math:`\{\Phi_{jk}(t_i) = \phi_{jk}(t_i) + \phi_{kj}(t_i)\}`
                for each sample time and for all ion pairs, as a strictly lower triangular
                matrix of shape ``(T, N, N)``.
                :math:`\Phi_{jk}` records the relative phase between ions :math:`j`
                and :math:`k`; matrix elements where :math:`j \leq k` are zero.
            ``displacements``
                Displacements :math:`\{\eta_{pj}\alpha_{pj}(t_i)\}` for all mode-ion
                combinations, as an array of shape ``(T, 3, N, N)``.
                The four dimensions indicate the sample time, the axis,
                the collective mode number, and the ion.
            ``infidelities``
                A 1D array of length ``T`` representing the operational infidelities of
                the Mølmer–Sørensen gate at each sample time, :math:`\mathcal{I}(t_i)`.

    See Also
    --------
    boulderopal.ions.ComplexOptimizableDrive :
        Class describing a piecewise-constant complex-valued optimizable drive.
    boulderopal.ions.RealOptimizableDrive :
        Class describing a piecewise-constant real-valued optimizable drive.
    boulderopal.ions.ms_simulate :
        Simulate a Mølmer–Sørensen-type operation on a trapped ions system.
    boulderopal.ions.obtain_ion_chain_properties :
        Calculate the properties of an ion chain.

    Notes
    -----
    The internal and motional Hamiltonian of :math:`N` ions is

    .. math::
        H_0 = \sum_{p = 1}^{3N} \hbar\nu_p \left(a_p^\dagger a_p + \frac{1}{2}\right)
            + \sum_{j = 1}^N \frac{\hbar \omega_0}{2} \sigma_{z,j} ,

    where the axis dimension and collective mode dimension are combined into a single index
    :math:`p` for simplicity, :math:`a_p` is the annihilation operator for the mode :math:`p`,
    and :math:`\sigma_{z,j}` is the Pauli :math:`Z` operator for the ion :math:`j`.
    The interaction Hamiltonian for Mølmer–Sørensen-type
    operations in the rotating frame with respect to :math:`H_0` is:

    .. math::
        H_I(t) = i\hbar\sum_{j = 1}^N \sigma_{x, j} \sum_{p = 1}^{3N} (-\beta_{pj}^*(t)a_p +
                \beta_{pj}(t) a_p^\dagger) ,

    where :math:`\sigma_{x, j}` is the Pauli :math:`X` operator for the ion :math:`j` and
    :math:`\beta_{pj}(t) = \eta_{pj} \frac{\gamma_j(t)}{2} e^{i\delta_p t}`,
    indicating the coupling of the ion :math:`j` to the motional mode :math:`p`,
    where :math:`\{\gamma_j\}` is the total drive acting on ion :math:`j`.

    The corresponding unitary operation is given by [1]_

    .. math::
        U(t) = \exp\left[ \sum_{j=1}^N \sigma_{x, j} B_j(t)
                + i\sum_{j=1}^N\sum_{k=1}^{j - 1} (\phi_{jk}(t) + \phi_{kj}(t))
                \sigma_{x, j} \sigma_{x, k} \right] ,

    where

    .. math::
        B_j(t) &\equiv \sum_{p = 1}^{3N}  \left(\eta_{pj}\alpha_{pj}(t)a_p^\dagger
            - \eta_{pj}^{\ast}\alpha_{pj}^\ast(t)a_p \right) ,

        \phi_{jk}(t) &\equiv \mathrm{Im} \left[ \sum_{p=1}^{3N} \int_{0}^{t} d \tau_1
            \int_{0}^{\tau_1} d \tau_2 \beta_{pj}(\tau_1)\beta_{pk}^{\ast}(\tau_2) \right] ,

    and

    .. math::
        \alpha_{pj}(t) = \int_0^t d\tau \frac{\gamma_j(\tau)}{2} e^{i \delta_p \tau} .

    The operational infidelity of the Mølmer–Sørensen gate is defined as [1]_:

    .. math::
        \mathcal{I} = 1 - \left| \left( \prod_{\substack{k=1 \\ l<k}}^N \cos (
            \phi_{kl} - \psi_{kl}) \right)
            \left( 1 - \sum_{j=1}^3 \sum_{k,l=1}^N \left[ |\eta_{jkl}|^2
            |\alpha_{jkl}|^2 \left(\bar{n}_{jk}+\frac{1}{2} \right) \right] \right) \right|^2 .

    You can use the `robust` flag to construct a Mølmer–Sørensen gate that is
    robust against dephasing noise. This imposes a symmetry [1]_ in the optimizable
    ion drives and aims to minimize the time-averaged positions of the phase-space
    trajectories,

    .. math::
        \langle \alpha_{pj} \rangle
            = \frac{1}{t_\text{gate}} \int_0^{t_\text{gate}}
                \alpha_{pj}(t) \mathrm{d} t ,

    where the axis dimension and the collective mode dimension are combined
    into a single index :math:`p` for simplicity.

    This is achieved by adding an additional term to the cost function,
    consisting of the sum of the square moduli of the time-averaged positions
    multiplied by the corresponding Lamb–Dicke parameters. That is to say,

    .. math::
        C_\text{robust} =
            \mathcal{I} + \sum_{p,j}
                \left| \eta_{pj} \langle \alpha_{pj} \rangle \right|^2 .

    References
    ----------
    .. [1] `C. D. B. Bentley, H. Ball, M. J. Biercuk, A. R. R. Carvalho,
            M. R. Hush, and H. J. Slatyer, Advanced Quantum Technologies 3, 2000044 (2020).
            <https://doi.org/10.1002/qute.202000044>`_
    """

    duration = ScalarDType.REAL(duration, "duration", min_=0)

    lamb_dicke_parameters = ArrayDType.REAL(
        lamb_dicke_parameters, "lamb_dicke_parameters", ndim=3
    )
    relative_detunings = ArrayDType.REAL(
        relative_detunings, "relative_detunings", ndim=2
    )
    target_phases = ArrayDType.REAL(target_phases, "target_phases", ndim=2)
    ion_count = _validate_system_parameters(
        lamb_dicke_parameters, relative_detunings, target_phases
    )

    check_argument(
        all(isinstance(drive, OptimizableDrive) for drive in drives),
        "All drives must be optimizable.",
        {"drives": drives},
    )

    _check_drives_addressing(drives, ion_count)

    drive_names = [drive.name for drive in drives]

    check_argument(
        len(drive_names) == len(set(drive_names)),
        "The drive names must be unique.",
        {"drives": drives},
        extras={"[drive.name for drive in drives]": drive_names},
    )

    graph = Graph()

    drive_pwcs = [
        (drive.get_pwc(graph, duration, robust), drive.addressing) for drive in drives
    ]
    ion_drives = _get_ion_drives(drive_pwcs, ion_count, graph, duration)

    sample_times = np.linspace(0.0, duration, sample_count)
    graph.tensor(sample_times, name="sample_times")

    phases = graph.ions.ms_phases(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
        name=_MS_NODE_NAMES[1],
    )

    displacements = graph.ions.ms_displacements(
        drives=ion_drives,
        lamb_dicke_parameters=lamb_dicke_parameters,
        relative_detunings=relative_detunings,
        sample_times=sample_times,
        name=_MS_NODE_NAMES[2],
    )

    infidelities = graph.ions.ms_infidelity(
        phases=phases,
        displacements=displacements,
        target_phases=target_phases,
        name=_MS_NODE_NAMES[3],
    )

    cost = infidelities[-1]
    if robust:
        cost += graph.ions.ms_dephasing_robust_cost(
            drives=ion_drives,
            lamb_dicke_parameters=lamb_dicke_parameters,
            relative_detunings=relative_detunings,
        )

    return run_optimization(
        graph=graph,
        cost_node_name=cost.name,
        output_node_names=drive_names + _MS_NODE_NAMES,
        **optimization_kwargs,
    )
