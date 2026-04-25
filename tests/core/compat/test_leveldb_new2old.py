# Copyright (C) 2026 Vrije Universiteit Brussel. All rights reserved.
# SPDX-License-Identifier: MIT

from benchkit.benches.leveldb import LevelDBBench
from benchkit.core.compat.new2old import CampaignCartesianProduct


def main() -> None:
    variables = {
        "bench_name": ["readrandom", "seekrandom"],
        "nb_threads": [1, 2, 3, 4],
    }

    campaign = CampaignCartesianProduct(
        benchmark=LevelDBBench(),
<<<<<<< HEAD
        variables=parameter_space,
=======
        variables=variables,
>>>>>>> a8e03a811236a8cd45b75a9b517303985ab3e88e
    )

    campaign.run()

    campaign.generate_graph(
        plot_name="lineplot",
        x="nb_threads",
        y="throughput",
        hue="bench_name",
    )


if __name__ == "__main__":
    main()
