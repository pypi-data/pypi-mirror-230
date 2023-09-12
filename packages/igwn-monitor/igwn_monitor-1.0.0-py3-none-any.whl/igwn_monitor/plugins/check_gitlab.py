# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check the GitLab readiness API and report as a plugin.
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import json
import os

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus

DEFAULT_API_PATH = "/-/readiness?all=1"


def check_gitlab(host, path=DEFAULT_API_PATH, timeout=60):
    url = make_url(host, path)
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return (NagiosStatus.CRITICAL, str(exc), None)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return (
            NagiosStatus.WARNING,
            "Failed to parse JSON from API query",
            resp.text,
        )

    try:
        stat = data["status"].upper()
        status = NagiosStatus[stat]
    except KeyError:
        status = NagiosStatus.WARNING
    message = f"Status: {stat}"
    detail = os.linesep.join((
        "Readiness API response:",
        json.dumps(data, indent=2),
    ))
    return status, message, detail


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
        add_timeout=True,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        required=True,
        help="FQDN of GitLab host to check",
    )
    parser.add_argument(
        "-p",
        "--api-path",
        default=DEFAULT_API_PATH,
        help="path of API to query",
    )
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message, detail = check_gitlab(
        opts.hostname,
        opts.api_path,
        timeout=opts.timeout,
    )
    print(message)
    if detail:
        print(detail)
    return status
