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
Module of node for building a calibration graph.
"""
from enum import Enum
from time import time
from typing import (
    TYPE_CHECKING,
    Callable,
    NoReturn,
    Optional,
)

import numpy as np
from qctrlcommons.preconditions import check_argument

if TYPE_CHECKING:
    from qctrlexperimentscheduler.graph import CalibrationGraph


def _no_return(value: NoReturn) -> NoReturn:
    """
    Use mypy to check if all items in the enum are handled.
    """
    raise RuntimeError(
        f"Unhandled {getattr(value, '__class__').__name__} value {value}."
    )


class CheckDataStatus(Enum):
    """
    The result of a check data function.

    If defined, this is an experiment that checks if we have reason to
    believe the current calibration is still valid, without performing
    the entire calibration experiment. If not defined, reproduces the
    result of the calibration experiment.

    Attributes
    ----------
    FAIL
        The check data routine failed.

    PASS
        The check data routine passed.
    """

    FAIL = "FAIL"
    PASS = "PASS"


class CalibrationStatus(Enum):
    """
    The result of a calibration function.

    Keeping track of the outcome of a calibration is important for graph
    traversal algorithms, because it allows to decide whether it is safe
    to perform dependent calibrations.

    Attributes
    ----------
    FAIL
        The calibration failed.

    PASS
        The calibration passed.
    """

    FAIL = "FAIL"
    PASS = "PASS"


class NodeStatus(Enum):
    """
    The status of the node, indicating whether its calibration has been
    performed or not.

    Knowing the status of the node allows the graph traversal algorithms
    determine whether to proceed or not with a sequence of calibrations
    across a graph.

    All nodes start at the UNCALIBRATED status. After the `calibrate` method
    of the node is called, it may update to either SUCCESS
    or FAIL, depending on the outcome of the calibration function.

    Attributes
    ----------
    UNCALIBRATED
        The node has not been calibrated.

    FAIL
        The node calibration failed or has timed out.

    SUCCESS
        The node calibration succeeded.
    """

    UNCALIBRATED = "UNCALIBRATED"
    FAIL = "FAIL"
    SUCCESS = "SUCCESS"


class CalibrationNode:
    """
    A node in the calibration graph, wrapping a calibration function.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The graph this node belongs to.
    calibration_function : Callable[[CalibrationGraph], CalibrationStatus]
        The callable that runs the calibration. The exact form of this function
        can vary a lot depending on the architecture that the calibration will
        run on, so don't assume anything about the function other than its
        input parameters and output return type.
    name : str
        The name of the node.
    timeout : float, optional
        The time (in seconds) after which this calibration has to be redone,
        typically due to system drifts. If provided, must be greater than zero.
        Defaults to None, in which case the the node doesn't time out.
    check_data_function : Callable[[CalibrationGraph], CheckDataStatus], optional
        The callable that runs the experiment to check data. This is an
        experiment to check if the calibration is capable of succeeding under
        the present conditions, and should be faster than a full calibration.
        The exact form of this form can vary depending on the architecture, so
        we don't assume anything besides the input and output types.
        If not provided, the calibration function is used to check data, if
        it is safe to run it (that is, if all the dependencies are in SUCCESS
        status). If that is not the case, it fails.
    """

    def __init__(
        self,
        calibration_graph: "CalibrationGraph",
        calibration_function: Callable[["CalibrationGraph"], CalibrationStatus],
        name: str,
        timeout: Optional[float] = None,
        check_data_function: Optional[
            Callable[["CalibrationGraph"], CheckDataStatus]
        ] = None,
    ):
        self._calibration_graph = calibration_graph
        self._calibration_function = calibration_function
        self._name = name
        self._node_status = NodeStatus.UNCALIBRATED
        self._last_calibration_time = -np.inf
        if timeout is not None:
            check_argument(
                timeout > 0,
                "The timeout period must be positive.",
                {"timeout": timeout},
            )
            self._timeout = timeout
        else:
            self._timeout = np.inf

        def _default_check_data_function(
            _calibration_graph: "CalibrationGraph",
        ) -> CheckDataStatus:
            """
            Custom check data for system where a clear check data definition
            isn't clear. In this case, the calibration function is used instead.

            This is a stopgap measure to use the Optimus algorithm (which
            requires a check data) without forcing the user to come up with
            check data experiment that might be bogus.

            Not that this only runs if the dependency nodes are calibrated.
            This is not how a check data function would usually work. This is
            only done because we can't trust results of a calibration function
            if the dependencies are miscalibrated.
            """
            dependencies = _calibration_graph.get_dependencies(self)
            if all(
                dependency.get_status() is NodeStatus.SUCCESS
                for dependency in dependencies
            ):
                node_status = self.calibrate()
                if node_status is NodeStatus.SUCCESS:
                    return CheckDataStatus.PASS

            return CheckDataStatus.FAIL

        self._check_data_function = check_data_function or _default_check_data_function

    @property
    def name(self):
        """
        Return the name of the node.
        """
        return self._name

    def calibrate(self) -> NodeStatus:
        """
        Run the provided calibration function.

        The outcome of this function determines whether the status of the
        node changes or remains the same.

        Returns
        -------
        NodeStatus
            The status of the node after the calibration.
        """
        calibration_status = self._calibration_function(self._calibration_graph)

        if calibration_status is CalibrationStatus.PASS:
            self._node_status = NodeStatus.SUCCESS
            self._last_calibration_time = time()
        elif calibration_status is CalibrationStatus.FAIL:
            self._node_status = NodeStatus.FAIL
        else:
            _no_return(calibration_status)

        return self._node_status

    def check_data(self) -> NodeStatus:
        """
        Run the provided function to run the experiment to check the data.

        If none is provided (not all calibration setups are capable of
        comporting a specialized check data function), then it will check
        if it is safe to run a calibration for this node. In other words, it
        will check if all dependencies are in SUCCESS status. If they are,
        a new calibration is run and its return status is used to determine
        the success of check data. If it is not safe to rerun a calibration
        (for example, if the dependencies haven't been calibrated yet),
        then check data fails.

        A failing check data experiment changes the state of the node.

        Returns
        -------
        NodeStatus
            The status of the node after the experiment.
        """
        data_status = self._check_data_function(self._calibration_graph)

        if data_status is CheckDataStatus.FAIL:
            self._node_status = NodeStatus.FAIL

        return self._node_status

    def check_if_timed_out(self):
        """
        Check whether the current node was last calibrated longer ago
        than the timeout period.

        This method may mutate the state of the node: if the current
        state of the node is SUCCESS and the timeout period has passed,
        the node status is updated to FAIL.
        """
        if (
            self._node_status is NodeStatus.SUCCESS
            and self.time_since_last_calibration() > self._timeout
        ):
            self._node_status = NodeStatus.FAIL

    def get_status(self) -> NodeStatus:
        """
        Get the status of the node, indicating whether the calibration has
        been run already, and whether it has succeeded.

        Returns
        -------
        NodeStatus
            Whether the calibration associated with the node has been run,
            and whether the last calibration has succeeded.
        """
        return self._node_status

    def in_graph(self, calibration_graph: "CalibrationGraph") -> bool:
        """
        Check if this node belongs to the graph provided.

        Parameters
        ----------
        calibration_graph : CalibrationGraph
            The graph that we want to know if this node belongs to.

        Returns
        -------
        bool
            Whether the node belongs to the graph.
        """
        return self._calibration_graph is calibration_graph

    def time_since_last_calibration(self) -> float:
        """
        Return the time since the last calibration was successful.

        Some graph traversal algorithms take into account whether the
        last calibration was longer ago than the typical drift times of
        the system, or whether the dependent nodes were calibrated more
        recently than the depending nodes. For these algorithms, having
        access to the last time since the calibration was run is important.

        Returns
        -------
        float
            The time in seconds since the last calibration was run
            successfully. If no calibration of this type was successful,
            this function returns `np.inf`.
        """
        return time() - self._last_calibration_time

    def __repr__(self) -> str:
        """
        Return string representation of the class.

        Returns
        -------
        str
            String representation of the calibration node.
        """
        return f'<CalibrationNode: name="{self.name}">'
