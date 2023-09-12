# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check the status of a GWOSC server
"""

import json
import os

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    DEFAULT_REQUEST_TIMEOUT,
    make_url,
    response_performance,
)
from ..utils import (
    NagiosStatus,
    format_performance_metrics,
)

DEFAULT_API_PATH = "/eventapi/json/"


def check_gwosc_eventapi(
    host,
    path=DEFAULT_API_PATH,
    timeout=DEFAULT_REQUEST_TIMEOUT,
):
    """Ping a GWOSC server and evaluate the reponse status.
    """
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

    detail = os.linesep.join((
        "Datasets:",
        "  " + "{os.linesep}  ".join(sorted(data)),
    ))

    metrics = response_performance(resp)
    metrics.update({
        "num_releases": len(data),
    })

    if "GWTC-3-confident" in data:
        message = "GWOSC server seems OK"
        status = NagiosStatus.OK
    else:
        message = "GWTC-3-confident not in list of releases"
        status = NagiosStatus.WARNING
    message += "|" + format_performance_metrics(metrics)

    return status, message, detail


def create_parser():
    """Create an argument parser for this script.
    """
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
        add_timeout=True,
    )
    parser.add_argument(
        "-H",
        "--hostname",
        default="localhost",
        help="hostname of Mattermost instance",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=DEFAULT_API_PATH,
        help="path on host to query",
    )
    return parser


def main(args=None):
    """Run the thing.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    code, message, detail = check_gwosc_eventapi(
        opts.hostname,
        opts.path,
        timeout=opts.timeout,
    )
    print(message)
    if detail:
        print(detail)
    return code
