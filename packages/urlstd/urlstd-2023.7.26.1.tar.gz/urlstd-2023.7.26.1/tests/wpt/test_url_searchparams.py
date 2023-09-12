# References:
#  https://github.com/web-platform-tests/wpt/blob/dcf353e2846063d4b9e62ec75545d0ea857ef765/url/url-searchparams.any.js

from typing import Optional

import pytest

from urlstd.parse import URL, URLSearchParams


def _b_url(url: str, base: Optional[str] = None) -> URL:
    return URL(url, base if base is not None else "about:blank")


def test_getter():
    """URL.searchParams getter."""
    url = _b_url("http://example.org/?a=b")
    search_params = url.search_params
    assert id(url.search_params) == id(search_params)


def test_updating_clearing():
    """URL.searchParams updating, clearing."""
    url = _b_url("http://example.org/?a=b")
    search_params = url.search_params
    assert str(search_params) == "a=b"

    search_params.set("a", "b")
    assert str(search_params) == "a=b"
    assert url.search == "?a=b"
    url.search = ""
    assert len(str(url.search_params)) == 0
    assert len(url.search) == 0
    assert len(str(search_params)) == 0


def test_setter_invalid_values():
    """URL.searchParams setter, invalid values."""
    urlstring = "http://example.org"
    url = _b_url(urlstring)
    with pytest.raises(AttributeError):
        # readonly property
        url.search_params = URLSearchParams(urlstring)  # type: ignore


def test_setters_update_propagation():
    """URL.searchParams and URL.search setters, update propagation."""
    url = _b_url("http://example.org/file?a=b&c=d")
    search_params = url.search_params
    assert url.search == "?a=b&c=d"
    assert str(search_params) == "a=b&c=d"

    url.search = "e=f&g=h"
    assert url.search == "?e=f&g=h"
    assert str(search_params) == "e=f&g=h"

    url.search = "?e=f&g=h"
    assert url.search == "?e=f&g=h"
    assert str(search_params) == "e=f&g=h"

    search_params.append("i", " j ")
    assert url.search == "?e=f&g=h&i=+j+"
    assert str(url.search_params) == "e=f&g=h&i=+j+"
    assert search_params.get("i") == " j "

    search_params.set("e", "updated")
    assert url.search == "?e=updated&g=h&i=+j+"
    assert search_params.get("e") == "updated"

    url2 = _b_url("http://example.org/file??a=b&c=d")
    assert url2.search == "??a=b&c=d"
    assert str(url2.search_params) == "%3Fa=b&c=d"

    url2.href = "http://example.org/file??a=b"
    assert url2.search == "??a=b"
    assert str(url2.search_params) == "%3Fa=b"
