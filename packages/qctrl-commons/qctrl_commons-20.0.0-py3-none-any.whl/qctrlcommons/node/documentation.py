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
Tools for organizing the graph documentation.
"""

from dataclasses import dataclass
from enum import (
    Enum,
    auto,
)
from typing import (
    Dict,
    List,
)


@dataclass
class DocumentationSection:
    """
    A section of the graphs documentation.

    Parameters
    ----------
    title : str
        The title of the section.
    description : str
        The description of the section.
    operations : str
        The names of the operations to be listed in the section.
    subsections : list[DocumentationSection]
        The subsections that should be nested inside the section.
    """

    title: str
    description: str
    operations: List[str]
    subsections: List["DocumentationSection"]


class Category(Enum):
    """
    The different categories of graph operations.
    """

    ARITHMETIC_FUNCTIONS = auto()
    BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS = auto()
    BUILDING_SMOOTH_HAMILTONIANS = auto()
    DEPRECATED_OPERATIONS = auto()
    FILTERING_AND_DISCRETIZING = auto()
    LARGE_SYSTEMS = auto()
    LINEAR_ALGEBRA = auto()
    MATH = auto()
    MANIPULATING_TENSORS = auto()
    MOLMER_SORENSEN = auto()
    OPTIMAL_AND_ROBUST_CONTROL = auto()
    OPTIMIZATION_VARIABLES = auto()
    OTHER_OPERATIONS = auto()
    QUANTUM_INFORMATION = auto()
    RANDOM_OPERATIONS = auto()
    TIME_EVOLUTION = auto()
    SIGNALS = auto()


def create_documentation_sections(
    operations: Dict[str, List[Category]]
) -> List[DocumentationSection]:
    """
    Create sections containing the full operations documentation.

    Parameters
    ----------
    operations : dict[str, list[Category]]
        The operations and their associated categories.

    Returns
    -------
    list[DocumentationSection]
        A list of objects describing the top-level operations documentation sections. Each category
        appears exactly once in the nested structure of sections.
    """
    excluded_node_names = ["getattr", "getitem"]
    categories_map: Dict[Category, List[str]] = {category: [] for category in Category}

    for name, categories in sorted(operations.items()):
        for category in categories:
            if name not in excluded_node_names:
                categories_map[category].append(name)

    sections = [
        DocumentationSection(
            "Optimization variables",
            "When performing optimizations, you can use these operations to create the optimizable "
            "variables that can be tuned by the optimizer in order to minimize your cost function.",
            categories_map.pop(Category.OPTIMIZATION_VARIABLES),
            [],
        ),
        DocumentationSection(
            "Piecewise-constant tensor functions (PWCs)",
            "You can use these operations to create piecewise-constant functions "
            "either to represent control signals or system Hamiltonians.",
            categories_map.pop(Category.BUILDING_PIECEWISE_CONSTANT_HAMILTONIANS),
            [],
        ),
        DocumentationSection(
            "Sampleable tensor functions (STFs)",
            "You can use these functions to represent time-dependent functions in "
            "Boulder Opal.",
            categories_map.pop(Category.BUILDING_SMOOTH_HAMILTONIANS),
            [],
        ),
        DocumentationSection(
            "Filtering and discretizing",
            "You can use these functions to filter or resample the control signals.",
            categories_map.pop(Category.FILTERING_AND_DISCRETIZING),
            [],
        ),
        DocumentationSection(
            "Predefined signals",
            "You can use these operations to create common analytical signals. "
            "\n\nFor creating analytical signals not bound to a graph see the "
            ":ref:`Signal library` module.",
            categories_map.pop(Category.SIGNALS),
            [],
        ),
        DocumentationSection(
            "Quantum information",
            "You can use these operations to calculate common operations and metrics "
            "from quantum information theory.",
            categories_map.pop(Category.QUANTUM_INFORMATION),
            [],
        ),
        DocumentationSection(
            "Time evolution",
            "You can use these operations to calculate the time evolution of your open or closed "
            "quantum system, either for simulations or optimizations.",
            categories_map.pop(Category.TIME_EVOLUTION),
            [],
        ),
        DocumentationSection(
            "Optimal and robust control",
            "You can use these operations, together with the operations for creating "
            ":ref:`optimization variables<Optimization variables>` "
            "to define convenient cost functions for optimal and robust control.",
            categories_map.pop(Category.OPTIMAL_AND_ROBUST_CONTROL),
            [],
        ),
        DocumentationSection(
            "Large systems",
            "You can use these operations to build graphs that efficiently handle "
            "large quantum systems.",
            categories_map.pop(Category.LARGE_SYSTEMS),
            [],
        ),
        DocumentationSection(
            "Mølmer–Sørensen gates",
            "You can use these operations to efficiently model systems described by "
            "Mølmer–Sørensen interactions.",
            categories_map.pop(Category.MOLMER_SORENSEN),
            [],
        ),
        DocumentationSection(
            "Random operations",
            "You can use these operations to create random quantities, which take different values "
            "each time they are evaluated. These operations are most useful in simulations and "
            "stochastic optimizations.",
            categories_map.pop(Category.RANDOM_OPERATIONS),
            [],
        ),
        DocumentationSection(
            "Manipulating tensors",
            "You can use these operations to manipulate the structures of tensors.",
            categories_map.pop(Category.MANIPULATING_TENSORS),
            [],
        ),
        DocumentationSection(
            "Arithmetic", "", categories_map.pop(Category.ARITHMETIC_FUNCTIONS), []
        ),
        DocumentationSection(
            "Linear algebra", "", categories_map.pop(Category.LINEAR_ALGEBRA), []
        ),
        DocumentationSection(
            "Basic mathematical functions", "", categories_map.pop(Category.MATH), []
        ),
        DocumentationSection(
            "Other operations",
            "You typically do not need to use these operations directly.",
            categories_map.pop(Category.OTHER_OPERATIONS),
            [],
        ),
        DocumentationSection(
            "Deprecated operations",
            "These operations are deprecated and will be removed in the future.",
            categories_map.pop(Category.DEPRECATED_OPERATIONS),
            [],
        ),
    ]
    # Verify that we dealt with all the categories.
    assert not categories_map
    return sections
