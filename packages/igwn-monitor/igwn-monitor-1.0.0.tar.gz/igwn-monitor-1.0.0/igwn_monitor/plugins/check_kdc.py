# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check that a KDC can be used to generate a Kerberos TGT.
"""

import os
from pathlib import Path

import gssapi

from ..auth import kerberos_tgt
from ..cli import IgwnMonitorArgumentParser
from ..utils import NagiosStatus

DEFAULT_PORT = 88
DEFAULT_KEYTAB = os.getenv("KRB5_KTNAME")


def check_kdc(
    kdc,
    principal,
    keytab=DEFAULT_KEYTAB,
):
    try:
        with kerberos_tgt(
            kdc=kdc,
            keytab=keytab,
            principal=principal,
            force=True,  # dont reuse existing creds
        ) as creds:
            return (
                NagiosStatus.OK,
                f"Successfully generated Kerberos TGT for {creds.name}",
                None,
            )
    except gssapi.exceptions.GSSError as exc:
        return (
            NagiosStatus.CRITICAL,
            f"Error generating TGT for {principal}",
            str(exc),
        )


def create_parser():
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
        add_timeout=False,  # unsupported
    )
    parser.add_argument(
        "-H",
        "--hostname",
        help="hostname of KDC",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="port to use on KDC",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="enable debugging",
    )
    parser.add_argument(
        "-B",
        "--kerberos-keytab",
        default=DEFAULT_KEYTAB,
        type=Path,
        help="path to Kerberos keytab file",
    )
    parser.add_argument(
        "-P",
        "--kerberos-principal",
        help=(
            "Principal to use with Kerberos, auto-discovered from "
            "-K/--kerberos-keytab if given"
        ),
    )
    return parser


def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    if opts.port:
        opts.hostname += ":" + str(opts.port)

    code, message, detail = check_kdc(
        opts.hostname,
        opts.kerberos_principal,
        keytab=opts.kerberos_keytab,
    )
    print(message)
    if detail:
        print(detail)
    return code
