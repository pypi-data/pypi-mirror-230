# Copyright CNRS/Inria/UNS
# Contributor(s): Eric Debreuve (since 2021)
#
# eric.debreuve@cnrs.fr
#
# This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

from __future__ import annotations

import dataclasses as dtcl
from pathlib import Path as path_t
from types import EllipsisType, UnionType
from typing import Any, Iterable

from conf_ini_g.extension.parser.type_hint import hint_tree_t
from conf_ini_g.extension.type import any_hint_h, none_t


@dtcl.dataclass(slots=True, repr=False, eq=False)
class _value_node_t:
    consolidated: Any
    # Leave elements to the tree


@dtcl.dataclass(slots=True, repr=False, eq=False)
class value_tree_t(_value_node_t):
    elements: tuple[value_tree_t, ...] = None

    @classmethod
    def NewFromValue(cls, value: Any, /) -> value_tree_t:
        """"""
        if isinstance(value, Iterable) and not isinstance(value, str):
            elements = tuple(cls.NewFromValue(_elm) for _elm in value)
            return cls(consolidated=value, elements=elements)

        return cls(consolidated=value)

    def CastValue(
        self, hint_tree: hint_tree_t, /, *, only_check_validity: bool = False
    ) -> tuple[Any, list[str]] | list[str]:
        """"""
        issues = self._CastToHint(hint_tree)
        if issues.__len__() > 0:
            if only_check_validity:
                return issues
            else:
                return None, issues

        if only_check_validity:
            return []
        else:
            return self.consolidated, []

    def _CastToHint(self, hint_node: hint_tree_t, /) -> list[str]:
        """
        Returned value=the value tree has been successfully cast to the hint tree
        specification, or not.
        """
        hn_type = hint_node.type
        hn_elements = hint_node.elements

        if hn_type is Any:
            return self._CompliesWithAnnotations(hint_node)

        if hn_type is none_t:
            # None is not supposed to have annotations. They are ignored if it does.
            if self.consolidated is None:
                output = []
            else:
                output = [f"{self.consolidated}: Invalid value; Expected=None."]
            return output

        if hn_type is UnionType:
            output = []
            for element in hn_elements:
                issues = self._CastToHint(element)
                if issues.__len__() > 0:
                    output.extend(issues)
                else:
                    return []
            return output

        if not isinstance(self.consolidated, hn_type):
            # Dealing with "equivalent" types first, such as "str" and "pathlib.Path".
            if issubclass(hn_type, path_t):
                try:
                    self.consolidated = hn_type(self.consolidated)
                    output = []
                except:
                    output = [
                        f"{self.consolidated}: Cannot be cast to type "
                        f'"{hn_type.__name__}".'
                    ]
                return output
            else:
                return [
                    f"{self.consolidated}: Invalid value type "
                    f'"{type(self.consolidated).__name__}"; '
                    f'Expected="{hn_type.__name__}".'
                ]
            # cast_value, success = SimplyCastValue(self.consolidated, hn_type)
            # if success:
            #     self.consolidated = cast_value
            # else:
            #     return [
            #         f'{self.consolidated}: Cannot be cast to type "{hn_type.__name__}".'
            #     ]

        if (self.elements is None) and (hn_elements is None):
            # self.consolidated has been cast above by "SimplyCastValue" if needed.
            return self._CompliesWithAnnotations(hint_node)

        if (self.elements is None) and (hn_elements is not None):
            return [
                f"{self.consolidated}: Not a container value; "
                f"Expected=Container with template {hint_node.template_as_str}."
            ]

        # For then on, self.elements is not None.

        if hn_elements is None:
            # The type hint does not fully specify valid values, so anything is valid.
            # self.consolidated has been cast above by "SimplyCastValue" if needed.
            return self._CompliesWithAnnotations(hint_node)

        n_value_elements = self.elements.__len__()
        n_hint_elements = hn_elements.__len__()
        has_ellipsis = (n_hint_elements == 2) and (hn_elements[1].type is EllipsisType)
        should_fake_ellipsis = (n_hint_elements == 1) and issubclass(
            hn_type, (list, set)
        )
        if (
            has_ellipsis
            or should_fake_ellipsis
            or (n_value_elements == n_hint_elements)
        ):
            if has_ellipsis or should_fake_ellipsis:
                adjusted_hn_elements = n_value_elements * (hn_elements[0],)
            else:
                adjusted_hn_elements = hn_elements
            issues = []
            for value_elm, hint_elm in zip(self.elements, adjusted_hn_elements):
                value_elm: value_tree_t
                issues.extend(value_elm._CastToHint(hint_elm))
            if issues.__len__() > 0:
                return issues

            # self.consolidated has been cast above by "SimplyCastValue" if needed.
            return self._CompliesWithAnnotations(hint_node)

        return [
            f"{self.consolidated}: Invalid container value; "
            f"Expected=Value following template {hint_node.template_as_str}."
        ]

    def _CompliesWithAnnotations(self, hint_node: hint_tree_t, /) -> list[str]:
        """"""
        output = []

        for annotation in hint_node.annotations:
            output.extend(annotation.ValueIsCompliant(self.consolidated))

        return output


# def SimplyCastValue(value: Any, expected_type: simple_hint_h, /) -> tuple[Any, bool]:
#     """
#     Works for string interpretation (e.g., value == "1.0" and expected_type is float),
#     or compatible type conversion (e.g., value == 1 and expected_type is float).
#
#     If value is a string, the expected type might be instantiable from it, e.g.
#     float("1.0"). However, a success does not mean that the interpretation is valid,
#     e.g. tuple("(1, 2, 3)") which creates a tuple of the characters. To confirm that a
#     success is also a correct interpretation, the string representation of the
#     interpreted value is compared with the original string. Unfortunately, this
#     procedure forbid using 1 for a float value since str(float("1")) == "1.0" != "1".
#     """
#     try:
#         interpreted = expected_type(value)
#         # If "expected_type" is a path and the value has a trailing folder separator,
#         # then the general-purpose test fails. But the conversion is always valid.
#         if issubclass(expected_type, path_t):  # Then value must be a string.
#             success = True
#         else:
#             # Note: str(value) below is "redundant" if already a string.
#             success = str(interpreted).replace(" ", "") == str(value).replace(" ", "")
#     except:
#         interpreted, success = None, False
#
#     return interpreted, success


def CastValue(
    value: Any, hint: any_hint_h | hint_tree_t, /, *, only_check_validity: bool = False
) -> tuple[Any, list[str]] | list[str]:
    """"""
    value_tree = value_tree_t.NewFromValue(value)
    if not isinstance(hint, hint_tree_t):
        hint = hint_tree_t.NewFromTypeHint(hint)

    return value_tree.CastValue(hint, only_check_validity=only_check_validity)
