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
Define a backend for the simulation of a single-qubit system.
"""

from typing import Optional

import numpy as np
from qctrl import Qctrl
from qctrlcommons.preconditions import check_argument

from qctrlexperimentscheduler.predefined.amplitude_calibration import (
    AmplitudeCalibrationBackend,
)


def simulate_single_qubit(
    session: Qctrl,
    control_values: np.ndarray,
    control_durations: np.ndarray,
    dephasing_noise: float = 0.0,
) -> np.ndarray:
    """
    Simulate the evolution of a single qubit under certain controls.

    This function uses Boulder Opal to simulate the evolution of a qubit
    in the backend.

    Parameters
    ----------
    session : :py:class:`qctrl.Qctrl`
        A session with Boulder Opal, it can be local or in the cloud.
    control_values : np.ndarray
        The values of the controls in each segment. They can be batched.
        The trailing dimension contains the values, while the leading
        dimensions are the batch dimensions.
    control_durations : np.ndarray
        The values of the durations of each segment of the controls. They
        must have the same length as the `control_values`.
    dephasing_noise : float, optional
        The amount of dephasing noise in the system. Defaults to no noise.

    Returns
    -------
    np.ndarray
        An array with two elements containing the probability of finding
        a qubit in state 0 or 1, respectively. The probabilities reside in
        the trailing dimension, while the leading dimensions are the batch
        dimensions.
    """
    graph = session.create_graph()

    control_signal = graph.pwc(
        values=control_values, durations=control_durations, time_dimension=-1
    )

    hamiltonian = graph.hermitian_part(
        control_signal * graph.pauli_matrix("P")
    ) + dephasing_noise * graph.pauli_matrix("Z")

    graph.infidelity_pwc(
        hamiltonian=hamiltonian, target=graph.target(np.diag([1, 0])), name="population"
    )

    result = session.functions.calculate_graph(
        graph=graph, output_node_names=["population"]
    )

    probability_1 = np.asarray(result.output["population"]["value"])

    probabilities = np.array([1 - probability_1, probability_1]).T

    return probabilities


class SimulationAmplitudeCalibrationBackend(AmplitudeCalibrationBackend):
    """
    A backend for simulating an amplitude calibration with Boulder Opal.

    This backend offers a simple model of a qubit subject to dephasing
    noise, and allows you to simulate sequences of Gaussian pulses.

    Parameters
    ----------
    session : :py:class:`~qctrl.Qctrl`
        A session of Boulder Opal to be used to perform the simulations.
    maximum_rabi_rate : float
        The maximum value of the controls of the qubit.
    pulse_duration : float
        The duration of the pulses, in seconds.
    time_step : float
        The duration of each time step of the control, in seconds.
    dephasing_noise : float, optional
        The amount of constant dephasing noise the system will be
        subject to. Defaults to no dephasing noise.
    shot_count : int, optional
        The default shot count for experiments run in this backend.
        Defaults to 4096.
    seed : int, optional
        A seed for the random measurements. Defaults to a random seed.
    """

    def __init__(
        self,
        session: Qctrl,
        maximum_rabi_rate: float,
        pulse_duration: float,
        time_step: float,
        dephasing_noise: float = 0.0,
        shot_count: int = 4096,
        seed: Optional[int] = None,
    ):
        self._session = session

        check_argument(
            maximum_rabi_rate > 0,
            "The maximum Rabi rate must be positive",
            {"maximum_rabi_rate": maximum_rabi_rate},
        )

        self._maximum_rabi_rate = maximum_rabi_rate

        check_argument(
            pulse_duration > 0,
            "The pulse duration must be positive",
            {"pulse_duration": pulse_duration},
        )

        self._pulse_duration = pulse_duration

        check_argument(
            time_step > 0,
            "The time step must be positive",
            {"time_step": time_step},
        )
        check_argument(
            time_step < pulse_duration,
            "The time step must be smaller than the pulse duration.",
            {"pulse_duration": pulse_duration, "time_step": time_step},
        )

        self._time_step = time_step

        self._dephasing_noise = dephasing_noise
        seed_sequence = np.random.SeedSequence(seed)
        self._default_shot_count = shot_count
        self._rng = np.random.default_rng(seed_sequence)

    def _simulate_experiment(
        self,
        control_values: np.ndarray,
        control_durations: np.ndarray,
        shot_count: int,
    ) -> np.ndarray:
        """
        Run a simulation of a system subject to a control PWC with the
        provided values and durations.

        The returned values correspond to the fraction of measurements
        of the state |1> given a limited number of shots.

        Parameters
        ----------
        control_values : np.ndarray
            The complex values of the controls.
            It can contain one batch dimension.
        control_durations : np.ndarray
            The values of each of the duration segments.
        shot_count : int
            The number of shots in this experiment.

        Returns
        -------
        np.ndarray
            The fraction of times the experiment returned a result with
            state |1>.
        """
        probabilities = simulate_single_qubit(
            session=self._session,
            control_values=control_values,
            control_durations=control_durations,
            dephasing_noise=self._dephasing_noise,
        ).reshape(-1, 2)

        output = np.array(
            [
                self._rng.choice([0, 1], p=probability, size=(shot_count,))
                for probability in probabilities
            ]
        )

        return np.mean(output == 1, axis=-1)

    def _get_pulse_values(
        self, amplitudes: np.ndarray, drag_parameters: np.ndarray
    ) -> np.ndarray:
        """
        Return values of a Gaussian pulse with the specified amplitude
        and DRAG parameter.

        Parameters
        ----------
        amplitudes : np.ndarray
            The values of the amplitude of the Gaussian pulse.
        drag_parameters : np.ndarray
            The values of the DRAG parameter of the Gaussian pulse.
            It must broadcastable with the amplitude.

        Returns
        -------
        np.ndarray
            The values of the pulse as a 2D array. If you provide more
            than one value of the amplitude and drag, the returned value
            here will also be a batch.
        """
        return np.array(
            [
                self._session.signals.gaussian_pulse(
                    duration=self._pulse_duration,
                    amplitude=_amplitude * self._maximum_rabi_rate,
                    drag=_drag,
                ).export_with_time_step(self._time_step)
                for _amplitude, _drag in np.broadcast(amplitudes, drag_parameters)
            ]
        )

    def pi_pulse_experiment(
        self,
        amplitude: np.ndarray,
        drag: np.ndarray,
        repetition_count: int,
        shot_count: Optional[int] = None,
    ) -> np.ndarray:
        r"""
        Run a simulation of a series of Gaussian :math:`\pi` pulses applied to a qubit
        initially in state :math:`|0\rangle`.

        Parameters
        ----------
        amplitude : np.ndarray
            Value of amplitudes of the pi pulse. Must be a 1D array.
        drag : np.ndarray
            Value of the DRAG parameter of the pi pulse. Must be a 1D array
            that is broadcastable with the `amplitude`.
        repetition_count : int
            The number of times the pi pulse is applied to the qubit in this
            experiment.
        shot_count : int, optional
            The number of shots of each experiment. If not provided, defaults
            to the default number of shots of the backend.

        Returns
        -------
        np.ndarray
            The fraction of times the experiments measured a qubit in :math:`|1\rangle`
            state. This is returned as a 1D array. If you passed more than
            one amplitude or DRAG parameter, then each element of the array
            corresponds to an experiment with one set of parameters.
        """
        check_argument(
            len(amplitude.shape) == 1,
            "The amplitude must be a 1D array.",
            {"amplitude": amplitude},
        )
        check_argument(
            len(drag.shape) == 1,
            "The DRAG parameter must be a 1D array.",
            {"drag": drag},
        )
        check_argument(
            drag.shape[0] == amplitude.shape[0]
            or drag.shape[0] == 1
            or amplitude.shape[0] == 1,
            "The amplitude and the DRAG parameter must be broadcastable.",
            {"amplitude": amplitude, "drag": drag},
        )

        values = np.tile(self._get_pulse_values(amplitude, drag), repetition_count)
        durations = np.repeat(self._time_step, values.shape[-1])
        return self._simulate_experiment(
            control_values=values,
            control_durations=durations,
            shot_count=shot_count or self._default_shot_count,
        )

    def pi_2_pulse_experiment(
        self,
        amplitude: np.ndarray,
        drag: np.ndarray,
        repetition_count: int,
        shot_count: Optional[int] = None,
    ) -> np.ndarray:
        r"""
        Run a simulation of a series of Gaussian :math:`\pi/2` pulses applied to a qubit
        initially in state :math:`|0\rangle`.

        Parameters
        ----------
        amplitude : np.ndarray
            Value of amplitudes of the pi pulse. Must be a 1D array.
        drag : np.ndarray
            Value of the DRAG parameter of the pi pulse. Must be a 1D array
            that is broadcastable with the `amplitude`.
        repetition_count : int
            The number of times the :math:`\pi/2` pulse is applied to the qubit in this
            experiment.
        shot_count : int, optional
            The number of shots of each experiment. If not provided, defaults
            to the default number of shots of the backend.

        Returns
        -------
        np.ndarray
            The fraction of times the experiments measured a qubit in :math:`|1\rangle`
            state. This is returned as a 1D array. If you passed more than
            one amplitude or DRAG parameter, then each element of the array
            corresponds to an experiment with one set of parameters.
        """
        check_argument(
            len(amplitude.shape) == 1,
            "The amplitude must be a 1D array.",
            {"amplitude": amplitude},
        )
        check_argument(
            len(drag.shape) == 1,
            "The DRAG parameter must be a 1D array.",
            {"drag": drag},
        )
        check_argument(
            drag.shape[0] == amplitude.shape[0]
            or drag.shape[0] == 1
            or amplitude.shape[0] == 1,
            "The amplitude and the DRAG parameter must be broadcastable.",
            {"amplitude": amplitude, "drag": drag},
        )

        values = np.tile(self._get_pulse_values(amplitude, drag), repetition_count)
        durations = np.repeat(self._time_step, values.shape[-1])
        return self._simulate_experiment(
            control_values=values,
            control_durations=durations,
            shot_count=shot_count or self._default_shot_count,
        )

    def pi_2_and_pi_pulse_experiment(
        self,
        pi_2_pulse_amplitude: np.ndarray,
        pi_2_pulse_drag: np.ndarray,
        pi_pulse_amplitude: np.ndarray,
        pi_pulse_drag: np.ndarray,
        repetition_count: int,
        shot_count: Optional[int] = None,
    ) -> np.ndarray:
        r"""
        Run a simulation of a Gaussian :math:`\pi/2` pulse followed by a series
        of Gaussian pi pulses applied to a qubit initially in state :math:`|0\rangle`.

        Parameters
        ----------
        pi_2_pulse_amplitude : np.ndarray
            Value of amplitudes of the :math:`\pi/2` pulse. Must be a 1D array
            that is broadcastable with `pi_2_pulse_drag`, `pi_pulse_amplitude`,
            and `pi_pulse_drag`.
        pi_2_pulse_drag : np.ndarray
            Value of the DRAG parameter of the :math:`\pi/2` pulse. Must be a 1D array
            that is broadcastable with `pi_2_pulse_amplitude`,
            `pi_pulse_amplitude`, and `pi_pulse_drag`.
        pi_pulse_amplitude : np.ndarray
            Value of amplitudes of the pi pulse. Must be a 1D array that is
            broadcastable with `pi_2_pulse_amplitude`, `pi_2_pulse_drag`,
            and `pi_pulse_drag`.
        pi_pulse_drag : np.ndarray
            Value of the DRAG parameter of the pi pulse. Must be a 1D array
            that is broadcastable with `pi_2_pulse_amplitude`, `pi_2_pulse_drag`,
            and `pi_pulse_amplitude`.
        repetition_count : int
            The number of times the pi pulse is applied to the qubit in this
            experiment.
        shot_count : int, optional
            The number of shots of each experiment. If not provided, defaults
            to the default number of shots of the backend.

        Returns
        -------
        np.ndarray
            The fraction of times the experiments measured a qubit in :math:`|1\rangle`
            state. This is returned as a 1D array. If you passed more than
            one amplitude or DRAG parameter, then each element of the array
            corresponds to an experiment with one set of parameters.
        """
        check_argument(
            len(pi_pulse_amplitude.shape) == 1,
            "The pi pulse amplitude must be a 1D array.",
            {"pi_pulse_amplitude": pi_pulse_amplitude},
        )
        check_argument(
            len(pi_pulse_drag.shape) == 1,
            "The pi pulse DRAG parameter must be a 1D array.",
            {"pi_pulse_drag": pi_pulse_drag},
        )
        check_argument(
            pi_pulse_drag.shape[0] == pi_pulse_amplitude.shape[0]
            or pi_pulse_drag.shape[0] == 1
            or pi_pulse_amplitude.shape[0] == 1,
            "The pi pulse amplitude and the pi pulse DRAG parameter must be broadcastable.",
            {"pi_pulse_amplitude": pi_pulse_amplitude, "pi_pulse_drag": pi_pulse_drag},
        )
        check_argument(
            len(pi_2_pulse_amplitude.shape) == 1,
            "The pi/2 pulse amplitude must be a 1D array.",
            {"pi_2_pulse_amplitude": pi_2_pulse_amplitude},
        )
        check_argument(
            len(pi_2_pulse_drag.shape) == 1,
            "The pi/2 pulse DRAG parameter must be a 1D array.",
            {"pi_2_pulse_drag": pi_2_pulse_drag},
        )
        check_argument(
            pi_2_pulse_drag.shape[0] == pi_2_pulse_amplitude.shape[0]
            or pi_2_pulse_drag.shape[0] == 1
            or pi_2_pulse_amplitude.shape[0] == 1,
            "The pi/2 pulse amplitude and the pi/2 pulse DRAG parameter must be broadcastable.",
            {
                "pi_2_pulse_amplitude": pi_pulse_amplitude,
                "pi_2_pulse_drag": pi_2_pulse_drag,
            },
        )

        values = np.concatenate(
            [
                self._get_pulse_values(pi_2_pulse_amplitude, pi_2_pulse_drag),
                np.tile(
                    self._get_pulse_values(pi_pulse_amplitude, pi_pulse_drag),
                    repetition_count,
                ),
            ],
            axis=-1,
        )
        durations = np.repeat(self._time_step, values.shape[-1])
        return self._simulate_experiment(
            control_values=values,
            control_durations=durations,
            shot_count=shot_count or self._default_shot_count,
        )
