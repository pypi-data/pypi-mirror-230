# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Command-line utilities for IGWN monitors
"""

import argparse
import os
from pathlib import Path

from . import __version__
from .auth import (
    DEFAULT_IDP,
    DEFAULT_TOKEN_ISSUER,
    DEFAULT_VAULT,
)
from .http import (
    AUTH_GET_FUNCTIONS,
    DEFAULT_REQUEST_TIMEOUT,
)


class IgwnMonitorArgumentFormatter(
    argparse.RawDescriptionHelpFormatter,
    argparse.ArgumentDefaultsHelpFormatter,
):
    pass


class IgwnMonitorArgumentParser(argparse.ArgumentParser):
    def __init__(
        self,
        *args,
        add_version=True,
        add_timeout=True,
        **kwargs,
    ):
        kwargs.setdefault("formatter_class", IgwnMonitorArgumentFormatter)
        super().__init__(*args, **kwargs)
        self._positionals.title = "Positional arguments"
        self._optionals.title = "Optional arguments"

        # add a default `--version` argument
        if add_version:
            self.add_version()

        # add a default `--timeout` argument
        if add_timeout:
            if add_timeout is True:
                timeout = DEFAULT_REQUEST_TIMEOUT
            else:  # user-specified value
                timeout = float(add_timeout)
            self.add_timeout(default=timeout)

    def add_timeout(
        self,
        default=DEFAULT_REQUEST_TIMEOUT,
        help="seconds before check times out",
        **kwargs,
    ):
        """Add a ``-t/--timeout`` argument to this `ArgumentParser`.
        """
        self.add_argument(
            "-t",
            "--timeout",
            type=float,
            default=default,
            help=help,
            **kwargs,
        )

    def add_version(self):
        """Add a ``-V/--version`` argument to this `ArgumentParser`.
        """
        self.add_argument(
            "-V",
            "--version",
            action="version",
            version=f"{self.prog} {__version__}",
        )

    def add_auth_argument_group(
        self,
        title="Authorisation arguments",
        auth_type="none",
        kerberos=True,
        description=None,
        keytab=True,
        principal=True,
        scitoken=True,
    ):
        group = self.add_argument_group(
            title=title,
            description=description,
        )
        group.add_argument(
            "-a",
            "--auth-type",
            choices=AUTH_GET_FUNCTIONS.keys(),
            default=auth_type,
            help="auth type to use",
        )
        group.add_argument(
            "-i",
            "--identity-provider",
            default=DEFAULT_IDP,
            help="name of ECP Identity Provider",
        )
        if kerberos:
            group.add_argument(
                "-K",
                "--no-kerberos",
                dest="kerberos",
                default=True,
                action="store_false",
                help="Disable kerberos auth",
            )
        else:
            group.add_argument(
                "-k",
                "--kerberos",
                action="store_true",
                help="Use Kerberos auth",
            )
        if keytab:
            group.add_argument(
                "-B",
                "--kerberos-keytab",
                default=os.getenv("KRB5_KTNAME"),
                type=Path,
                help="path to Kerberos keytab file",
            )
        if principal:
            group.add_argument(
                "-P",
                "--kerberos-principal",
                help=(
                    "principal to use with Kerberos, auto-discovered from "
                    "-K/--kerberos-keytab if given"
                ),
            )
        if scitoken:
            group.add_argument(
                "-X",
                "--token-vaultserver",
                default=DEFAULT_VAULT,
                help="URL of token vault server",
            )
            group.add_argument(
                "-I",
                "--token-issuer",
                default=DEFAULT_TOKEN_ISSUER,
                help="name of token issuer",
            )
            group.add_argument(
                "-G",
                "--token-vaulttokenfile",
                help="path of vault token to read/write",
            )
            group.add_argument(
                "-T",
                "--token-audience",
                help=(
                    "audience for scitoken, defaults to the fully-qualified "
                    "URL of the target host"
                ),
            )
            group.add_argument(
                "-S",
                "--token-scope",
                help="scope (or comma-separated list) for scitoken",
            )
            group.add_argument(
                "-R",
                "--token-role",
                help="vault name of role for OIDC",
            )
            group.add_argument(
                "-C",
                "--token-credkey",
                help="key to use in vault secretpath"
            )
        return group
