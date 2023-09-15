from datetime import date, datetime
from typing import Optional, Union
from uuid import uuid4

import pytest

from mesh_common import is_optional, optional_origin_type
from mesh_common.text import Colors, Modifiers, colored_text


class _TestClass:
    pass


@pytest.mark.parametrize(
    "test_type, expected",
    [
        (int, False),
        (bool, False),
        (str, False),
        (bytes, False),
        (datetime, False),
        (date, False),
        (_TestClass, False),
        (Union[None, int], True),
        (Union[None, bool], True),
        (Optional[int], True),
        (Optional[bool], True),
        (Union[int, None], True),
        (Union[_TestClass, None], True),
        (Union[int, None, str], False),
        (Union[_TestClass, None, int], False),
        (Union[int, str], False),
        (Union[int, int], False),
    ],
)
def test_is_optional(test_type: type, expected: bool):

    assert is_optional(test_type) == expected, repr(test_type)


@pytest.mark.parametrize(
    "test_type, expected",
    [
        (int, int),
        (_TestClass, _TestClass),
        (Union[None, int], int),
        (Union[None, bool], bool),
        (Optional[int], int),
        (Optional[bool], bool),
        (Union[int, None], int),
        (Union[_TestClass, None], _TestClass),
        (Union[int, None, str], Union[int, None, str]),
        (Union[_TestClass, None, int], Union[_TestClass, None, int]),
        (Union[int, str], Union[int, str]),
        (Union[int, int], Union[int, int]),
        (Union[int, int, None], int),
    ],
)
def test_get_optional_origin_type(test_type: type, expected: type):

    assert optional_origin_type(test_type) == expected, repr(test_type)


def test_get_color_text():
    text = uuid4().hex
    red_text = colored_text(text, Colors.red)
    assert red_text == f"\033[31m{text}\033[0m"


def test_get_bold_green_flashing_text():
    text = uuid4().hex
    red_text = colored_text(text, Colors.green, Modifiers.bold, Modifiers.flash)
    assert red_text == f"\033[32;1;5m{text}\033[0m"


def test_get_bold_text():
    text = uuid4().hex
    red_text = colored_text(text, Colors.red, Modifiers.bold)
    assert red_text == f"\033[31;1m{text}\033[0m"


def test_get_bold_italic_text():
    text = uuid4().hex
    red_text = colored_text(text, Colors.red, Modifiers.bold, Modifiers.italic)
    assert red_text == f"\033[31;1;3m{text}\033[0m"
