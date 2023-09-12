# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check the status of a Hashicorp Vault server

See https://developer.hashicorp.com/vault/api-docs/system/health
for details of the API endpoint used, including the various status
code values for different cluster nodes.
"""

import json

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus

DEFAULT_API_PATH = "/v1/sys/health"
DEFAULT_PORT = 8200

VAULT_STATES = {
    200: (NagiosStatus.OK, "Vault ready"),
    429: (NagiosStatus.WARNING, "Vault in standby"),
    472: (NagiosStatus.WARNING, "Vault in disaster recovery mode"),
    473: (NagiosStatus.WARNING, "Vault in performance standy"),
    501: (NagiosStatus.CRITICAL, "Vault not initialised"),
    503: (NagiosStatus.CRITICAL, "Vault sealed"),
}


def check_vault(
    host,
    port=DEFAULT_PORT,
    path="/",
    api=DEFAULT_API_PATH,
    expected_code=200,
    timeout=10,
):
    """Check the health of a Hashicorp vault server.
    """
    url = make_url(f"{host.rstrip('/')}:{port}", path, api)

    # make the request
    try:
        resp = requests.get(
            url,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        # failed to connect
        return (
            NagiosStatus.CRITICAL,
            str(exc),
            None,
        )

    # try to decode the JSON first, because the API uses
    # the HTTP status code to encode state information,
    # see https://developer.hashicorp.com/vault/api-docs/system/health
    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        # report JSON issue
        return (
            NagiosStatus.WARNING,
            "Failed to parse JSON from API query",
            str(exc),
        )

    detail = (
        "Health API response:\n"
        + json.dumps(data, indent=2)
    )

    # map the HTTP code to a plugin status
    try:
        status, message = VAULT_STATES[resp.status_code]
    except KeyError:
        # check the response
        try:
            resp.raise_for_status()
        except requests.RequestException as exc:
            return (NagiosStatus.CRITICAL, str(exc), None)
        status = NagiosStatus.UNKNOWN
        message = f"Unknown status ({resp.status_code})"

    # if the code we got is what we expected, things are OK
    if resp.status_code == expected_code:
        status = NagiosStatus.OK

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
        default="/",
        help="path on host to query",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="path to use when connecting to the vault server",
    )
    parser.add_argument(
        "-c",
        "--expected-code",
        default=200,
        type=int,
        help="the status code that is expected",
    )
    return parser


def main(args=None):
    """Run the thing.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)
    code, message, detail = check_vault(
        opts.hostname,
        path=opts.path,
        port=opts.port,
        expected_code=opts.expected_code,
        timeout=opts.timeout,
    )

    print(message)
    if detail:
        print(detail)
    return code.value
