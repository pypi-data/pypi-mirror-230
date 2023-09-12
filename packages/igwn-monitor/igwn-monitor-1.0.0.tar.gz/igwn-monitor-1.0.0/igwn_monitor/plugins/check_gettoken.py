# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check that we can get a SciToken using htgettoken.
"""

import os
import subprocess

from ..auth import scitoken as get_scitoken
from ..cli import IgwnMonitorArgumentParser
from ..utils import NagiosStatus


def check_gettoken(
    require_scopes=None,
    timeout=60,
    **token_kw,
):
    try:
        with get_scitoken(
            strict=True,
            timeout=timeout,
            **token_kw,
        ) as token:
            claims = dict(token.claims())
    except subprocess.SubprocessError as exc:  # htgettoken failed
        return (
            NagiosStatus.CRITICAL,
            "htgettoken failed",
            str(exc),
        )
    except Exception as exc:  # something else failed
        return (
            NagiosStatus.CRITICAL,
            str(exc),
            None,
        )

    message = "Bearer token created OK"
    detail = os.linesep.join((
        f"Audience: {claims['aud']}",
        f"Issuer: {claims['iss']}",
        f"Scopes: {claims['scope']}",
    ))

    missing = set(require_scopes or []) - set(claims["scope"].split(" "))
    if missing:
        return (
            NagiosStatus.WARNING,
            message + f" but missing '{missing.pop()}'",
            detail,
        )

    return NagiosStatus.OK, message, detail


def create_parser():
    """Create an argument parser for this script.
    """
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
    )
    parser.add_argument(
        "-s",
        "--require-scope",
        action="append",
        help="scope to assert returned by token",
    )
    parser.add_auth_argument_group(scitoken=True)
    return parser


def main(args=None):
    """Run the thing.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    code, message, detail = check_gettoken(
        require_scopes=opts.require_scope or [],
        timeout=opts.timeout,
        keytab=opts.kerberos_keytab,
        principal=opts.kerberos_principal,
        vaultserver=opts.token_vaultserver,
        vaulttokenfile=opts.token_vaulttokenfile,
        issuer=opts.token_issuer,
        audience=opts.token_audience,
        scope=opts.token_scope,
        role=opts.token_role,
        credkey=opts.token_credkey,
    )

    print(message)
    if detail:
        print(detail)
    return code
