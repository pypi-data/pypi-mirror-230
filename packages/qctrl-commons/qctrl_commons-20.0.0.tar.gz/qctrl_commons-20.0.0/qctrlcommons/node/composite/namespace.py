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
Namespaces for functions, nodes, and classes.
"""

from functools import partial

NAMESPACE_ATTR = "namespace_name"
COMPOSITE_ATTR = "composite_node"


def composite_node(categories: list):
    """
    Define a decorator that:
        - Sets a new attribute `composite_node` to True.
        - Sets a new attribute `categories` to a given value.
    """
    assert isinstance(categories, list), "The categories must be a list."

    def _set_node_information(obj, categories):
        setattr(obj, "categories", categories)
        setattr(obj, COMPOSITE_ATTR, True)
        return obj

    return partial(_set_node_information, categories=categories)
