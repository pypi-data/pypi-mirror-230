import re
import sys
from dataclasses import MISSING, fields
from itertools import chain, combinations

import pytest

from gitmojis.models import Gitmoji, GitmojiList


def get_gitmoji_fields_powerset():
    gitmoji_fields = fields(Gitmoji)

    return chain.from_iterable(
        combinations(gitmoji_fields, r) for r in range(1, len(gitmoji_fields) + 1)
    )


def test_gitmoji_from_dict_with_valid_data(gitmoji_dict):
    gitmoji = Gitmoji.from_dict(gitmoji_dict)

    assert isinstance(gitmoji, Gitmoji)


def test_gitmoji_from_dict_with_required_field_missing(mocker, gitmoji_dict):
    mocker.patch.dict(
        gitmoji_dict,
        {
            field.name: gitmoji_dict[field.name]
            for field in fields(Gitmoji)
            if field.default is not MISSING
        },
        clear=True,
    )

    with pytest.raises(
        TypeError,
        match=(
            rf"missing key-value pair for required field "
            rf"'({'|'.join(field.name for field in fields(Gitmoji) if field.default is MISSING)})'."
        ),
    ):
        Gitmoji.from_dict(gitmoji_dict)


def test_gitmoji_from_dict_with_non_field_data_if_strict_mode(mocker, gitmoji_dict):
    mocker.patch.dict(gitmoji_dict, {"does_not_exist": None})

    with pytest.raises(
        TypeError,
        match=re.escape(
            f"{f'{Gitmoji.__name__}.' if sys.version_info >= (3, 10) else ''}"
            f"__init__() got an unexpected keyword argument 'does_not_exist'"
        ),
    ):
        Gitmoji.from_dict(gitmoji_dict, strict=True)


def test_gitmoji_from_dict_with_non_field_data_if_not_strict_mode(mocker, gitmoji_dict):
    mocker.patch.dict(gitmoji_dict, {"does_not_exist": None})

    gitmoji = Gitmoji.from_dict(gitmoji_dict, strict=False)

    assert isinstance(gitmoji, Gitmoji)


def test_gitmoji_to_dict_with_skipping_defaults(gitmoji):
    gitmoji = Gitmoji(
        **{
            field.name: getattr(gitmoji, field.name)
            if field.default is MISSING
            else field.default
            for field in fields(Gitmoji)
        }
    )
    gitmoji_dict = gitmoji.to_dict(skip_defaults=True)

    assert all(
        field.name not in gitmoji_dict
        for field in fields(Gitmoji)
        if field.default is not MISSING
    )


def test_gitmoji_to_dict_with_no_skipping_defaults(gitmoji):
    gitmoji_dict = gitmoji.to_dict(skip_defaults=False)

    assert all(field.name in gitmoji_dict for field in fields(Gitmoji))


def test_gitmoji_list_subclassing_with_invalid_index_fields():
    with pytest.raises(
        ValueError, match="'does_not_exist' is not a name of Gitmoji field."
    ):
        type(
            "GitmojiListSubclass",
            (GitmojiList,),
            {"index_fields": ("does_not_exist",)},
        )


def test_gitmoji_list_subclassing_with_valid_index_fields():
    class GitmojiListSubclass(GitmojiList):
        index_fields = ("emoji", "code")

    assert issubclass(GitmojiListSubclass, GitmojiList)


def test_gitmoji_list_instantiation_with_no_data():
    gitmoji_list = GitmojiList()

    assert gitmoji_list.data == []


def test_gitmoji_list_instantiation_with_valid_data(gitmoji_list):
    gitmoji_list = GitmojiList(gitmoji_list.data)

    assert isinstance(gitmoji_list, GitmojiList)


def test_gitmoji_list_instantiation_with_invalid_data(gitmoji_list):
    with pytest.raises(
        TypeError,
        match=(
            f"all items of {GitmojiList.__name__} data must be of type "
            f"{Gitmoji.__name__}; item {len(gitmoji_list.data)} is str."
        ),
    ):
        GitmojiList(gitmoji_list.data + ["not_a_gitmoji"])


def test_gitmoji_list_instantiation_with_duplicated_data(gitmoji_list):
    with pytest.raises(
        ValueError,
        match=(
            rf"duplicates found in "
            rf"'{'|'.join(field for field in GitmojiList.index_fields)}' field."
        ),
    ):
        GitmojiList(gitmoji_list.data * 2)


@pytest.mark.parametrize("index", GitmojiList.index_fields)
def test_gitmoji_list_indexing_with_str(gitmoji_list, index):
    for gitmoji in gitmoji_list.data:
        indexed_gitmoji = gitmoji_list[getattr(gitmoji, index)]

        assert indexed_gitmoji == gitmoji


def test_gitmoji_list_indexing_with_int(gitmoji_list):
    for index in range(len(gitmoji_list)):
        indexed_gitmoji = gitmoji_list[index]

        assert indexed_gitmoji == gitmoji_list.data[index]


@pytest.mark.parametrize(
    "index",
    [
        slice(2),
        slice(0, 2),
        slice(0, -1, 2),
    ],
    ids=[
        "stop only",
        "start and stop",
        "start, stop, and step",
    ],
)
def test_gitmoji_list_indexing_with_slice(mocker, gitmoji_list, index):
    mocker.patch.object(GitmojiList, "index_fields", ())

    gitmoji_list = GitmojiList(gitmoji_list.data * 3)

    indexed_gitmojis = gitmoji_list[index]

    assert indexed_gitmojis == gitmoji_list.data[index]


def test_gitmoji_list_indexing_with_invalid_str_index(gitmoji_list):
    with pytest.raises(
        IndexError,
        match="'does_not_exist' is not a value of any of index fields in the list data.",
    ):
        gitmoji_list["does_not_exist"]


def test_gitmoji_list_indexing_with_invalid_index_type(gitmoji_list):
    with pytest.raises(
        TypeError, match="index must be a str, an int, or a slice, not NoneType."
    ):
        gitmoji_list[None]


@pytest.mark.parametrize("field_name", [field.name for field in fields(Gitmoji)])
def test_gitmoji_list_iter_field(gitmoji_list, field_name):
    iterator = gitmoji_list.iter_field(field_name)

    assert list(iterator) == [
        getattr(gitmoji, field_name) for gitmoji in gitmoji_list.data
    ]


@pytest.mark.parametrize(
    "gitmoji_fields",
    get_gitmoji_fields_powerset(),
    ids=[
        f"{', '.join(field.name for field in field_names_subset)}"
        for field_names_subset in get_gitmoji_fields_powerset()
    ],
)
def test_gitmoji_list_iter_fields_with_fields_subset(gitmoji_list, gitmoji_fields):
    iterator = gitmoji_list.iter_fields(
        *[gitmoji_field.name for gitmoji_field in gitmoji_fields]
    )

    for item, gitmoji in zip(iterator, gitmoji_list):
        assert item == tuple(getattr(gitmoji, field.name) for field in gitmoji_fields)


def test_gitmoji_list_iter_fields_with_no_fields(gitmoji_list):
    iterator = gitmoji_list.iter_fields()

    for item, gitmoji in zip(iterator, gitmoji_list):
        assert item == tuple(getattr(gitmoji, field.name) for field in fields(Gitmoji))
