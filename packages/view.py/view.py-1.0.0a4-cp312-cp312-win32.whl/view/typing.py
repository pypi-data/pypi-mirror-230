from __future__ import annotations

from typing import (Any, Awaitable, Callable, ClassVar, Dict, Generic, List,
                    Tuple, Type, TypeVar, Union)

from typing_extensions import ParamSpec, Protocol, TypedDict

AsgiSerial = Union[
    bytes,
    str,
    int,
    float,
    list,
    tuple,
    Dict[str, "AsgiSerial"],
    bool,
    None,
]

AsgiDict = Dict[str, AsgiSerial]

AsgiReceive = Callable[[], Awaitable[AsgiDict]]
AsgiSend = Callable[[AsgiDict], Awaitable[None]]

ResponseHeaders = Dict[str, str]

_ViewResponseTupleA = Tuple[str, int, ResponseHeaders]
_ViewResponseTupleB = Tuple[int, str, ResponseHeaders]
_ViewResponseTupleC = Tuple[str, ResponseHeaders, int]
_ViewResponseTupleD = Tuple[int, ResponseHeaders, str]
_ViewResponseTupleE = Tuple[ResponseHeaders, str, int]
_ViewResponseTupleF = Tuple[ResponseHeaders, int, str]
_ViewResponseTupleG = Tuple[str, ResponseHeaders]
_ViewResponseTupleH = Tuple[ResponseHeaders, str]
_ViewResponseTupleI = Tuple[str, int]
_ViewResponseTupleJ = Tuple[int, str]

_ViewResponseType = Union[
    _ViewResponseTupleA,
    _ViewResponseTupleB,
    _ViewResponseTupleC,
    _ViewResponseTupleD,
    _ViewResponseTupleE,
    _ViewResponseTupleF,
    _ViewResponseTupleG,
    _ViewResponseTupleH,
    _ViewResponseTupleI,
    _ViewResponseTupleJ,
    str,
]
P = ParamSpec("P")
V = TypeVar("V", bound="ValueType")

ViewResponse = Awaitable[_ViewResponseType]
Context = Any
R = TypeVar("R", bound="ViewResponse")
ViewRoute = Callable[P, R]

ValidatorResult = Union[bool, Tuple[bool, str]]
Validator = Callable[[V], ValidatorResult]

TypeInfo = Tuple[int, Union[Type[Any], None], List["TypeInfo"]]


class RouteInputDict(TypedDict, Generic[V]):
    name: str
    type_codes: list[TypeInfo]
    default: V | None
    validators: list[Validator[V]]
    is_body: bool
    has_default: bool


ViewBody = Dict[str, "ValueType"]


class _SupportsViewBodyCV(Protocol):
    __view_body__: ViewBody


class _SupportsViewBodyF(Protocol):
    def __view_body__(self) -> ViewBody:
        ...


class _SupportsAnnotations(Protocol):
    __annotations__: ClassVar[dict[str, Any]]


SupportsViewBody = Union[_SupportsViewBodyCV, _SupportsViewBodyF]
ViewBodyLike = Union[SupportsViewBody, _SupportsAnnotations]
ValueType = Union[
    ViewBodyLike,
    str,
    int,
    Dict[str, "ValueType"],
    bool,
    float,
    Type[Any],
]
Parser = Callable[[str], ViewBody]


class Part(Protocol[V]):
    name: str
    tp: type[V] | None


Callback = Callable[[], Any]
