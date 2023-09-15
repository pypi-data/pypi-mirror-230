import sys
from collections import UserList
from dataclasses import MISSING, asdict, dataclass, fields
from typing import (
    Any,
    ClassVar,
    Dict,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    SupportsIndex,
    Tuple,
    Union,
    overload,
)

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

__all__ = [
    "Gitmoji",
    "GitmojiList",
]


@dataclass(frozen=True, eq=True)
class Gitmoji:
    emoji: str
    entity: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None
    semver: Optional[Literal["major", "minor", "patch"]] = None

    @classmethod
    def from_dict(cls, __dict: Dict[str, Any], /, *, strict: bool = False) -> Self:
        for field in fields(cls):
            if field.default is MISSING and field.name not in __dict:
                raise TypeError(
                    f"missing key-value pair for required field {field.name!r}."
                )
        if not strict:
            __dict = {
                name: value
                for name, value in __dict.items()
                if name in cls.__dataclass_fields__
            }
        return cls(**__dict)

    def to_dict(self, *, skip_defaults: bool = False) -> Dict[str, Any]:
        fields_dict = asdict(self)
        if skip_defaults:
            fields_dict = {
                field_name: field_value
                for (field_name, field_value), field in zip(
                    fields_dict.items(), fields(self)
                )
                # Include required fields and ...
                if field.default is MISSING
                # ... optional fields with non-default values
                or (field.default is not MISSING and field_value != field.default)
            }
        return fields_dict


class GitmojiList(UserList[Gitmoji]):
    index_fields: ClassVar[Tuple[str, ...]] = (
        "emoji",
        "entity",
        "code",
        "description",
        "name",
    )

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        for index_field in cls.index_fields:
            if index_field not in Gitmoji.__dataclass_fields__:
                raise ValueError(
                    f"{index_field!r} is not a name of {Gitmoji.__name__} field."
                )

    def __init__(self, __data: Optional[Sequence[Gitmoji]] = None, /) -> None:
        super().__init__(__data)

        if not self.data:
            return

        for index, item in enumerate(self.data):
            if not isinstance(item, Gitmoji):
                raise TypeError(
                    f"all items of {self.__class__.__name__} data must be of type "
                    f"{Gitmoji.__name__}; item {index} is {type(item).__name__}."
                )

        for index_field in self.__class__.index_fields:
            field_values = list(filter(None, self.iter_field(index_field)))
            if len(field_values) > len(set(field_values)):
                raise ValueError(f"duplicates found in {index_field!r} field.")

    @property
    def gitmojis(self) -> List[Gitmoji]:
        return self.data

    @overload
    def __getitem__(self, __index: str, /) -> Gitmoji:
        ...

    @overload
    def __getitem__(self, __index: SupportsIndex, /) -> Gitmoji:
        ...

    @overload
    def __getitem__(self, __index: slice, /) -> Self:
        ...

    def __getitem__(self, __index: Union[str, SupportsIndex, slice], /) -> Union[Gitmoji, Self]:  # fmt: skip
        if isinstance(__index, str):
            for gitmoji, index_fields in zip(
                self.gitmojis, self.iter_fields(*self.__class__.index_fields)
            ):
                if __index in index_fields:
                    return gitmoji
            raise IndexError(
                f"{__index!r} is not a value of any of index fields in the list data."
            )
        elif isinstance(__index, int):
            return self.gitmojis[__index]
        elif isinstance(__index, slice):
            return self.__class__(self.gitmojis[__index])
        raise TypeError(
            f"index must be a str, an int, or a slice, not {type(__index).__name__}."
        )

    def iter_field(self, __field_name: str, /) -> Iterator[Optional[str]]:
        return iter([getattr(gitmoji, __field_name) for gitmoji in self.gitmojis])

    def iter_fields(self, *__field_names: str) -> Iterator[Tuple[Optional[str], ...]]:
        if not __field_names:
            __field_names = tuple(field.name for field in fields(Gitmoji))
        return zip(*(self.iter_field(field) for field in __field_names))
