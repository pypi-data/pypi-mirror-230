"""Implementation of attrs and :mod:`dataclasses` fields and methods.

This is a transitional module for those who want to write code that works across
versions of this library.
"""

import typing
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

if typing.TYPE_CHECKING:
    from binobj.fields.base import Field
    from binobj.structures import Struct


def fields(struct: "Struct") -> List["Field[Any]"]:
    return sorted(struct.__binobj_struct__.components.values(), key=lambda f: f.index)


def asdict(struct: "Struct") -> Dict[str, Any]:
    return {name: struct[name] for name in struct}


def astuple(struct: "Struct") -> Tuple[Any, ...]:
    return tuple(struct[name] for name in struct)
