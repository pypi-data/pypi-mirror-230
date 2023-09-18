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
Collection of algorithms to traverse the calibration graphs.
"""

from enum import Enum
from typing import TYPE_CHECKING

from qctrlexperimentscheduler.node import (
    CalibrationNode,
    NodeStatus,
)

if TYPE_CHECKING:
    from qctrlexperimentscheduler.graph import CalibrationGraph


class Verbosity(Enum):
    """
    The level of verbosity of the calibration routines.

    Attributes
    ----------

    VERBOSE
        Show task status messages and progress bars.
    QUIET
        Do not show task status messages and progress bars.
    """

    VERBOSE = "VERBOSE"
    QUIET = "QUIET"


def _recursive_recalibration(
    calibration_graph: "CalibrationGraph", node: CalibrationNode, verbosity: Verbosity
):
    """
    Rerun the calibration of the dependency tree of the current node.

    This protocol runs a check data experiment for the node provided. If it
    fails, it runs the same protocol in all the dependencies. If after this
    the current node is not in a success state, it forces a recalibration of
    the current node as well.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The calibration graph that contains the calibration tasks to be
        performed.
    node : CalibrationNode
        The node whose state you want to recalibrate.
    verbosity : Verbosity
        The verbosity of messages when running calculations.

    Notes
    -----
    This protocol is very much analogous to the `diagnose` function of the
    Optimus algorithm [1], with the difference that a recalibration is run at
    the end even if none of the dependencies recalibrated, as long as the
    node is not in SUCCESS state. This is to make sure that even nodes
    without dependencies are recalibrated, if necessary.

    References
    ----------
    .. [1] `J. Kelly, P. O'Malley, M. Neeley, H. Neven, J. M. Martinis,
           arXiv:1803.03226.
           <https://arxiv.org/abs/1803.03226>`_
    """
    if verbosity is Verbosity.VERBOSE:
        print(f"Running recursive_recalibration for node {node.name}.")

    if node.check_data() is NodeStatus.SUCCESS:
        if verbosity is Verbosity.VERBOSE:
            print(f"  Node {node.name} is in SUCCESS state. Skipping.")
        return

    dependencies = calibration_graph.get_dependencies(node)

    for dependency in dependencies:
        _recursive_recalibration(calibration_graph, dependency, verbosity)

    if node.get_status() is not NodeStatus.SUCCESS:
        if verbosity is Verbosity.VERBOSE:
            print(f"  Calibrating node {node.name}.")
        node.calibrate()


def check_state(calibration_graph: "CalibrationGraph", node: CalibrationNode) -> bool:
    """
    Part of the Optimus algorithm that checks the sanity of the dependency tree.

    Check if all of the following are true for this node and all the nodes
    in its dependency tree, after checking if they have timed out:
    1. They are in a SUCCESS state.
    2. None of their dependencies have been calibrated more recently than
       the node itself.

    This function only mutates the state of the node if they have timed
    out.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The graph the dependency tree belongs to.
    node : CalibrationNode
        The node whose state is being assessed.

    Returns
    -------
    bool
        Whether the check state has passed or not.
    """
    node.check_if_timed_out()

    if node.get_status() is not NodeStatus.SUCCESS:
        return False

    for dependency in calibration_graph.get_dependencies(node):
        if (
            dependency.time_since_last_calibration()
            < node.time_since_last_calibration()
        ):
            return False
        if not check_state(calibration_graph, dependency):
            return False

    return True


def execute_optimus(
    calibration_graph: "CalibrationGraph", node: CalibrationNode, verbosity: Verbosity
):
    """
    Run an adapted version of the Optimus "maintain" algorithm.

    Pass the node that you want to calibrate, and the algorithm will rerun
    the nodes that it depends on, if they aren't in a success state, or if
    any of the nodes in their dependency tree have recalibrated sooner than
    nodes that are further up in the dependency tree.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The calibration graph that contains the calibration tasks to be
        performed.
    node : CalibrationNode
        The node whose state is being checked.
    verbosity : Verbosity
        The verbosity of messages when running calculations.

    Notes
    -----
    This implementation is very similar to the `maintain` function of
    the Optimus algorithm [1]. The main difference is that it calls the
    equivalent of the `diagnose` function in the top-level node as well,
    which may cause it to recalibrate before the end of the `maintain`.
    To make sure we're not duplicating calibrations, we check the status
    of the node at the end before proceeding.

    References
    ----------
    .. [1] `J. Kelly, P. O'Malley, M. Neeley, H. Neven, J. M. Martinis,
           arXiv:1803.03226.
           <https://arxiv.org/abs/1803.03226>`_
    """
    if verbosity is Verbosity.VERBOSE:
        print(f"Running execute_optimus for node {node.name}.")

    dependencies = calibration_graph.get_dependencies(node)

    # Recursively run this function through all the dependency tree.
    for dependency in dependencies:
        execute_optimus(calibration_graph, dependency, verbosity)

    # Skip the rest if the node is well calibrated.
    if check_state(calibration_graph, node):
        if verbosity is Verbosity.VERBOSE:
            print(f"  Check state passed for node {node.name}. Skipping.")
        return

    # If we got to this point, attempt recalibration of the tree.
    _recursive_recalibration(calibration_graph, node, verbosity)

    # If node is still failing check state, recalibrate.
    # This covers the corner case in the test test_check_state_with_fork
    # We should revisit later for a better solution.
    if not check_state(calibration_graph, node):
        if verbosity is Verbosity.VERBOSE:
            print(f"  Calibrating node {node.name}.")
        node.calibrate()


def execute_wave(
    calibration_graph: "CalibrationGraph", node: CalibrationNode, verbosity: Verbosity
) -> bool:
    """
    Run a modified version of the Wave algorithm for graph traversal.

    This differs from the original Wave algorithm [1]_ in that, in this
    implementation, if a node runs a calibration experiment, then all
    the dependents of the node will run their calibration experiments
    as well.

    Parameters
    ----------
    calibration_graph : CalibrationGraph
        The calibration graph that contains the calibration tasks to be
        performed.
    node : CalibrationNode
        The node whose state is being checked.
    verbosity : Verbosity
        The verbosity of messages when running calculations.

    Returns
    -------
    bool
        Whether the current `node` has been recalibrated or not as part
        of this routine.

    References
    ----------
    .. [1] `L. Riesebos, B. Bondurant, K. R. Brown. IEEE Micro 41, 57 (2021)
           <https://ieeexplore.ieee.org/document/9477114>`_
    """
    if verbosity is Verbosity.VERBOSE:
        print(f"Running execute_wave for node {node.name}.")

    node.check_if_timed_out()

    dependencies_recalibrated = [
        execute_wave(calibration_graph, dependency, verbosity)
        for dependency in calibration_graph.get_dependencies(node)
    ]

    if any(dependencies_recalibrated) or (node.get_status() is not NodeStatus.SUCCESS):
        if verbosity is Verbosity.VERBOSE:
            print(f"  Calibrating node {node.name}.")
        node.calibrate()
        return True

    if verbosity is Verbosity.VERBOSE:
        print(f"  Node {node.name} is up to date. Skipping.")
    return False
