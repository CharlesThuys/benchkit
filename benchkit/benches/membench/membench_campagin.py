# Copyright (C) 2026 Vrije Universiteit Brussel. All rights reserved.
# SPDX-License-Identifier: MIT

from benchkit.benches.membench.membench_benchmark import MemBenchBench
from benchkit.commandwrappers.taskset import TasksetWrap
from benchkit.core.compat.new2old import CampaignCartesianProduct


def main() -> None:
    parameter_space = {
        # "example2.txt", "example3.txt" are not running
        "benchfile_name": ["baseline.txt"]
        # workloads/baseline.txt
    }

    taskset_wrap = TasksetWrap()

    campaign = CampaignCartesianProduct(
        benchmark=MemBenchBench(),
        variables=parameter_space,
        command_wrappers=[taskset_wrap],
        duration_s=5,
        nb_runs=10
    )

    campaign.run()

    """ campaign.generate_graph(
        plot_name="scatterplot",
        x="num_threads",
        y="throughput",
    ) """


if __name__ == "__main__":
    main()


""" def membench_campaign(
    name: str = "membench_campaign",
    benchmark: Optional[MemBenchBench] = None,
    # Membench allows for granular control over benchmarks via files
    # When creating benchmarks, just created new ones inside the /examples folder
    # And include the file name in this list
    benchfile: Iterable[str] = (
        "example1.txt",
        "example2.txt",
    ),  # Benchmark does not end: "example3.txt"
    # TODO remove the example and use the parameters as used in the examples
    # directly with the command line
    src_dir: Optional[PathType] = None,
    results_dir: Optional[PathType] = None,
    command_wrappers: Iterable[CommandWrapper] = (),
    command_attachments: Iterable[CommandAttachment] = (),
    shared_libs: Iterable[SharedLib] = (),
    pre_run_hooks: Iterable[PreRunHook] = (),
    post_run_hooks: Iterable[PostRunHook] = (),
    platform: Platform | None = None,
    nb_runs: int = 1,
    benchmark_duration_seconds: int = 5,
    debug: bool = False,
    gdb: bool = False,
    enable_data_dir: bool = False,
    continuing: bool = False,
    constants: Constants = None,
    pretty: Optional[Dict[str, str]] = None,
) -> CampaignCartesianProduct:
    Return a cartesian product campaign configured for the Membench benchmark.

    variables = {
        "benchfile_name": benchfile,
    }

    if pretty is not None:
        pretty = {"lock": pretty}

    if src_dir is None:
        pass

    if benchmark is None:
        benchmark = MemBenchBench(
            src_dir=src_dir,
            command_wrappers=command_wrappers,
            command_attachments=command_attachments,
            shared_libs=shared_libs,
            pre_run_hooks=pre_run_hooks,
            post_run_hooks=post_run_hooks,
            platform=platform,
        )

    return CampaignCartesianProduct(
        name=name,
        benchmark=benchmark,
        nb_runs=nb_runs,
        variables=variables,
        constants=constants,
        debug=debug,
        gdb=gdb,
        enable_data_dir=enable_data_dir,
        continuing=continuing,
        benchmark_duration_seconds=benchmark_duration_seconds,
        results_dir=results_dir,
        pretty=pretty,
    )
 """
