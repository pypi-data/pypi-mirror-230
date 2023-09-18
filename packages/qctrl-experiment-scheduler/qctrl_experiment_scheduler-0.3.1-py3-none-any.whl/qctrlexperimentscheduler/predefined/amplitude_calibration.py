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
Module for building the predefined graph for amplitude calibration.
"""

from __future__ import annotations

from functools import partial
from typing import (
    Callable,
    Optional,
)

import numpy as np
from qctrl import Qctrl
from qctrlcommons.graph import Graph
from qctrlcommons.node.node_data import Tensor

from qctrlexperimentscheduler import (
    CalibrationGraph,
    CalibrationStatus,
    Variable,
)


class AmplitudeCalibrationBackend:
    r"""
    An abstract class for the backends where you can use the predefined
    amplitude calibration graph.

    Backends are interfaces with either external hardware like IBM-Q or
    Rigetti, or a simulator that uses Boulder Opal. The constructor of
    the backend can take all the parameters that are exclusive for a
    certain interface. For example, an IBM-Q backend can take the user's
    IBM credentials, while a simulation backend will include the Boulder
    Opal session and parameters like the amount of noise to be simulated.

    The methods of this class contain all the operations that an
    amplitude calibration requires. Specifically, it needs the capability
    of performing three kinds of experiments:

    1. A repetition of N :math:`\pi`-pulses followed by a measurement.
    2. A repetition of N :math:`\pi/2`-pulses followed by a measurement.
    3. One :math:`\pi/2`-pulse followed by N :math:`\pi`-pulses and a measurement.

    Each of these functions should take the parameters of the Gaussian
    pulses used (amplitude and DRAG coefficient) as well as the number of
    repetitions N of each experiment. The result is then returned in the
    form of the fraction of the results in the state :math:`|1\rangle`.
    """

    def pi_pulse_experiment(
        self,
        amplitude: np.ndarray,
        drag: np.ndarray,
        repetition_count: int,
        shot_count: Optional[int] = None,
    ):
        r"""
        Run a series of :math:`\pi` pulses in the backend.

        This is an abstract method and should not be called directly.
        """
        raise NotImplementedError

    def pi_2_pulse_experiment(
        self,
        amplitude: np.ndarray,
        drag: np.ndarray,
        repetition_count: int,
        shot_count: Optional[int] = None,
    ):
        r"""
        Run a series of :math:`\pi/2` pulses in the backend.

        This is an abstract method and should not be called directly.
        """
        raise NotImplementedError

    def pi_2_and_pi_pulse_experiment(
        self,
        pi_2_pulse_amplitude: np.ndarray,
        pi_2_pulse_drag: np.ndarray,
        pi_pulse_amplitude: np.ndarray,
        pi_pulse_drag: np.ndarray,
        repetition_count: int,
        shot_count: Optional[int] = None,
    ):
        r"""
        Run a :math:`\pi/2` pulse followed by a series of :math:`\pi` pulses in the backend.

        This is an abstract method and should not be called directly.
        """
        raise NotImplementedError


def _fit_parameters(
    session: Qctrl,
    variables: list[Variable],
    y_data: np.ndarray,
    fit_function: Callable[[Graph, list[Tensor]], np.ndarray],
) -> list[np.ndarray]:
    """
    Auxiliary function for fitting points in a curve.

    The data analysis part of the calibration function needs to perform
    some curve fitting tasks to figure out the value of certain calibration
    variables.

    Parameters
    ----------
    session : Qctrl
        A session of Boulder Opal, whose optimizer will be used to
        perform some curve fitting.
    variables : list[Variable]
        The unknown variables that the curve fitting process seeks to
        determine.
    y_data : np.ndarray
        The 1D array of data corresponding to the points returned by
        the experiments.
    fit_function : Callable
        The curve that we want to fit in the provided `y_data`. It should
        receive an instance of the Graph object, and a list of tensors
        that matches the length of `variables`. It should output a tensor
        that has the same shape as `y_data`.

    Returns
    -------
    list[np.ndarray]
        The best values of the `variables` to fit the `y_data` in the
        curve provided by `fit_function`.
    """
    graph = session.create_graph()

    optimization_variables = [
        variable.to_optimization_variable(graph=graph) for variable in variables
    ]

    graph.sum(
        (fit_function(graph, *optimization_variables) - y_data) ** 2,
        name="cost",
    )

    output_names = [variable.name for variable in optimization_variables]

    results = session.functions.calculate_optimization(
        graph=graph,
        cost_node_name="cost",
        output_node_names=output_names,
        optimization_count=4,
    )

    outputs = [np.asarray(results.output[name]["value"]) for name in output_names]

    return outputs


def _find_peak(
    session: Qctrl,
    x_data: np.ndarray,
    y_data: np.ndarray,
    current_estimate: np.ndarray,
) -> np.ndarray:
    """
    Run the data analysis to find the peak of the input data.

    This is used for coarse amplitude calibration.

    Parameters
    ----------
    session : Qctrl
        The Boulder Opal session that will run the curve fit.
    x_data : np.ndarray
        The values of the points in the x axis.
    y_data : np.ndarray
        The values of the points in the y axis.
    current_estimate : np.ndarray
        The current estimate of the frequency. This is used as an initial
        guess for the curve fitting function.

    Returns
    -------
    np.ndarray
        The estimated peak of the function.
    """
    initial_value = np.pi / 2 / current_estimate

    # As the amplitude is normalized by the maximum Rabi rate, 1 is the
    # maximum amplitude and the peak is never further than 1.
    lower_bound = np.pi / 2

    # Don't look for frequencies that are faster than the sampling rate.
    upper_bound = 2 * np.pi / np.max(np.diff(x_data))

    frequency = Variable(
        initial_value=initial_value,
        upper_bound=upper_bound,
        lower_bound=lower_bound,
    )

    def _sine_oscillations(graph, frequency):
        return graph.sin(frequency * x_data) ** 2

    frequency_estimate = _fit_parameters(
        session=session,
        variables=[frequency],
        fit_function=_sine_oscillations,
        y_data=y_data,
    )[0]

    return np.pi / 2 / frequency_estimate


def _find_deviation_from_frequency(
    session: Qctrl,
    x_data: np.ndarray,
    y_data: np.ndarray,
    expected_frequency: float,
    uncertainty: float = 0.1,
    phase_offset: float = 0,
) -> np.ndarray:
    """
    Run the data analysis to find how much an oscillating function
    deviates from its expected frequency.

    This is used for fine amplitude calibration.

    Parameters
    ----------
    session : Qctrl
        The Boulder Opal session that will run the curve fit.
    x_data : np.ndarray
        The values of the points in the x axis.
    y_data : np.ndarray
        The values of the points in the y axis.
    expected_frequency : float
        The expected frequency of the oscillations. This value is used
        as the initial guess of the frequency variable in the curve fit.
        Note that typical applications of this function will have
        frequencies that are far from zero. Passing an expected frequency
        that is close to zero can cause numerical errors.
    uncertainty : float, optional
        The fractional amount of the `expected_frequency` that the fine
        calibration is allowed to change. Defaults to 0.1.
    phase_offset : float, optional
        The expected initial offset in the phase of square sine function
        when plotting the populations as a function of the repetitions.
        Typically this would be caused by extra gates added at the
        beginning of the sequence. A pi/2 pulse at the beginning of the
        sequence adds an offset of pi/4, for example. Defaults to 0,
        which is the case of a sequence with only the gates counted in
        the x_data.

    Returns
    -------
    np.ndarray
        The number that has to be multiplied by the frequency of the
        function for it to match the `expected_frequency`.
    """

    # As these are fine calibrations, assume that the correct value doesn't
    # differ too much from the current estimate.
    initial_value = np.array([expected_frequency])
    padding = expected_frequency * uncertainty
    frequency = Variable(
        initial_value=initial_value,
        upper_bound=expected_frequency + padding,
        lower_bound=expected_frequency - padding,
    )

    def _sine_oscillations(graph, frequency):
        return graph.sin(frequency * x_data + phase_offset) ** 2

    frequency_estimate = _fit_parameters(
        session=session,
        variables=[frequency],
        fit_function=_sine_oscillations,
        y_data=y_data,
    )[0]

    return expected_frequency / frequency_estimate


def coarse_calibration_function(
    calibration_graph: CalibrationGraph,
    backend: AmplitudeCalibrationBackend,
    session: Qctrl,
    point_count: int = 150,
) -> CalibrationStatus:
    """
    Perform the coarse amplitude calibration in the provided backend.

    It calls the backend function to run a series of experiments varying the
    amplitude of the Gaussian pulses. The amplitude value for which
    all the population is transferred to state 1 is considered the rough
    value of the pi pulse amplitude. Half of its value is the rough value
    of the pi/2 pulse amplitude.

    Data analysis is used to determine the point where the population
    peaks.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The calibration graph where this calibration process is being
        performed. It contains the variables that will be used and
        updated during the optimization.
    backend : AmplitudeCalibrationBackend
        A class containing all the communication necessary with an
        external or simulated hardware that will be calibrated.
    session : Qctrl
        The session of Boulder Opal used to perform the data analysis.
    point_count : int, optional
        The number of points collected by this experiment. All the points
        are linearly spaced and between 0 and the current estimate of the
        pi pulse amplitude. Defaults to 150.

    Returns
    -------
    CalibrationStatus
       Whether the calibration has succeeded.
    """
    pi_pulse_amplitude = calibration_graph.get_variable("pi_pulse_amplitude").get()

    amplitudes = np.linspace(0, 1, point_count + 1)[1:] * pi_pulse_amplitude[0]

    try:
        populations = backend.pi_pulse_experiment(
            amplitude=amplitudes,
            drag=np.array([0]),
            repetition_count=1,
        )
    except:  # pylint: disable=bare-except
        return CalibrationStatus.FAIL

    rough_amplitude_estimate = _find_peak(
        session=session,
        x_data=amplitudes,
        y_data=populations,
        current_estimate=pi_pulse_amplitude,
    )

    calibration_graph.get_variable("pi_pulse_amplitude").set(rough_amplitude_estimate)
    calibration_graph.get_variable("pi_2_pulse_amplitude").set(
        rough_amplitude_estimate / 2
    )

    return CalibrationStatus.PASS


def fine_pi_2_pulse_calibration_function(
    calibration_graph: CalibrationGraph,
    backend: AmplitudeCalibrationBackend,
    session: Qctrl,
    point_count: int = 14,
) -> CalibrationStatus:
    """
    Perform the fine amplitude calibration of the pi/2 pulse in the backend provided.

    It performs a series of repetition experiments of the pi/2 pulse.
    For a perfect pi/2 pulse, the populations would oscillate with a
    frequency of pi/4 of the number of pulses. Any deviations from this
    frequency are used to correct the current estimate of the pi/2 pulse
    amplitude.

    Most of the experiments use an odd number of repetitions as a way of
    keeping the results away from the minima and maxima of the oscillations,
    making it easier to differentiate an over-rotation from an under-rotation.
    The initial points also include even numbers as a way to get a sense
    of the amplitude of the oscillations. With few repetitions, it is less
    likely that errors will accumulate, and the points are more likely to
    actually coincide with maxima and minima.

    Data analysis is then performed to determine how much the frequency
    of oscillation differs from the expected one.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The calibration graph where this calibration process is being
        performed. It contains the variables that will be used and
        updated during the optimization.
    backend : AmplitudeCalibrationBackend
        A class containing all the communication necessary with an
        external or simulated hardware that will be calibrated.
    session : Qctrl
        The Boulder Opal session that will run the data analysis.
    point_count : int, optional
        The number of points collected. The points collected correspond
        to all the repetitions up to 4, and then only the odd ones. Defaults
        to 14 points.

    Returns
    -------
    CalibrationStatus
        Whether the calibration has succeeded.
    """
    pi_2_pulse_amplitude = calibration_graph.get_variable("pi_2_pulse_amplitude").get()

    repetitions = np.setdiff1d(
        np.arange(1, max(point_count + 1, 2 * point_count - 4)),
        np.arange(6, 2 * point_count - 4, 2),
    )

    try:
        populations = np.array(
            [
                backend.pi_2_pulse_experiment(
                    amplitude=pi_2_pulse_amplitude,
                    drag=np.array([0]),
                    repetition_count=repetition_count,
                )
                for repetition_count in repetitions
            ]
        )
    except:  # pylint: disable=bare-except
        return CalibrationStatus.FAIL

    amplitude_correction = _find_deviation_from_frequency(
        x_data=repetitions,
        y_data=populations,
        session=session,
        expected_frequency=np.pi / 4,
        phase_offset=0,
    )

    calibration_graph.get_variable("pi_2_pulse_amplitude").set(
        pi_2_pulse_amplitude * amplitude_correction
    )

    return CalibrationStatus.PASS


def fine_pi_pulse_calibration_function(
    calibration_graph: CalibrationGraph,
    backend: AmplitudeCalibrationBackend,
    session: Qctrl,
    point_count: int = 14,
) -> CalibrationStatus:
    """
    Perform the fine amplitude calibration of the pi pulse in the backend provided.

    It performs a series of repetition experiments of the pi pulse, preceded
    by an initial pi/2 pulse. For a perfect pi pulse, the populations would
    oscillate with a frequency of pi/2 of the number of pulses. Any
    deviations from this frequency are used to correct the current
    estimate of the pi pulse amplitude.

    The initial pi/2 pulse has the role of putting the results close to the
    0.5 value, as staying away from the maxima and minima allows us to
    more easily identify if something is an under-rotation or an over-rotation.
    Whether the number of repetitions is odd or even doesn't make much
    difference in this case, so we just use the same values as the pi/2
    pulse calibration for consistency.

    Data analysis is then performed to determine how much the frequency
    of oscillation differs from the expected one.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The calibration graph where this calibration process is being
        performed. It contains the variables that will be used and
        updated during the optimization.
    backend : AmplitudeCalibrationBackend
        A class containing all the communication necessary with an
        external or simulated hardware that will be calibrated.
    session : Qctrl
        The Boulder Opal session that will run the data analysis.
    point_count : int, optional
        The number of points collected. The points collected correspond
        to all the repetitions up to 4, and then only the odd ones. Defaults
        to 14 points.

    Returns
    -------
    CalibrationStatus
        Whether the calibration has succeeded.
    """
    pi_pulse_amplitude = calibration_graph.get_variable("pi_pulse_amplitude").get()
    pi_2_pulse_amplitude = calibration_graph.get_variable("pi_2_pulse_amplitude").get()

    repetitions = np.setdiff1d(
        np.arange(1, max(point_count + 1, 2 * point_count - 4)),
        np.arange(6, 2 * point_count - 4, 2),
    )

    try:
        populations = np.array(
            [
                backend.pi_2_and_pi_pulse_experiment(
                    pi_2_pulse_amplitude=pi_2_pulse_amplitude,
                    pi_2_pulse_drag=np.array([0]),
                    pi_pulse_amplitude=pi_pulse_amplitude,
                    pi_pulse_drag=np.array([0]),
                    repetition_count=repetition_count,
                )
                for repetition_count in repetitions
            ]
        )
    except:  # pylint: disable=bare-except
        return CalibrationStatus.FAIL

    # The presence of an initial pi/2 pulse puts the state in the equator
    # of the Bloch sphere even before any pi pulses have been applied, and
    # causes a phase offset of pi/4 in the population plot.
    amplitude_correction = _find_deviation_from_frequency(
        session=session,
        x_data=repetitions,
        y_data=populations,
        expected_frequency=np.pi / 2,
        phase_offset=np.pi / 4,
    )

    calibration_graph.get_variable("pi_pulse_amplitude").set(
        pi_pulse_amplitude * amplitude_correction
    )

    return CalibrationStatus.PASS


def create_amplitude_calibration_graph(
    backend: AmplitudeCalibrationBackend, session: Qctrl
) -> CalibrationGraph:
    r"""
    Creates a predefined graph for the amplitude calibration of Gaussian
    :math:`\pi` and :math:`\pi/2` pulses.

    This calibration graph contains three nodes. The root node is a coarse
    amplitude calibration that updates the value of the amplitudes of
    both the :math:`\pi` and the :math:`\pi/2` pulses. The subsequent nodes use these two
    values of the coarse calibration of the amplitudes for the fine
    calibration of each of the amplitudes individually. As the experiment
    for pi pulse calibration uses a :math:`\pi/2` pulse, the fine :math:`\pi/2` pulse
    calibration is treated as a requirement for the fine pi pulse calibration.

    The two variables stored in this node are the amplitude for each of
    the Gaussian pulses. They're stored in units of the maximum Rabi
    frequency of the system, and thus restricted to the interval between
    0 and 1.

    Parameters
    ----------
    backend : AmplitudeCalibrationBackend
        The backend where the calibration will be performed. It can be a
        an interface with external hardware or a simulator.
    session : :py:class:`~qctrl.Qctrl`
        The session of Boulder Opal used to perform the data analysis.

    Returns
    -------
    CalibrationGraph
        A graph for amplitude calibration.
    """
    calibration_graph = CalibrationGraph()

    calibration_graph.create_variable(
        initial_value=np.array([1.0]),
        upper_bound=1,
        lower_bound=0,
        name="pi_pulse_amplitude",
    )
    calibration_graph.create_variable(
        initial_value=np.array([0.5]),
        upper_bound=1,
        lower_bound=0,
        name="pi_2_pulse_amplitude",
    )

    coarse_calibration_node = calibration_graph.create_node(
        calibration_function=partial(
            coarse_calibration_function, backend=backend, session=session
        ),
        name="coarse_amplitude_calibration",
    )
    fine_pi_2_pulse_calibration_node = calibration_graph.create_node(
        calibration_function=partial(
            fine_pi_2_pulse_calibration_function, backend=backend, session=session
        ),
        name="fine_pi_2_pulse_amplitude_calibration",
        dependencies=[coarse_calibration_node],
    )
    calibration_graph.create_node(
        calibration_function=partial(
            fine_pi_pulse_calibration_function, backend=backend, session=session
        ),
        name="fine_pi_pulse_amplitude_calibration",
        dependencies=[coarse_calibration_node, fine_pi_2_pulse_calibration_node],
    )

    return calibration_graph
