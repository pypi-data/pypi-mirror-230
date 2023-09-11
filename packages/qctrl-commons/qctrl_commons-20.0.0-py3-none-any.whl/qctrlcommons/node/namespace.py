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
Module for primary node namespaces.
"""
from __future__ import annotations

import inspect
import sys
from dataclasses import dataclass

from qctrlcommons.node.base import Node


@dataclass
class _PrimaryNamespaceDoc:
    """
    A helper class for building the doc for the primary node namespaces.
    """

    namespace_name: str
    sub_nodes: dict
    categories: list


def create_namespace_doc(
    namespace_name, module_name, categories, node_name_formatter=lambda x: x
):
    """
    Create a _PrimaryNamespaceDoc given a namespace name, the name of the module
    and a list of categories.
    """
    # Collect the `sub_nodes`.
    sub_nodes = {}
    for _, obj in inspect.getmembers(sys.modules[module_name]):
        if (
            inspect.isclass(obj)
            and obj.__module__ == module_name
            and issubclass(obj, Node)
        ):
            new_name = node_name_formatter(obj.name)
            sub_nodes[new_name] = obj.create_graph_method()
    return _PrimaryNamespaceDoc(namespace_name, sub_nodes, categories)
