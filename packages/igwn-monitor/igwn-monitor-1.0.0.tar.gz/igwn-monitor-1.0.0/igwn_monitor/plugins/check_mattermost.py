# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check the status of a Mattermost server
"""

import requests
from requests.compat import json

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus

DEFAULT_PING_PATH = "/api/v4/system/ping"


def check_mattermost(url, timeout=30.):
    """Ping a Mattermost server and evaluate the reponse status.
    """
    try:
        resp = requests.get(
            url,
            timeout=timeout,
        )
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

    # parse the JSON to determine the Mattermost service status
    status = data['status'].upper()
    statstr = f"Mattermost service {status}"
    message = (
        "Ping API response:\n"
        + json.dumps(data, indent=2)
    )

    if status == "UNHEALTHY":
        return NagiosStatus.WARNING, statstr, message
    if status == "FAIL":
        return NagiosStatus.CRITICAL, statstr, message
    try:
        return NagiosStatus[status], statstr, message
    except KeyError:
        return NagiosStatus.UNKNOWN, statstr, message


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
        default="api/v4/system/ping",
        help="path on host to query",
    )
    return parser


def main(args=None):
    """Run the thing.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    url = make_url(opts.hostname, opts.path)
    code, message, detail = check_mattermost(
        url,
        timeout=opts.timeout,
    )

    print(message)
    if detail:
        print(detail)
    return code
