# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check that a vault token exists and is accepted by the vault.
"""

import os
import sys

import requests

from ..cli import IgwnMonitorArgumentParser

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"
__version__ = "1.0.0"


def check_token(
    path,
    vault,
    scopes=None,
    audience=None,
    warning=0,
    critical=0,
    timeout=30.,
):
    # load the token
    try:
        with open(path, "r") as file:
            token = file.read().strip()
    except Exception as exc:
        return 2, str(exc)

    try:
        resp = requests.get(
            f"https://{vault}:8200/v1/auth/token/lookup-self",
            headers={
                "X-Vault-Token": token,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        details = resp.json()
    except requests.HTTPError as exc:
        resp = exc.response
        return 2, f"'{resp.status_code} {resp.reason}' from {resp.request.url}"
    except requests.RequestException as exc:
        return 2, str(exc)

    remaining = details["data"]["ttl"]
    message = os.linesep.join((
        f"Vault token is valid ({remaining}s remaining)",
        f"Issue time  : {details['data']['issue_time']}",
        f"Duration    : {details['data']['creation_ttl']}",
        f"Expire time : {details['data']['expire_time']}",
        f"Policies    : {', '.join(sorted(details['data']['policies']))}",
    ))

    if remaining <= critical:
        return 2, message
    if remaining <= warning:
        return 1, message
    return 0, message


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
        add_timeout=True,
    )
    parser.add_argument(
        "-f",
        "--token-file",
        required=True,
        help=(
            "file from which to read token, if not given WLCG Beare "
            "Token Discovery protocol is used"
        ),
    )
    parser.add_argument(
        "-a",
        "--vault-host",
        required=True,
        help="hostname for vault",
    )
    parser.add_argument(
        "-w",
        "--timeleft-warning",
        default=0,
        type=float,
        help="warning threshold (seconds) on token time remaining",
    )
    parser.add_argument(
        "-c",
        "--timeleft-critical",
        default=0,
        type=float,
        help="critical threshold (seconds) on token time remaining",
    )

    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)
    status, message = check_token(
        path=opts.token_file,
        vault=opts.vault_host,
        timeout=opts.timeout,
        warning=opts.timeleft_warning,
        critical=opts.timeleft_critical,
    )
    print(message)
    return status


if __name__ == "__main__":
    sys.exit(main())
