# -*- coding: utf-8 -*-
# Copyright (C) Cardiff University (2023)
# SPDX-License-Identifier: MIT

"""Check the HTCondor pool status and report as a monitoring plugin.
"""

import enum
import json
import re
import sys
import time
from socket import getfqdn

import htcondor

from ..cli import IgwnMonitorArgumentParser

__version__ = "1.0.0"

DEFAULT_COLLECTOR_HOST = htcondor.param.get("COLLECTOR_HOST", None)

NagiosStatus = enum.IntEnum('NagiosStatus', [
    "OK",
    "WARNING",
    "CRITICAL",
    "UNKNOWN",
], start=0)


def collector_names(coll, pool=None):
    """Return the FQDNs of all collectors.
    """
    if pool is not None:
        for host in re.split("[, ]+", pool):
            try:
                yield getfqdn(host)
            except Exception:
                yield host
        return
    return (c["Machine"] for c in coll.query(
        htcondor.AdTypes.Collector,
        projection=["Machine"],
    ))


def schedd_status(coll):
    """Return the status of any and all Schedds known to the collector.
    """
    for schedd in coll.query(
        htcondor.AdTypes.Schedd,
        projection=[
            "Name",
            "TotalRunningJobs",
            "TotalHeldJobs",
            "TotalIdleJobs",
        ],
    ):
        yield schedd


def startd_status(coll):
    """Return the status of any and all Startds known to the collector.
    """
    for starter in coll.query(
        htcondor.AdTypes.Startd,
        projection=[
            "Cpus",
            "Disk",
            "Gpus",
            "Memory",
            "State",
        ],
    ):
        yield starter


def check_htcondor_pool(
    pool=None,
    warning=(0, None),
    critical=(None, None),
):
    coll = htcondor.Collector(pool)

    # get info on APs
    schedds = []
    queue = {
        "running": 0,
        "idle": 0,
        "held": 0,
    }
    for schedd in schedd_status(coll):
        schedds.append(schedd["Name"])
        queue["running"] += schedd.get("TotalRunningJobs", 0)
        queue["idle"] += schedd.get("TotalIdleJobs", 0)
        queue["held"] += schedd.get("TotalHeldJobs", 0)
    queue["total"] = sum(queue.values())

    # get info on EPs
    nodes = startd_status(coll)

    cpus = {"total": 0, "claimed": 0}
    gpus = {"total": 0, "claimed": 0}
    memory = {"total": 0, "claimed": 0}
    disk = {"total": 0, "claimed": 0}
    for node in nodes:
        ncpus = node.get("Cpus", 0)
        ngpus = node.get("Gpus", 0)
        mem = node.get("Memory", 0)
        ndisk = node.get("Disk", 0)
        cpus["total"] += ncpus
        gpus["total"] += ngpus
        memory["total"] += mem
        disk["total"] += ndisk
        if node['State'] == "Claimed":
            cpus["claimed"] += ncpus
            gpus["claimed"] += ngpus
            memory["claimed"] += mem
            disk["claimed"] += ndisk

    # totals
    ncpus = cpus['total']
    ngpus = gpus['total']
    njobs = queue['total']
    nmem = memory['total']
    ndisk = disk['total']

    # determine status
    suffix = None
    status = NagiosStatus.OK
    if not len(schedds):
        status = NagiosStatus.CRITICAL
        suffix = "no Schedds found"
    elif not njobs:
        status = NagiosStatus.CRITICAL
        suffix = "no jobs in queue"
    elif critical[0] is not None and ncpus <= critical[0]:
        status = NagiosStatus.CRITICAL
        suffix = f"{ncpus} total CPUs found"
    elif critical[1] is not None and ngpus <= critical[1]:
        status = NagiosStatus.CRITICAL
        suffix = f"{ngpus} total GPUs found"
    elif not queue["running"]:
        status = NagiosStatus.WARNING
        suffix = "no jobs running"
    elif warning[0] is not None and ncpus <= warning[0]:
        status = NagiosStatus.WARNING
        suffix = f"{ncpus} CPUs found"
    elif warning[1] is not None and ngpus <= warning[1]:
        status = NagiosStatus.WARNING
        suffix = f"{ngpus} GPUs found"
    else:
        status = NagiosStatus.OK

    message = f"HTCondor Pool status {status.name}"
    if suffix:
        message += ", " + suffix
    metrics = " ".join((
        f"'schedds'={len(schedds)};;0;0;",
        f"'claimed_cpus'={cpus['claimed']};{ncpus};{ncpus};0;{ncpus}",
        f"'claimed_gpus'={gpus['claimed']};{ngpus};{ngpus};0;{ngpus}",
        f"'running_jobs'={queue['running']};{njobs};{njobs};0;{njobs}",
        f"'idle_jobs'={queue['idle']};{njobs};{njobs};0;{njobs}",
        f"'held_jobs'={queue['held']};{njobs};{njobs};0;{njobs}",
        f"'claimed_memory'={memory['claimed']}MB;{nmem};{nmem};0;{nmem}",
        f"'claimed_disk'={disk['claimed']}KB;{ndisk};{ndisk};0;{ndisk}",
    ))

    scheddnames = "\n  ".join(sorted(schedds))
    collnames = "\n  ".join(sorted(collector_names(coll, pool)))
    details = "\n".join((
        f"Collectors:\n  {collnames}",
        f"Access Points:\n  {scheddnames}",
    ))

    return status, f"{message}|{metrics}", details


# -- reporting ------------------------

def _write_json(blob, file):
    """Write an object to ``file`` in JSON format.
    """
    if isinstance(file, str):
        with open(file, "w") as fobj:
            return _write_json(blob, fobj)

    return json.dump(blob, file)


def report_nagios_json(state, message, detail, interval=7200, file=None):
    blob = {
        "author": {
            "name": "Duncan Macleod",
            "email": "duncan.macleod@ligo.org",
        },
        "created_unix": int(time.time()),
        "status_intervals": [
            {
                "start_sec": 0,
                "end_sec": interval,
                "num_status": state.value,
                "txt_status": "\n".join((message, detail)),
            },
            {
                "start_sec": interval,
                "num_status": 3,
                "txt_status": "HTCondor pool check is not running",
            },
        ],
    }

    if file is None or file == "stdout":
        file = sys.stdout
    _write_json(blob, file)
    return state.value


# -- command-line parsing -------------

def cpu_gpu_threshold(value):
    if not value:
        return (None, None)
    thresholds = [int(v.strip()) if v else None for v in value.split(",", 1)]
    if len(thresholds) == 1:
        return (thresholds[0], None)
    return thresholds


def create_parser():
    """Create an `argparse.ArgumentParser` for this utility.
    """
    parser = IgwnMonitorArgumentParser(
        description=__doc__,
        prog=__name__.rsplit(".", 1)[-1],
        add_timeout=False,
    )
    parser.add_argument(
        "-p",
        "--pool",
        default=DEFAULT_COLLECTOR_HOST,
        help="address of collector to query",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        default="stdout",
        help="path to output file",
    )
    parser.add_argument(
        "-w",
        "--warning",
        default=(0, None),
        metavar="NCPUS,NGPUS",
        type=cpu_gpu_threshold,
        help="count of claimed CPUS (and GPUS) below which to return WARNING",
    )
    parser.add_argument(
        "-c",
        "--critical",
        default=(None, None),
        metavar="NCPUS,NGPUS",
        type=cpu_gpu_threshold,
        help="count of claimed CPUS (and GPUS) below which to return CRITICAL",
    )
    return parser


# -- run the thing --------------------

def main(args=None):
    parser = create_parser()
    opts = parser.parse_args(args=args)

    state, message, detail = check_htcondor_pool(
        pool=opts.pool,
        warning=opts.warning,
        critical=opts.critical,
    )

    # write to IGWN custom JSON format
    if opts.output_file != "stdout":
        return report_nagios_json(
            state,
            message,
            detail,
            file=opts.output_file,
        )

    # report as a standard monitoring plugin
    print(message)
    if detail:
        print(detail)

    return state


if __name__ == "__main__":
    sys.exit(main())
