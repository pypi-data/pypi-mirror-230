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
Module for nodes to calculate differentiations.
"""
from typing import List

import forge
import numpy as np

from qctrlcommons.node import node_data
from qctrlcommons.node.base import Node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.utils import validate_shape
from qctrlcommons.preconditions import (
    check_argument,
    check_argument_iterable,
)


class Hessian(Node):
    r"""
    Calculate a single Hessian matrix for all the variables.

    The Hessian is a matrix containing all the second partial derivatives
    of the `tensor` with respect to the `variables`.

    Parameters
    ----------
    tensor : Tensor(scalar, real)
        The real scalar tensor :math:`T` whose Hessian matrix you want to
        calculate.
    variables : list[Tensor(real)]
        The list of real variables :math:`\{\theta_i\}` with respect to
        which you want to take the second partial derivatives of the
        tensor. If any of the tensors of the list is not scalar, this
        function treats each of the elements of the tensor as a different
        variable. It does this by flattening all tensors and concatenating
        them in the same sequence that you provided in this list.
    name : str or None, optional
        The name of the node.

    Returns
    -------
    Tensor(2D, real)
        The real Hessian matrix :math:`H` containing the second partial
        derivatives of the `tensor` :math:`T` with respect to the
        `variables` :math:`\{\theta_i\}`.

    Warnings
    --------
    This function currently doesn't support calculating a Hessian matrix for
    a graph which includes an `infidelity_pwc` node if it involves a Hamiltonian
    with degenerate eigenvalues at any segment. In that case, the function
    returns a `nan` Hessian matrix.

    Notes
    -----
    The :math:`(i,j)` element of the Hessian contains the partial
    derivative of the `tensor` with respect to the ith and the jth
    `variables`:

    .. math::
        H_{i,j} = \frac{\partial^2 T}{\partial \theta_i \partial \theta_j}.

    The variables :math:`\{\theta_i\}` follow the same sequence as the
    input list of `variables`. If some of the `variables` are not scalars,
    this function flattens them and concatenates them in the same order of
    the list of `variables` that you provided to create the sequence of
    scalar variables :math:`\{\theta_i\}`.

    If you choose a negative log-likelihood as the tensor :math:`T`, you
    can use this Hessian as an estimate of the Fisher information matrix.
    """
    name = "hessian"
    args = [
        forge.arg("tensor", type=node_data.Tensor),
        forge.arg("variables", type=List[node_data.Tensor]),
    ]
    rtype = node_data.Tensor
    categories = [Category.LINEAR_ALGEBRA]

    @classmethod
    def create_node_data(cls, _operation, **kwargs):
        tensor = kwargs.get("tensor")
        variables = kwargs.get("variables")
        check_argument(
            isinstance(tensor, node_data.Tensor),
            "The tensor parameter must be a Tensor.",
            {"tensor": tensor},
        )
        tensor_shape = validate_shape(tensor, "tensor")
        check_argument(
            tensor_shape == (),
            "The tensor must be a scalar tensor.",
            {"tensor": tensor},
        )
        check_argument_iterable(variables, "variables")
        check_argument(
            all(isinstance(variable, node_data.Tensor) for variable in variables),
            "Each of the variables must be a Tensor.",
            {"variables": variables},
        )
        variable_count = sum(
            np.prod(validate_shape(variable, f"variables[{n}]"), dtype=int)
            for n, variable in enumerate(variables)
        )
        shape = (variable_count, variable_count)
        return node_data.Tensor(_operation, shape=shape)
