# Copyright (C) 2026 Vrije Universiteit Brussel. All rights reserved.
# SPDX-License-Identifier: MIT

from benchkit.benches.multi_thread_wpo .multithread_bench import MultThreadBench
from benchkit.commandwrappers.taskset import TasksetWrap
from benchkit.core.compat.new2old import CampaignCartesianProduct


def main() -> None:
    parameter_space = {
        "num_threads": [1, 2, 4, 8],
        # "optimization": ["0", "1", "2", "3"]
    }

    taskset_wrap = TasksetWrap()

    campaign = CampaignCartesianProduct(
        benchmark=MultThreadBench(),
        variables=parameter_space,
        command_wrappers=[taskset_wrap],
        duration_s=5,
        nb_runs=10
    )

    campaign.run()

    campaign.generate_graph(
        plot_name="scatterplot",
        x="num_threads",
        y="throughput",
    )


if __name__ == "__main__":
    main()
