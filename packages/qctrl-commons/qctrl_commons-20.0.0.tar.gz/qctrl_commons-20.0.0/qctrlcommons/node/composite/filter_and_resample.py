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
System-agnostic convenient nodes.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from qctrlcommons.node.composite.namespace import composite_node
from qctrlcommons.node.documentation import Category
from qctrlcommons.node.node_data import (
    ConvolutionKernel,
    Pwc,
)


@composite_node([Category.FILTERING_AND_DISCRETIZING])
def filter_and_resample_pwc(
    graph: "Graph",
    pwc: Pwc,
    kernel: ConvolutionKernel,
    segment_count: int,
    duration: Optional[float] = None,
    name: Optional[str] = None,
) -> Pwc:
    r"""
    Filter a piecewise-constant function by convolving it with a kernel and resample it again.

    Parameters
    ----------
    graph : Graph
        The graph object where the node will belong.
    pwc : Pwc
        The piecewise-constant function :math:`\alpha(t)` to be filtered.
    kernel : ConvolutionKernel
        The node representing the kernel :math:`K(t)`.
    segment_count : int
        The number of segments of the resampled filtered function.
    duration : float or None, optional
        Force the resulting piecewise-constant function to have a certain duration.
        This option is mainly to avoid floating point errors when the total duration is
        too small. Defaults to the sum of segment durations of `pwc`.
    name : str or None, optional
        The name of the node.

    Returns
    -------
    Pwc
        The filtered and resampled piecewise-constant function.

    See Also
    --------
    :func:`Graph.convolve_pwc` :
        Create the convolution of a piecewise-constant function with a kernel.
    :func:`Graph.discretize_stf` :
        Create a piecewise-constant function by discretizing a sampleable function.
    :func:`Graph.sinc_convolution_kernel` :
        Create a convolution kernel representing the sinc function.

    Notes
    -----
    The convolution is

    .. math::
        (\alpha * K)(t) \equiv
        \int_{-\infty}^\infty \alpha(\tau) K(t-\tau) \mathrm{d}\tau.

    Convolution in the time domain is equivalent to multiplication in the
    frequency domain, so this function can be viewed as applying a linear
    time-invariant filter (specified via its time domain kernel :math:`K(t)`)
    to :math:`\alpha(t)`.
    """
    total_duration = duration or np.sum(pwc.durations)

    return graph.discretize_stf(
        stf=graph.convolve_pwc(pwc=pwc, kernel=kernel),
        duration=total_duration,
        segment_count=segment_count,
        name=name,
    )
