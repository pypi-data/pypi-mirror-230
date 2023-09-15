# -*- coding: utf-8 -*-

from collections import OrderedDict
import glob
import os
import sys

import dask
from dask.distributed import Client, LocalCluster, wait, system
from dask.distributed import progress as distributed_progress

# from dask_jobqueue import SLURMCluster
import psutil


def progress(fs):
    if sys.stdout.isatty():
        return distributed_progress(fs)
    else:
        wait(fs)
        return fs


def cpu_count_physical():
    # Adapted from psutil
    """Return the number of physical cores in the system."""
    IDS = ["physical_package_id", "die_id", "core_id", "book_id", "drawer_id"]
    # Method #1
    core_ids = set()
    for path in glob.glob("/sys/devices/system/cpu/cpu[0-9]*/topology"):
        core_id = []
        for id in IDS:
            id_path = os.path.join(path, id)
            if os.path.exists(id_path):
                with open(id_path) as f:
                    core_id.append(int(f.read()))
        core_ids.add(tuple(core_id))
    result = len(core_ids)
    if result != 0:
        return result
    else:
        return None


def hyperthreading_info():
    no_logical_cpus = psutil.cpu_count(logical=True)
    no_physical_cpus = cpu_count_physical()
    if no_logical_cpus is None or no_physical_cpus is None:
        hyperthreading = None
    else:
        hyperthreading = no_logical_cpus > no_physical_cpus
    return (hyperthreading, no_logical_cpus, no_physical_cpus)


class DistributedLocalClusterScheduler:
    def __init__(self, threads_per_worker=2, **kwargs):
        (hyperthreading, no_logical_cpus, no_physical_cpus) = hyperthreading_info()
        if hyperthreading:
            factor = no_logical_cpus // no_physical_cpus
            no_available_physical_cpus = dask.system.CPU_COUNT // factor
            if no_available_physical_cpus < threads_per_worker:
                # Avoid situation where number of workers becomes zero
                # because number of threads per worker exceeds number
                # of available physical cpus.
                threads_per_worker = no_available_physical_cpus
            n_workers = no_available_physical_cpus // threads_per_worker
            memory_limit = (system.MEMORY_LIMIT * 0.9) / n_workers
        else:
            # let dask figure it out
            n_workers = None
            memory_limit = None
        self.cluster = LocalCluster(
            n_workers=n_workers,
            threads_per_worker=threads_per_worker,
            memory_limit=memory_limit,
        )
        self.client = Client(self.cluster)

    def __enter__(self):
        self.cluster.__enter__()
        self.client.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.client.__exit__(type, value, traceback)
        self.cluster.__exit__(type, value, traceback)


class ExternalScheduler:
    def __init__(self, scheduler_file, auto_shutdown=True, **kwargs):
        self.scheduler_file = scheduler_file
        self.client = Client(scheduler_file=scheduler_file)
        self.auto_shutdown = auto_shutdown

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        if self.auto_shutdown:
            self.client.shutdown()
        self.client.__exit__(type, value, traceback)


class LocalThreadsScheduler:
    def __init__(self, **kwargs):
        self.client = None

    def __enter__(self):
        dask.config.set(scheduler="threads")
        return self

    def __exit__(self, type, value, traceback):
        pass


class MPIScheduler:
    def __init__(self, **kwargs):
        from dask_mpi import initialize

        n_workers = 4  # tasks-per-node from scheduler
        n_threads = 4  # cpus-per-task from scheduler
        memory_limit = (system.MEMORY_LIMIT * 0.9) / n_workers
        initialize(
            "ib0",
            nthreads=n_threads,
            local_directory="/scratch/local",
            memory_limit=memory_limit,
        )
        self.client = Client()

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, type, value, traceback):
        self.client.__exit__(type, value, traceback)


class SingleThreadedScheduler:
    def __init__(self, **kwargs):
        self.client = None

    def __enter__(self):
        dask.config.set(scheduler="single-threaded")
        return self

    def __exit__(self, type, value, traceback):
        pass


SCHEDULERS = OrderedDict(
    [
        ("distributed-local-cluster", DistributedLocalClusterScheduler),
        ("external", ExternalScheduler),
        ("threaded", LocalThreadsScheduler),
        ("mpi", MPIScheduler),
        ("single-threaded", SingleThreadedScheduler),
    ]
)


def setup_scheduler(args):
    scheduler_spec = args.dask_scheduler.split("@")
    scheduler_name = scheduler_spec[0]
    scheduler_kwargs = {k: v for k, v in (e.split("=") for e in scheduler_spec[1:])}
    scheduler = SCHEDULERS[scheduler_name]
    return scheduler(**scheduler_kwargs)
