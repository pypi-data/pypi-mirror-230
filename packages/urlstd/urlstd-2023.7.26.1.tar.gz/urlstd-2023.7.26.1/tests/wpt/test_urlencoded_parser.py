# References:
#  https://github.com/web-platform-tests/wpt/blob/dcf353e2846063d4b9e62ec75545d0ea857ef765/url/urlencoded-parser.any.js

import pytest

from urlstd.parse import URLSearchParams


@pytest.mark.parametrize(
    "val",
    [
        {"input": "test", "output": [["test", ""]]},
        {"input": "\uFEFFtest=\uFEFF", "output": [["\uFEFFtest", "\uFEFF"]]},
        {
            "input": "%EF%BB%BFtest=%EF%BB%BF",
            "output": [["\uFEFFtest", "\uFEFF"]],
        },
        {"input": "%EF%BF%BF=%EF%BF%BF", "output": [["\uFFFF", "\uFFFF"]]},
        {"input": "%FE%FF", "output": [["\uFFFD\uFFFD", ""]]},
        {"input": "%FF%FE", "output": [["\uFFFD\uFFFD", ""]]},
        {"input": "†&†=x", "output": [["†", ""], ["†", "x"]]},
        {"input": "%C2", "output": [["\uFFFD", ""]]},
        {"input": "%C2x", "output": [["\uFFFDx", ""]]},
        {
            "input": "_charset_=windows-1252&test=%C2x",
            "output": [["_charset_", "windows-1252"], ["test", "\uFFFDx"]],
        },
        {"input": "", "output": []},
        {"input": "a", "output": [["a", ""]]},
        {"input": "a=b", "output": [["a", "b"]]},
        {"input": "a=", "output": [["a", ""]]},
        {"input": "=b", "output": [["", "b"]]},
        {"input": "&", "output": []},
        {"input": "&a", "output": [["a", ""]]},
        {"input": "a&", "output": [["a", ""]]},
        {"input": "a&a", "output": [["a", ""], ["a", ""]]},
        {"input": "a&b&c", "output": [["a", ""], ["b", ""], ["c", ""]]},
        {"input": "a=b&c=d", "output": [["a", "b"], ["c", "d"]]},
        {"input": "a=b&c=d&", "output": [["a", "b"], ["c", "d"]]},
        {"input": "&&&a=b&&&&c=d&", "output": [["a", "b"], ["c", "d"]]},
        {
            "input": "a=a&a=b&a=c",
            "output": [["a", "a"], ["a", "b"], ["a", "c"]],
        },
        {"input": "a==a", "output": [["a", "=a"]]},
        {"input": "a=a+b+c+d", "output": [["a", "a b c d"]]},
        {"input": "%=a", "output": [["%", "a"]]},
        {"input": "%a=a", "output": [["%a", "a"]]},
        {"input": "%a_=a", "output": [["%a_", "a"]]},
        {"input": "%61=a", "output": [["a", "a"]]},
        {"input": "%61+%4d%4D=", "output": [["a MM", ""]]},
        {"input": "id=0&value=%", "output": [["id", "0"], ["value", "%"]]},
        {"input": "b=%2sf%2a", "output": [["b", "%2sf*"]]},
        {"input": "b=%2%2af%2a", "output": [["b", "%2*f*"]]},
        {"input": "b=%%2a", "output": [["b", "%*"]]},
    ],
)
def test_params(val):
    msg = f'URLSearchParams constructed with: {val["input"]!r}'
    test_params.__doc__ = msg

    sp = URLSearchParams(val["input"])
    for i, item in enumerate(sp):
        assert item == tuple(val["output"][i]), msg
