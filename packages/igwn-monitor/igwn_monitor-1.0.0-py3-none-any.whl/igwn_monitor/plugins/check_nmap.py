# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check availability of a host using nmap
"""

__author__ = "Duncan Macleod <duncan.macleod@ligo.org>"

import os
import subprocess
from shutil import which

from ..cli import IgwnMonitorArgumentParser
from ..utils import NagiosStatus

NMAP = which("nmap") or "/usr/bin/nmap"


def check_nmap(
    host,
    timeout=60.,
):
    """Ping a Mattermost server and evaluate the reponse status.
    """
    proc = subprocess.run([
        NMAP,
        "-sn",
        host,
        "--host-timeout", str(timeout),
    ], capture_output=True)

    if proc.returncode:
        return (
            NagiosStatus.CRITICAL,
            "nmap failed",
            str(proc.stderr.decode("utf-8")),
        )

    stdout = proc.stdout.decode("utf-8").strip()
    lines = stdout.splitlines()

    if any(line.startswith("Note: Host seems down") for line in lines):
        return NagiosStatus.CRITICAL, "Host seems down", stdout

    try:
        return NagiosStatus.OK, lines[2], os.linesep.join(lines[3:])
    except IndexError:
        return NagiosStatus.WARNING, "Failed to parse nmap output", stdout


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
        help="hostname of Mattermost instance",
    )
    return parser


def main(args=None):
    """Run the thing.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    code, message, detail = check_nmap(
        opts.hostname,
        timeout=opts.timeout,
    )

    print(message)
    if detail:
        print(detail)
    return code
