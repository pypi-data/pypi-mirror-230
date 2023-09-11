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
Utilities for running verifications and performing common transformations on inputs.
"""

from enum import Enum
from typing import (
    Any,
    Optional,
    Union,
)

import numpy as np
from scipy.sparse import (
    issparse,
    spmatrix,
)

from qctrlcommons.exceptions import QctrlArgumentsValueError
from qctrlcommons.node.node_data import (
    Pwc,
    Stf,
)


def check_argument(
    condition: Any, description: str, arguments: dict, extras: Optional[dict] = None
) -> None:
    """
    Raises a QctrlArgumentsValueError with the specified parameters if
    the given condition is false, otherwise does nothing.
    """
    if condition:
        return
    raise QctrlArgumentsValueError(description, arguments, extras=extras)


def check_argument_hermitian(operator: Union[np.ndarray, spmatrix], argument_name: str):
    """
    Raises a QctrlArgumentsValueError if the specified array or sparse matrix
    is not a Hermitian operator, otherwise does nothing.
    """

    check_argument(
        len(operator.shape) == 2,
        f"{argument_name} must be Hermitian, but is not 2D.",
        {argument_name: operator},
    )
    check_argument(
        operator.shape[0] == operator.shape[1],
        f"{argument_name} must be Hermitian, but is non-square.",
        {argument_name: operator},
    )

    if issparse(operator):
        check_argument(
            np.allclose((operator - operator.getH()).data, 0.0),
            f"{argument_name} must be Hermitian, but does not equal its Hermitian conjugate.",
            {argument_name: operator},
        )

    else:
        check_argument(
            np.allclose(operator, operator.T.conj()),
            f"{argument_name} must be Hermitian, but does not equal its Hermitian conjugate.",
            {argument_name: operator},
        )


def check_argument_non_hermitian(array: np.ndarray, argument_name: str):
    """
    Raises a QctrlArgumentsValueError if the specified array is a Hermitian operator,
    otherwise does nothing.
    """
    check_argument(
        len(array.shape) == 2,
        f"{argument_name} must be non-Hermitian, but is not 2D.",
        {argument_name: array},
    )
    check_argument(
        array.shape[0] == array.shape[1],
        f"{argument_name} must be non-Hermitian, but is non-square.",
        {argument_name: array},
    )
    check_argument(
        not np.allclose(array, array.T.conj()),
        f"{argument_name} must be non-Hermitian, "
        "but equals its Hermitian conjugate (i.e. is Hermitian).",
        {argument_name: array},
    )


def check_argument_unitary(array: np.ndarray, argument_name: str):
    """
    Raises a QctrlArgumentsValueError if the specified array is not a unitary operator,
    otherwise does nothing.
    """
    check_argument(
        len(array.shape) == 2,
        f"{argument_name} must be unitary, but is not 2D.",
        {argument_name: array},
    )
    check_argument(
        array.shape[0] == array.shape[1],
        f"{argument_name} must be unitary, but is non-square.",
        {argument_name: array},
    )
    check_argument(
        np.allclose(array @ array.T.conj(), np.identity(array.shape[0])),
        f"{argument_name} must be unitary, but its Hermitian conjugate is not its inverse.",
        {argument_name: array},
    )


def check_argument_operator(array: np.ndarray, argument_name: str):
    """
    Raises a QctrlArgumentsValueError if the specified array is not an operator (square),
    otherwise does nothing.
    """
    check_argument(
        len(array.shape) == 2, f"{argument_name} must be 2D.", {argument_name: array}
    )
    check_argument(
        array.shape[0] == array.shape[1],
        f"{argument_name} must be square.",
        {argument_name: array},
    )


def check_argument_partial_isometry(array: np.ndarray, argument_name: str):
    """
    Raises a QctrlArgumentsValueError if the specified array is not a
    partial isometry. (V is a partial isometry iff VV^†V = V)
    """
    check_argument(
        len(array.shape) == 2,
        f"{argument_name} must be a partial isometry, but is not 2D.",
        {argument_name: array},
    )
    check_argument(
        array.shape[0] == array.shape[1],
        f"{argument_name}  must be a partial isometry, but is non-square.",
        {argument_name: array},
    )
    check_argument(
        np.allclose(array @ array.T.conj() @ array, array),
        f"{argument_name} must be a partial isometry, but does not yield itself "
        "when multiplied by its adjoint and then itself.",
        {argument_name: array},
    )


def check_argument_orthogonal_projection_operator(
    array: np.ndarray, argument_name: str
):
    """
    Raises a QctrlArgumentsValueError if the specified array is not an orthogonal
    projection operator (Hermitian and idempotent), otherwise does nothing.
    """
    check_argument(
        len(array.shape) == 2,
        f"{argument_name} must be an orthogonal projection operator, but is not 2D.",
        {argument_name: array},
    )
    check_argument(
        array.shape[0] == array.shape[1],
        f"{argument_name} must be an orthogonal projection operator, but is non-square.",
        {argument_name: array},
    )
    check_argument(
        np.allclose(array, array.T.conj()),
        f"{argument_name} must be an orthogonal projection operator, but is not Hermitian.",
        {argument_name: array},
    )
    check_argument(
        np.allclose(array, array @ array),
        f"{argument_name} must be an orthogonal projection operator, "
        "but is not idempotent (does not equal its square).",
        {argument_name: array},
    )


def check_argument_nonzero(array: np.ndarray, argument_name: str):
    """
    Raises a QctrlArgumentsValueError if all values in the specified array are zero.
    """
    check_argument(
        np.any(array),
        f"{argument_name} must contain some non-zero elements.",
        {argument_name: array},
    )


def check_argument_iterable(argument, argument_name):
    """
    Raises QctrlArgumentsValueError if the argument is not iterable.
    """
    try:
        iter(argument)
    except TypeError as error:
        raise QctrlArgumentsValueError(
            f"{argument_name} must be an iterable, such as a list.",
            {argument_name: argument},
        ) from error


def check_argument_integer(argument, argument_name):
    """
    Raises QctrlArgumentsValueError if the argument is not an integer.
    """
    check_argument(
        np.isscalar(argument),
        f"{argument_name} must be scalar.",
        {argument_name: argument},
    )
    check_argument(
        np.isreal(argument), f"{argument_name} must be real.", {argument_name: argument}
    )
    check_argument(
        argument % 1 == 0,
        f"{argument_name} must be an integer.",
        {argument_name: argument},
    )


def check_argument_integer_sequence(argument, name):
    """
    Raises QctrlArgumentsValueError if the argument is not a sequence of integer numbers.
    """

    check_argument_iterable(argument, name)

    check_argument(
        all(np.isscalar(x) for x in argument),
        f"Items of {name} must be scalar.",
        {name: argument},
    )
    check_argument(
        all(np.isreal(x) for x in argument),
        f"Items of {name} must be real.",
        {name: argument},
    )
    check_argument(
        all(x % 1 == 0 for x in argument),
        f"Items of {name} must be an integer.",
        {name: argument},
    )


def check_argument_positive_integer(argument, argument_name):
    """
    Raises QctrlArgumentsValueError if the argument is not a strictly positive integer.
    """
    check_argument(
        np.isscalar(argument),
        f"{argument_name} must be scalar.",
        {argument_name: argument},
    )
    check_argument(
        np.isreal(argument) and argument % 1 == 0 and argument > 0,
        f"{argument_name} must be a positive integer.",
        {argument_name: argument},
    )


def check_argument_real_vector(argument, argument_name):
    """
    Raises QctrlArgumentsValueError if the argument is not a 1-D array of real numbers.
    """
    check_numeric_numpy_array(argument, argument_name, dtype=NumpyDtype.REAL)

    # This makes sure that extracting shape doesn't throw an error if the
    # user passes a list. Instead, a list will fail the next test, with a
    # more meaningful message.
    shape = getattr(argument, "shape", ())

    check_argument(
        len(shape) == 1,
        f"{argument_name} must be a one-dimensional array.",
        {argument_name: argument},
    )
    check_argument(
        len(argument) > 0,
        f"{argument_name} must be an array with at least one element.",
        {argument_name: argument},
    )


class NumpyDtype(Enum):
    """
    NumPy numeric data types.
    """

    COMPLEX = "iufc"
    REAL = "iuf"
    INTEGER = "iu"


def check_numeric_numpy_array(argument, argument_name, dtype=NumpyDtype.COMPLEX):
    """
    Raises QctrlArgumentsValueError if the argument is a NumPy array of
    a non-dtype. Does nothing if the argument doesn't have a
    field `argument.dtype.kind` (which all NumPy arrays have).
    """
    if hasattr(argument, "dtype"):
        if hasattr(argument.dtype, "kind"):
            check_argument(
                argument.dtype.kind in dtype.value,
                f"{argument_name} must contain data of a numeric type.",
                {argument_name: argument},
                extras={f"{argument_name}.dtype": argument.dtype},
            )


def check_argument_non_negative_scalar(argument, argument_name):
    """
    Raises QctrlArgumentsValueError if the argument is not a non-negative scalar.

    In other words, the argument should be a real scalar which is either greater than
    or equal to zero.
    """
    check_argument(
        np.isscalar(argument),
        f"{argument_name} must be scalar.",
        {argument_name: argument},
    )
    check_argument(
        np.isreal(argument), f"{argument_name} must be real.", {argument_name: argument}
    )
    check_argument(
        argument >= 0,
        f"{argument_name} must not be negative.",
        {argument_name: argument},
    )


def check_argument_positive_scalar(argument, argument_name):
    """
    Raises QctrlArgumentsValueError if the argument is not a strictly positive scalar
    number.
    """
    check_argument_non_negative_scalar(argument, argument_name)
    check_argument(
        argument != 0, f"{argument_name} cannot be zero.", {argument_name: argument}
    )


def check_duration(duration, duration_name):
    """
    Checks that the duration is valid.

    A valid duration is a positive real or a zero scalar.

    Parameters
    ----------
    duration: number
        The duration to be tested.
    duration_name : str
        The name of the parameter of the duration.
    """
    check_argument_non_negative_scalar(duration, duration_name)


def check_sample_times(sample_times, sample_times_name):
    """
    Checks that the sample_times array is valid.

    A valid sample_times array is one-dimensional, only contains real
    numbers, is ordered, and has at least one element.

    Parameters
    ----------
    sample_times : np.ndarray
        The array to be tested.
    sample_times_name : str
        The name of the array.
    """
    check_argument_real_vector(sample_times, sample_times_name)
    check_argument(
        # Note that this is also true for sample_times only holding one element or empty.
        np.all(np.diff(sample_times) > 0),
        f"{sample_times_name} must be ordered and not have duplicate values.",
        {sample_times_name: sample_times},
    )


def check_sample_times_with_bounds(sample_times, sample_times_name, pwc, pwc_name):
    """
    Checks that the sample_times array is valid (see check_sample_times) and
    that its values lie between 0 and sum(pwc.durations) (included).

    Parameters
    ----------
    sample_times : np.ndarray
        The array to be tested.
    sample_times_name : str
        The name of the array.
    pwc : Union[Pwc, SparsePwc]
        The PWC function whose duration bounds the values of the sample times.
    pwc_name : str
        The name of the PWC function.
    """
    check_sample_times(sample_times, sample_times_name)

    duration = np.sum(pwc.durations)
    check_argument(
        (sample_times[0] >= 0.0 or np.isclose(sample_times[0], 0.0))
        and (sample_times[-1] <= duration or np.isclose(sample_times[-1], duration)),
        f"{sample_times_name} must be between 0 and the duration of {pwc_name}.",
        {sample_times_name: sample_times, pwc_name: pwc},
        extras={"sum({duration_pwc_name}.durations)": duration},
    )


def check_operator(operator, operator_name):
    """
    Checks that the operator is a square 2D array or tensor, or a batch of them.

    Otherwise, the function raises an exception.

    Parameters
    ----------
    operator : np.ndarray or Tensor
        The operator to be tested for validity.
    operator_name : str
        The name of the operator, used for the error messages.
    """
    check_numeric_numpy_array(operator, operator_name)

    # Obtains shape in a way that doesn't throw an obscure error message if
    # the user passes a list or a Pwc by mistake. Instead, an error is
    # thrown in the next check_argument.
    shape = getattr(operator, "shape", ())

    check_argument(
        len(shape) >= 2,
        f"{operator_name} must have at least two dimensions.",
        {operator_name: operator},
        extras={f"{operator_name}.shape": shape},
    )
    check_argument(
        shape[-1] == shape[-2],
        f"The last two dimensions of {operator_name} must be equal.",
        {operator_name: operator},
        extras={f"{operator_name}.shape": shape},
    )


def check_square_pwc_or_stf(pwc_or_stf, pwc_or_stf_name):
    """
    Checks that the Pwc or Stf is a square matrix, or batch of square matrices.

    Parameters
    ----------
    pwc_or_stf : Pwc or Stf
        The pwc_or_stf to be tested.
    pwc_or_stf_name : str
        The name of the `pwc_or_stf`, used for error messages.
    """
    check_argument(
        isinstance(pwc_or_stf, (Pwc, Stf)),
        f"The {pwc_or_stf_name} must be a Pwc or an Stf.",
        {pwc_or_stf_name: pwc_or_stf},
    )

    check_argument(
        len(pwc_or_stf.value_shape) == 2,
        f"The value of {pwc_or_stf_name} must be a matrix, or batch of matrices.",
        {pwc_or_stf_name: pwc_or_stf},
    )
    check_argument(
        pwc_or_stf.value_shape[0] == pwc_or_stf.value_shape[1],
        f"The value of {pwc_or_stf_name} must be a square matrix, or batch of square matrices.",
        {pwc_or_stf_name: pwc_or_stf},
    )


def check_optimization_variable_parameters(
    initial_values, count, lower_bound, upper_bound
):
    """
    Checks that the initial values for optimization variables are valid.

    Parameters
    ----------
    initial_values : list[np.ndarray] or np.ndarray
        Initial values to be checked.
    count : int
        The number of optimization variables.
    lower_bound : float
        The lower bound of initial values.
    upper_bound : float
        The upper bound of initial values.
    """
    check_argument(count > 0, "count must be positive.", {"count": count})
    check_argument(
        upper_bound > lower_bound,
        "lower_bound must be less than upper_bound.",
        {"lower_bound": lower_bound, "upper_bound": upper_bound},
    )

    def _check_value_array(value_array):
        check_argument(
            isinstance(value_array, np.ndarray) and len(value_array.shape) == 1,
            "Initial values must be a 1D array or a list of 1D arrays.",
            {"initial_values": initial_values, "upper bound": upper_bound},
        )
        check_argument(
            value_array.shape[0] == count,
            "Initial values must have the same length as count.",
            {"initial_values": initial_values, "count": count},
        )

        check_argument(
            np.all(value_array >= lower_bound),
            "Initial values must not be smaller than the lower bound.",
            {"initial_values": initial_values, "lower_bound": lower_bound},
        )
        check_argument(
            np.all(value_array <= upper_bound),
            "Initial values must not be greater than the upper bound.",
            {"initial_values": initial_values, "upper_bound": upper_bound},
        )

    if initial_values is not None:
        if isinstance(initial_values, list):
            for value in initial_values:
                _check_value_array(value)
        else:
            _check_value_array(initial_values)
