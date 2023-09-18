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
Module containing the basic infrastructure for building calibration graphs.
"""

from __future__ import annotations

import textwrap as tw
import uuid
from enum import Enum
from typing import (
    Callable,
    NoReturn,
    Optional,
)

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from qctrlcommons.preconditions import check_argument
from qctrlvisualizer.style import (
    BORDER_COLOR,
    QCTRL_STYLE_COLORS,
    qctrl_style,
)

from qctrlexperimentscheduler.graph_traversal import (
    Verbosity,
    execute_optimus,
    execute_wave,
)
from qctrlexperimentscheduler.node import (
    CalibrationNode,
    CalibrationStatus,
    CheckDataStatus,
)
from qctrlexperimentscheduler.variable import Variable


def _no_return(value: NoReturn) -> NoReturn:
    """
    Use mypy to check if all items in the enum are handled.
    """
    raise RuntimeError(
        f"Unhandled {getattr(value, '__class__').__name__} value {value}."
    )


def _split_text(text: str) -> str:
    """
    Split a string, whose words are separated by "_", into paragraphs,
    such that the resulting text is in a bounding box close to a square.

    For example, consider the string "this_is_a_node". The `max_word_len` here
    determines to 4 (since both "this" and "node" have a length of 4 characters).
    The text will then be split into paragraphs, where each paragraph has up to
    max_word_len=4 characters (including blanks). Thus for the example, the output
    of the function will be:
        "this
         is a
         node".
    """

    text = text.replace("_", " ")
    word_list = text.split(" ")
    max_word_len = max(map(len, word_list))

    text_wrapper = tw.TextWrapper(width=max_word_len)
    final_text = text_wrapper.fill(text=text)

    return final_text


def _get_textbox_size(text: str, font_size: int | float) -> int | float:
    """
    Compute the size (width and height) of the bounding box of the given text.
    This function will create a `plt.figure` and adds the specified text to a textbox
    therein. Afterwards, the bounding box is computed. In the future, it might make
    sense to compute the size without creating a `plt.figure`. Also see the following
    discussion in the PR:
    https://github.com/qctrl/experiment-scheduler/pull/44#discussion_r1120879110.
    """

    figure = plt.figure()
    renderer = figure.canvas.get_renderer()
    text_box = plt.text(0, 0, text, fontsize=font_size)

    bounding_box = text_box.get_window_extent(renderer=renderer)
    width = bounding_box.width
    height = bounding_box.height
    plt.close()

    return max(width, height)


class CalibrationProtocol(Enum):
    """
    The calibration protocol used for an execution of the graph.

    Attributes
    ----------
    OPTIMUS
        A modified version of the Optimus algorithm [1]_. The modifications
        allow it to be used even for nodes that don't have specialized
        check data experiments.

    WAVE
        A modified version of the Wave algorithm [2]_. The modifications
        trigger recalibrations of all the dependents of nodes that have
        been recalibrated.

    References
    ----------
    .. [1] `J. Kelly, P. O'Malley, M. Neeley, H. Neven, J. M. Martinis,
            arXiv:1803.03226. <https://arxiv.org/abs/1803.03226>`_
    .. [2] `L. Riesebos, B. Bondurant, K. R. Brown. IEEE Micro 41, 57 (2021)
           <https://ieeexplore.ieee.org/document/9477114>`_
    """

    OPTIMUS = "OPTIMUS"
    WAVE = "WAVE"


class CalibrationGraph:
    """
    A class that defines a graph with all the steps of a calibration.
    """

    def __init__(self):
        self._nodes: dict[str, CalibrationNode] = {}
        self._edges: dict[str, list[str]] = {}
        self._variables: dict[str, Variable] = {}

    def create_node(
        self,
        calibration_function: Callable[["CalibrationGraph"], CalibrationStatus],
        dependencies: Optional[list[CalibrationNode]] = None,
        name: Optional[str] = None,
        timeout: Optional[float] = None,
        check_data_function: Optional[
            Callable[["CalibrationGraph"], CheckDataStatus]
        ] = None,
    ) -> CalibrationNode:
        """
        Add a node to the calibration graph.

        Parameters
        ----------
        calibration_function : Callable[[CalibrationGraph], CalibrationStatus]
            The callable that runs the calibration. The exact form of this function
            can vary a lot depending on the architecture that the calibration will
            run on, so don't assume anything about the function other than its
            input parameters and output return type.
        dependencies : list[CalibrationNode], optional
            A list of nodes that represent calibrations that this calibration
            depends on. They must belong to the same calibration as this
            node. These dependencies will be added to the graph in the alphabetical
            order by their names. Defaults to no dependencies.
        name : str, optional
            The optional name of the node. Each node name has to be unique in a
            given graph. Defaults to None, in which case a random name is
            assigned to the node.
        timeout : float, optional
            The time (in seconds) after which this calibration has to be redone,
            typically due to system drifts. If provided, must be grater than zero.
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

        Returns
        -------
        CalibrationNode
            The object representing the node created by this method.
        """
        dependencies = dependencies or []

        check_argument(
            all(node.in_graph(self) for node in dependencies),
            "Dependencies of a node must belong to the same graph.",
            {"dependencies": dependencies},
            extras={"Available nodes": list(self._nodes.keys())},
        )
        if name is not None:
            check_argument(
                name not in self._nodes,
                "The node name must be unique in a graph.",
                {"name": name},
                extras={"Used names": list(self._nodes.keys())},
            )

        unique_name = name or uuid.uuid4().hex
        node = CalibrationNode(
            calibration_graph=self,
            calibration_function=calibration_function,
            name=unique_name,
            timeout=timeout,
            check_data_function=check_data_function,
        )

        self._nodes[unique_name] = node
        self._edges[unique_name] = sorted(node.name for node in dependencies)
        return node

    def create_variable(
        self,
        initial_value: np.ndarray,
        upper_bound: float = np.inf,
        lower_bound: float = -np.inf,
        name: Optional[str] = None,
    ) -> Variable:
        """
        Add a variable to the calibration graph.

        Parameters
        ----------
        initial_value : np.ndarray
            The initial value assigned to the variable. It must only contain
            real values, and the values must lie between `upper_bound` and
            `lower_bound`, if they are defined. It cannot have more than one
            dimension.
        upper_bound : float, optional
            The upper limit of the values of this variable. Defaults to `np.inf`,
            in which case no upper limit is enforced.
        lower_bound : float, optional
            The upper limit of the values of this variable. Defaults to `-np.inf`,
            in which case no lower limit is enforced.
        name : str, optional
            The optional name of the variable. Each variable name has to be
            unique in a given graph. Defaults to None, in which case a random
            name is assigned to the variable.

        Returns
        -------
        Variable
            The object holding the calibration variable.
        """
        if name is not None:
            check_argument(
                name not in self._variables,
                "The variable name must be unique in a graph.",
                {"name": name},
                extras={"Used names": list(self._variables.keys())},
            )

        unique_name = name or uuid.uuid4().hex
        variable = Variable(
            initial_value=initial_value,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            name=unique_name,
        )
        self._variables[unique_name] = variable
        return variable

    def get_dependencies(self, node: CalibrationNode) -> list[CalibrationNode]:
        """
        Return a list of nodes on which the provided node depend.

        Parameters
        ----------
        node : CalibrationNode
            The node whose dependents you want to determine. It must
            belong to this calibration graph.

        Returns
        -------
        list[CalibrationNode]
            A list of nodes on which this node depends.
        """
        check_argument(
            node.in_graph(self), "The node must belong to this graph.", {"node": node}
        )

        dependency_names = self._edges.get(node.name, [])

        dependency_nodes = [self._nodes[name] for name in dependency_names]

        return dependency_nodes

    def get_node(self, name: str) -> CalibrationNode:
        """
        Return the node with this name, if present in the graph.

        Parameters
        ----------
        name : str
            The name of the node to fetch.

        Returns
        -------
        CalibrationNode
            The node from the graph whose name matches the name provided.
        """
        check_argument(
            name in self._nodes,
            "No node with this name found in this graph.",
            {"name": name},
            extras={"Available variables": list(self._nodes.keys())},
        )

        return self._nodes[name]

    def get_variable(self, name: str) -> Variable:
        """
        Return the variable with this name, if present in the graph.

        Parameters
        ----------
        name : str
            The name of the variable to fetch.

        Returns
        -------
        Variable
            The variable from the graph whose name matches the name provided.
        """
        check_argument(
            name in self._variables,
            "No variable with this name found in this graph.",
            {"name": name},
            extras={"Available variables": list(self._variables.keys())},
        )

        return self._variables[name]

    def execute(
        self,
        node: CalibrationNode,
        protocol: CalibrationProtocol = CalibrationProtocol.WAVE,
        verbosity: Verbosity = Verbosity.QUIET,
    ):
        """
        Execute calibrations in a graph in sequence, with the intention of
        keeping the selected node in a calibrated state.

        Parameters
        ----------
        node : CalibrationNode
            The node that you want to keep to calibrated.
        protocol : CalibrationProtocol, optional
            The algorithm used to traverse the calibration graph. By default,
            this function uses a modified version of the Wave algorithm [1]_.
        verbosity : Verbosity, optional
            The verbosity level of this run. Defaults to QUIET.

        References
        ----------
        .. [1] `L. Riesebos, B. Bondurant, K. R. Brown. IEEE Micro 41, 57 (2021)
               <https://ieeexplore.ieee.org/document/9477114>`_
        """
        check_argument(
            node.in_graph(self),
            "The node must belong to the calibration graph.",
            {"node": node},
        )

        if protocol is CalibrationProtocol.OPTIMUS:
            execute_optimus(self, node, verbosity)
        elif protocol is CalibrationProtocol.WAVE:
            execute_wave(self, node, verbosity)
        else:
            _no_return(protocol)

    @qctrl_style()
    def visualize(
        self,
        font_size: int | float = 12,
        arrow_linewidth: int | float = 5,
        arrowheads_size: int | float = 20,
        figure_size: Optional[list[int | float]] = None,
    ):
        """
        Create a visualization of the `CalibrationGraph` as a directed graph,
        where each edge is an arrow between exactly two nodes.

        Parameters
        ----------
        font_size : int or float, optional
            The font size of the node labels. Defaults to 12.
        arrow_linewidth : int or float, optional
            The linewidth of the edges between the nodes. Defaults to 5.
        arrowheads_size : int or float, optional
            The size of the arrowheads of the edges between the nodes.
            Defaults to 20.
        figure_size : list[int or float], optional
            A list of length 2 defining the size of the matplotlib figure, in which
            the graph is plotted (in inches). The first entry denotes the figure width
            and the second entry denotes the figure height. If not passes, the figure
            size is computed automatically.
        """

        check_argument(
            isinstance(font_size, (float, int)),
            "font_size must be an integer or float.",
            {"font_size": font_size},
        )

        check_argument(
            isinstance(arrow_linewidth, (float, int)),
            "arrow_linewidth must be an integer or float.",
            {"arrow_linewidth": arrow_linewidth},
        )

        check_argument(
            isinstance(arrowheads_size, (float, int)),
            "arrowheads_size must be an integer or float.",
            {"arrowheads_size": arrowheads_size},
        )

        # We will scale the figure size by 2 if `figure_size==None`. Notice that this is a magic
        # number, which is chosen by trial and error: For both inline backend and macosx backend
        # of matplotlib, many different graphs were plotted and 2 seemed to be a good choice for
        # all the cases.
        scaling = 2

        nodes = []
        edges = []
        for node_name, node in self._nodes.items():
            node_label = _split_text(node_name)
            nodes.append(node_label)
            for dependency in self.get_dependencies(node):
                dependency_label = _split_text(dependency.name)
                edges.append(tuple([dependency_label, node_label]))

        text_box_sizes = [
            _get_textbox_size(node_text, font_size) for node_text in nodes
        ]

        fig, axis = plt.subplots(layout="constrained")

        # Multiply text_box_size by 72. This is because the node size is measured in points ** 2,
        # whereas the text_box_sizes are measured in inch. Since 1 typographic point = 1/72 in,
        # we need to multiply by 72 for unit conversion. Notice that this factor is independent of
        # `plt.rcParams["figure.dpi"]`.
        pixels = 1 / fig.dpi
        node_size = (
            np.max(text_box_sizes) * 72 * scaling * pixels * plt.rcParams["figure.dpi"]
        )

        plotting_graph = nx.DiGraph()
        plotting_graph.add_nodes_from(nodes)
        plotting_graph.add_edges_from(edges)

        layout = nx.spiral_layout(plotting_graph)

        draw_nodes = nx.draw_networkx_nodes(
            G=plotting_graph,
            pos=layout,
            node_size=node_size,
            node_color=QCTRL_STYLE_COLORS[0],
            ax=axis,
            linewidths=1,
            alpha=0.5,
        )
        draw_nodes.set_edgecolor(BORDER_COLOR)
        nx.draw_networkx_labels(
            G=plotting_graph, pos=layout, font_size=font_size, font_color="w"
        )
        nx.draw_networkx_edges(
            G=plotting_graph,
            pos=layout,
            width=arrow_linewidth,
            edge_color=QCTRL_STYLE_COLORS[5],
            arrows=True,
            arrowsize=arrowheads_size,
            node_size=node_size,
            ax=axis,
        )

        if figure_size is None:
            # Adjust the figsize automatically according to the scaling. `axis.get_tightbbox`
            # returns an object `Bbox(x0=, y0=, x1=, y1=)`, where `x0`, `y0` determine the position
            # of the origin and `x1`, `y1` determine the size of the axis. These parameters are
            # retrieved through`.bounds`. Since we are only interested in the size, we select
            # `x1` (figure_width) and `y1` (figure_height).
            figure_width, figure_height = (
                scaling
                * pixels
                * np.array(
                    axis.get_tightbbox(renderer=fig.canvas.get_renderer()).bounds
                )[2:4]
            )
        else:
            check_argument(
                isinstance(figure_size, list) and len(figure_size) == 2,
                "figure_size must be a list of length 2.",
                {"figure_size": figure_size},
            )

            check_argument(
                isinstance(figure_size[0], (float, int))
                and isinstance(figure_size[1], (float, int)),
                "The elements of figure_size must be integers or floats, respectively.",
                {"figure_size": figure_size},
            )

            figure_width, figure_height = figure_size

        fig.set_size_inches(figure_width, figure_height)
