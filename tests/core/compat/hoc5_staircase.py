
from benchkit.benches.cachestaircase import CacheStaircaseBench
from benchkit.commandwrappers.taskset import TasksetWrap
from benchkit.commandwrappers.perf import PerfStatWrap
from benchkit.core.compat.new2old import CampaignCartesianProduct


def main() -> None:

    taskset_wrap = TasksetWrap()
    perf_wrap = PerfStatWrap(
        events=[
            "cache-references",
        ],
        use_json=True,
    )

    sizes = [1 << s for s in range(10, 28)]

    parameter_space = {
        "array_bytes": sizes,  # 1 KB → 128 MB
        "access_pattern": [
            "sequential", "random"
        ],
        "master_thread_core": [0],
    }

    campaign = CampaignCartesianProduct(
        benchmark=CacheStaircaseBench(),
        variables=parameter_space,
        nb_runs=5,
        command_wrappers=[
            perf_wrap, taskset_wrap
        ],
        post_run_hooks=[perf_wrap.post_run_hook_update_results],
    )

    campaign.run()

    campaign.generate_graph(
        plot_name="lineplot",
        x="array_bytes",
        y="duration_s",
        hue="access_pattern"
    )


if __name__ == "__main__":
    main()
