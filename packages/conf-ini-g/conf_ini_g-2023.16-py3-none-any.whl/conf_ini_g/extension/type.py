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

import dataclasses as dtcl
from types import EllipsisType, GenericAlias, UnionType
from typing import Annotated, Any, ClassVar, Sequence

from rich.text import Text as text_t

from conf_ini_g.extension.string import AlignedOnSeparator

# --- Unannotated hints
# Atoms
generic_hint_h = Any
simple_hint_h = type[Any]
complex_hint_h = GenericAlias | UnionType
# Grouping
non_complex_hint_h = generic_hint_h | simple_hint_h
raw_hint_h = non_complex_hint_h | complex_hint_h
# --- Annotated hints
annotated_hint_t = type(Annotated[object, None])
# --- [Un]Annotated hints
any_hint_h = raw_hint_h | annotated_hint_t
# --- Complex hints additional components:
#     - EllipsisType for GenericAlias, as in: tuple[int, ...]
#     - None for UnionType, as in: int | None
complex_hint_additions_h = EllipsisType | None


class none_t:  # To play the role of NoneType
    pass


@dtcl.dataclass(slots=True, repr=False, eq=False)
class annotation_t:
    ACCEPTED_TYPES: ClassVar[tuple[non_complex_hint_h, ...]] = (Any,)

    @classmethod
    def NewAnnotatedType(cls, *args, **kwargs) -> annotated_hint_t:
        """
        Recommendation: Should only be implemented if ACCEPTED_TYPES contains a single
        type, thus avoiding to use:
        Annotated[there_is_no_other_choice_then_single_accepted_type, annotation_t(...)]
        and using:
        annotation_t.NewAnnotatedType(...)
        instead.
        """
        raise NotImplementedError

    def Issues(self) -> list[str]:
        """"""
        return []

    def ValueIsCompliant(self, _: Any, /) -> list[str]:
        """"""
        return []

    def __str__(self) -> str:
        """"""
        return text_t.from_markup(self.__rich__()).plain

    def __rich__(self) -> str:
        """"""
        output = [TypeAsRichStr(self)]

        names = (_fld.name for _fld in dtcl.fields(self))
        for name in names:
            value = getattr(self, name)
            output.append(f"    {NameValueTypeAsRichStr(name, value, separator='@=@')}")

        output = AlignedOnSeparator(output, "@=@", " = ")

        return "\n".join(output)


def IsAnnotated(hint: any_hint_h, /) -> bool:
    """"""
    return isinstance(hint, annotated_hint_t)


def TypeOfAnnotatedHint(annotated_hint: annotated_hint_t, /) -> raw_hint_h:
    """"""
    return annotated_hint.__args__[0]


def AnnotationsOfAnnotatedHint(annotated_hint: annotated_hint_t, /) -> tuple[Any, ...]:
    """"""
    output = tuple(annotated_hint.__metadata__)
    if all(isinstance(_elm, annotation_t) for _elm in output):
        return output

    raise ValueError(
        f'{output}: Not all elements are of type "{annotation_t.__name__}".'
    )


def HintComponents(hint: any_hint_h, /) -> tuple[raw_hint_h, tuple[Any, ...]]:
    """"""
    if IsAnnotated(hint):
        return TypeOfAnnotatedHint(hint), AnnotationsOfAnnotatedHint(hint)

    return hint, ()


def TypeAsRichStr(value: Any, /, *, prefix: str = "") -> str:
    """
    Richer alternative (however, causes troubles with packages like TensorFlow):
    Additional parameter: relative_to_home: bool = True
    from conf_ini_g.extension.python import SpecificationPath
    return (
        f"[bold magenta]{type(instance).__name__}[/]"
        f"[gray]@"
        f"{SpecificationPath(type(instance), relative_to_home=relative_to_home)}:[/]"
    )
    """
    return f"[yellow]{prefix}{type(value).__name__}[/]"


def NameValueTypeAsRichStr(name: str, value: Any, /, *, separator: str = "=") -> str:
    """"""
    formatted_type = TypeAsRichStr(value, prefix=":")
    if isinstance(value, Sequence) and (value.__len__() == 0):
        value = "[cyan]<empty>[/]"

    return f"[blue]{name}{separator}[/]{value}{formatted_type}"
