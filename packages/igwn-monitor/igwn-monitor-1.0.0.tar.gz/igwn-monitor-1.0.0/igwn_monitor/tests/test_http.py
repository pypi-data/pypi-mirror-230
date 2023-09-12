# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Tests for :mod:`igwn_monitor.http`.
"""

import pytest

from .. import http


@pytest.mark.parametrize(("args", "kwargs", "result"), [
    # just a host name
    (
        ("example.com",),
        {},
        "https://example.com",
    ),
    # host specifies scheme
    (
        ("http://example.com",),
        {},
        "http://example.com",
    ),
    # host including port
    (
        ("example.com:80",),
        {},
        "http://example.com:80",
    ),
    # paths
    (
        ("example.com", "path", "path2"),
        {},
        "https://example.com/path/path2",
    ),
    # host including path
    (
        ("example.com/path", "path2"),
        {},
        "https://example.com/path/path2",
    ),
    # host including port and path
    (
        ("example.com:80/path", "path2"),
        {},
        "http://example.com:80/path/path2",
    ),
    # kwargs
    (
        ("example.com", "path", "path2"),
        {"scheme": "imap", "query": "a=1", "fragment": "loc"},
        "imap://example.com/path/path2?a=1#loc",
    ),
])
def test_make_url(args, kwargs, result):
    assert http.make_url(*args, **kwargs) == result
