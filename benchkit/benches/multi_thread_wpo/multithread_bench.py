import re
from pathlib import Path

from benchkit.core.bktypes import RecordResult
from benchkit.core.bktypes.callresults import BuildResult, FetchResult, RunResult
from benchkit.core.bktypes.contexts import BuildContext, CollectContext, FetchContext, RunContext
from benchkit.dependencies.packages import PackageDependency
from benchkit.utils.buildtools import build_dir_from_ctx, cmake_build
from benchkit.utils.dir import benchkit_dir, get_benches_dir, caller_dir


class MultThreadBench:

    def fetch(
        self,
        ctx: FetchContext,
        parent_dir: Path | None = None
    ) -> FetchResult:

        parent_dir = get_benches_dir(parent_dir=parent_dir)
        bench_dir = parent_dir / "multi-thread-wpo"
        src_file = caller_dir() / "multi_thread_test.c"

        comm = ctx.platform.comm

        if comm.isdir(bench_dir):
            return FetchResult(src_dir=bench_dir)

        comm.makedirs(path=bench_dir, exist_ok=True)

        ctx.exec(
            argv=[
                "cp",
                f"{src_file}",
                f"{bench_dir}"
            ]
        )

        return FetchResult(src_dir=bench_dir)

    def build(
        self,
        ctx: BuildContext,
        num_threads: int = 4,
        optimization: str = "2",
    ) -> BuildResult:

        platform = ctx.platform
        src_dir = ctx.fetch_result.src_dir
        src_file = src_dir/"multi_thread_test.c"
        obj_dir = build_dir_from_ctx(ctx=ctx)
        multithread_path = obj_dir / "multi_thread_test"

        platform.comm.makedirs(path=obj_dir, exist_ok=True)

        ctx.exec(
            argv=[
                "gcc",
                f"{src_file}",
                f"-O{optimization}",
                f"-pthread",
                f"-D THREAD_COUNT={num_threads}",
                f"-o",
                f"{multithread_path}",
            ],
            cwd=src_dir,
            output_is_log=True
        )

        result = BuildResult(build_dir=obj_dir)

        return result

    def run(
        self,
        ctx: RunContext,
    ) -> RunResult:

        build_dir = ctx.build_result.build_dir

        run_command = [
            "./multi_thread_test"
        ]

        exec_out = ctx.exec(
            argv=run_command, cwd=build_dir, output_is_log=True)

        result = RunResult(outputs=[exec_out])
        return result

    def collect(
        self,
        ctx: CollectContext,
    ) -> RecordResult:

        output = ctx.run_result.outputs[-1].stdout

        matches = dict(re.findall(r"(\w+)\s*=\s*(\d+)", output))

        threads = int(matches["threads"])

        duration_s = ctx.run_result.outputs[-1].duration_s

        result_dict = {
            "duration_s": duration_s,
            "throughput": (1000000 * threads) / duration_s if duration_s > 0 else 0,
        }

        return result_dict

    @staticmethod
    def dependencies() -> list[PackageDependency]:
        """
        List system package dependencies required to build and run MatrixTraversal.

        Returns:
            List of PackageDependency objects for required system packages.
            These are Ubuntu/Debian package names; other distributions may have
            different package names.

        Dependencies include:
            - build-essential: C/C++ compiler and build tools
        """
        return [
            PackageDependency("build-essential"),
        ]
