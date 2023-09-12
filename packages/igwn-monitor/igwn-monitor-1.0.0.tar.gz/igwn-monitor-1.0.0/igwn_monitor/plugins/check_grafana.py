# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Query a the Health API of a Grafana instance
and report status in nagios format.
"""

import json
import os

import requests

from ..cli import IgwnMonitorArgumentParser
from ..http import (
    get_with_auth,
    make_url,
    response_message,
)
from ..utils import (
    NagiosStatus,
)

HEALTH_API_PATH = "api/health"


def check_grafana(
    host,
    path="/",
    api=HEALTH_API_PATH,
    timeout=30.,
    auth_type="none",
    **request_kw,
):
    url = make_url(host, path or "", api)

    try:
        resp = get_with_auth(
            auth_type,
            url,
            timeout=timeout,
            **request_kw,
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        return NagiosStatus.CRITICAL, response_message(exc.response), str(exc)
    except requests.RequestException as exc:
        return NagiosStatus.CRITICAL, str(exc), None

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return (
            NagiosStatus.WARNING,
            "Failed to parse JSON from API query",
            resp.text,
        )

    detail = os.linesep.join((
        "Health API response:",
    ) + tuple(f"  {k}: '{v}'" for (k, v) in data.items()))

    try:
        dbhealth = data["database"].upper()
        if dbhealth == "FAILING":
            code = NagiosStatus.CRITICAL
        else:
            code = NagiosStatus[dbhealth.upper()]
    except KeyError:
        return (
            NagiosStatus.UNKNOWN,
            "Unable to parse database health",
            detail,
        )

    message = f"Grafana Health {dbhealth}"
    return code, message, detail


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
        action="store",
        required=True,
        help="URI of grafana instance",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=None,
        help="path on vhost of grafana app",
    )
    parser.add_auth_argument_group(auth_type="saml")
    return parser


def main(args=None):
    """Run the thing.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    code, message, detail = check_grafana(
        opts.hostname,
        path=opts.path,
        timeout=opts.timeout,
        auth_type=opts.auth_type,
        idp=opts.identity_provider,
        kerberos=opts.kerberos,
        kerberos_keytab=opts.kerberos_keytab,
        kerberos_principal=opts.kerberos_principal,
    )

    print(message)
    if detail:
        print(detail)
    return code.value
