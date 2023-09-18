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
Module for the calibration variables.
"""
from typing import Optional

import numpy as np
from qctrlcommons.graph import Graph
from qctrlcommons.node.node_data import Tensor
from qctrlcommons.preconditions import check_argument


class Variable:
    """
    A parameter, or list of parameters, whose values the calibration will
    determine.

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
        The optional name of the variable. Defaults to None.
    """

    def __init__(
        self,
        initial_value: np.ndarray,
        upper_bound: float = np.inf,
        lower_bound: float = -np.inf,
        name: Optional[str] = None,
    ):
        check_argument(
            np.all(np.isreal(initial_value)),
            "The initial value must be real.",
            {"initial_value": initial_value},
        )
        check_argument(
            np.all(initial_value <= upper_bound),
            "The initial value must not be greater than the upper bound.",
            {"initial_value": initial_value, "upper_bound": upper_bound},
        )
        check_argument(
            np.all(initial_value >= lower_bound),
            "The initial value must not be smaller than the lower bound.",
            {"initial_value": initial_value, "lower_bound": lower_bound},
        )
        check_argument(
            upper_bound > lower_bound,
            "The lower bound must be smaller than the upper bound.",
            {"lower_bound": lower_bound, "upper_bound": upper_bound},
        )
        check_argument(
            len(np.asarray(initial_value).shape) < 2,
            "The variable cannot have more than one dimension.",
            {"initial_value": initial_value},
            extras={"initial value shape": np.asarray(initial_value).shape},
        )

        self._value = np.asarray(initial_value)
        self._upper_bound = upper_bound
        self._lower_bound = lower_bound
        self._name = name

    def to_optimization_variable(
        self, graph: Graph, name: Optional[str] = None
    ) -> Tensor:
        """
        Create an optimization variable that matches the form of the
        calibration variable.

        You can use this to use Boulder Opal's graphs to perform curve
        fitting with the calibration variables.

        Parameters
        ----------
        graph : :py:class:`~qctrl.graphs.Graph`
            The Boulder Opal model-based optimization graph object to
            which you want to pass the variable.
        name : str, optional
            The name of the variable in the Boulder Opal graph. Defaults to
            the same name of the calibration variable.

        Returns
        -------
        :py:class:`~qctrl.graphs.Tensor`
            The name of the tensor that corresponds to the optimization
            variable.
        """
        check_argument(
            isinstance(graph, Graph),
            "The graph must be a Boulder Opal optimization graph.",
            {"graph": graph},
            extras={"type of graph": type(graph)},
        )

        count = self._value.size
        _name = name or self._name
        upper_bound = self._upper_bound
        lower_bound = self._lower_bound

        is_lower_unbounded = self._lower_bound is (-np.inf)
        is_upper_unbounded = self._upper_bound is (np.inf)

        # Don't pass -infinity as a lower bound, to avoid runtime errors.
        if is_lower_unbounded:
            min_value = np.min(self._value)
            lower_padding = max(np.abs(min_value), 1)
            lower_bound = min_value - lower_padding

        # Don't pass infinity as an upper bound, to avoid runtime errors.
        if is_upper_unbounded:
            max_value = np.max(self._value)
            upper_padding = max(np.abs(max_value), 1)
            upper_bound = max_value + upper_padding

        return graph.optimization_variable(
            count=count,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            is_lower_unbounded=is_lower_unbounded,
            is_upper_unbounded=is_upper_unbounded,
            initial_values=self._value.reshape((count,)),
            name=_name,
        )

    def set(self, value: np.ndarray):
        """
        Update the value of the variable.

        Parameters
        ----------
        value : np.ndarray
            The new value of this variable. It must be real and within
            the interval defined by lower_bound and upper_bound.
        """
        value_array = np.asarray(value)
        check_argument(
            np.all(np.isreal(value)), "The value must be real.", {"value": value}
        )
        check_argument(
            value_array.shape == self._value.shape,
            "The new value must have the same shape as the current value.",
            {"value": value},
            extras={
                "current value shape": self._value.shape,
                "new value shape": value_array.shape,
            },
        )
        check_argument(
            np.all(value <= self._upper_bound),
            "The value must not be greater than the upper bound.",
            {"value": value},
            extras={"upper bound": self._upper_bound},
        )
        check_argument(
            np.all(value >= self._lower_bound),
            "The value must not be smaller than the lower bound.",
            {"value": value},
            extras={"lower bound": self._lower_bound},
        )
        self._value = value_array

    def get(self) -> np.ndarray:
        """
        Return the value of the variable.

        Returns
        -------
        np.ndarray
            The current value of the variable.
        """
        return self._value

    def __repr__(self) -> str:
        """
        Return string representation of the class.

        Returns
        -------
        str
            String representation of the calibration variable.
        """
        if self._name is None:
            return f"<Variable: value={self._value}>"
        return f'<Variable: name="{self._name}", value={self._value}>'
