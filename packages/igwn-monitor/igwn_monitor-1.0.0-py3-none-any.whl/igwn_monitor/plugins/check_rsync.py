# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check the status of an rsync server
"""

import subprocess
from shutil import which

from ..cli import IgwnMonitorArgumentParser
from ..http import make_url
from ..utils import NagiosStatus

RSYNC = which("rsync") or "rsync"
DEFAULT_PORT = 873


def check_rsync(
    host,
    port=DEFAULT_PORT,
    timeout=10.,
):
    if port:
        host += f":{port}"
    target = make_url(host, scheme="rsync")

    proc = subprocess.run(
        [RSYNC, target, "--timeout", str(timeout)],
        check=False,
        capture_output=True,
    )
    if proc.returncode:
        return (
            NagiosStatus.CRITICAL,
            "Rsync query failed",
            proc.stderr.decode("utf-8").strip(),
        )
    return (
        NagiosStatus.OK,
        "Rsync query OK",
        proc.stdout.decode("utf-8").strip(),
    )


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
        "--port",
        default=DEFAULT_PORT,
        help="port on host to query",
    )
    return parser


def main(args=None):
    """Run the thing.
    """
    parser = create_parser()
    opts = parser.parse_args(args=args)

    code, message, detail = check_rsync(
        opts.hostname,
        port=opts.port,
        timeout=opts.timeout,
    )

    print(message)
    if detail:
        print(detail)
    return code
