# Copyright (C) 2026 Vrije Universiteit Brussel. All rights reserved.
# SPDX-License-Identifier: MIT

from benchkit.benches.mattrav import MatrixTraversal
from benchkit.commandwrappers.taskset import TasksetWrap
from benchkit.core.compat.new2old import CampaignCartesianProduct


def main() -> None:
    parameter_space = {
        "N": [1000],  # , 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000],
        "order": [0, 1],
        "optimization": ["0", "1", "2", "3"]
    }

    taskset_wrap = TasksetWrap()

    campaign = CampaignCartesianProduct(
        benchmark=MatrixTraversal(),
        variables=parameter_space,
        command_wrappers=[taskset_wrap],
        duration_s=5,
        nb_runs=10
    )

    campaign.run()

    campaign.generate_graph(
        plot_name="scatterplot",
        x="optimization",
        y="duration_s",
        hue="order"
    )


if __name__ == "__main__":
    main()
