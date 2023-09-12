# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check a token issuer, vaguely.
"""

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
        add_timeout=True,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        help="host name of SciToken issuer",
    )
    parser.add_argument(
        "-n",
        "--issuer-name",
        help="name of SciToken issuer",
    )
    return parser


def get_keys(host, issuer, timeout=10., **request_kw):
    config_url = make_url(host, issuer, "/.well-known/openid-configuration")

    with requests.Session() as sess:
        # pull down the OpenID configuration
        resp = sess.get(config_url, timeout=timeout, **request_kw)
        resp.raise_for_status()
        conf = resp.json()
        resp.close()

        # then pull down the list of issuer keys
        jwks_uri = conf["jwks_uri"]
        resp = sess.get(jwks_uri, timeout=timeout, **request_kw)
        resp.raise_for_status()
        return resp.json()["keys"]


def check_scitoken_issuer(host, issuer, timeout=10.):
    try:
        issuer_keys = get_keys(host, issuer, timeout=timeout)
    except requests.RequestException as exc:
        return (
            NagiosStatus.CRITICAL,
            str(exc),
            None,
        )

    nkeys = len(issuer_keys)
    metrics = format_performance_metrics({
        "issuer_keys": (nkeys, 0, None, 0, None),
    })
    message = f"Issuer UP, {nkeys} keys available|{metrics}"

    if not nkeys:
        return NagiosStatus.WARNING, message, None
    return NagiosStatus.OK, message, None


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    status, message, detail = check_scitoken_issuer(
        opts.hostname,
        opts.issuer_name,
        timeout=opts.timeout,
    )
    print(message)
    if detail:
        print(detail)
    return status
