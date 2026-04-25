# Copyright (C) 2025 Vrije Universiteit Brussel. All rights reserved.
# SPDX-License-Identifier: MIT
"""
LevelDB benchmark implementation for benchkit.

This module implements the benchkit protocol for LevelDB's db_bench benchmark tool.
LevelDB is an embedded key-value store optimized for fast storage, commonly used
for benchmarking storage and database performance.

The implementation covers:
- Fetching LevelDB source from GitHub
- Building db_bench and preparing a test database
- Running various LevelDB benchmarks (readrandom, fillseq, etc.)
- Parsing performance metrics from db_bench output

Example:
    >>> from pathlib import Path
    >>> bench = LevelDBBench()

    # ------------------------------------------------------------------
    # Fetch: clone LevelDB sources
    # ------------------------------------------------------------------
    >>> fetch_ctx = FetchContext.from_args(
    ...     fetch_args={
    ...         "parent_dir": Path("/tmp/src"),
    ...         "commit": "v1.17.0",
    ...     }
    ... )
    >>> fetch_result = bench.fetch(ctx=fetch_ctx, **fetch_ctx.fetch_args)

    # ------------------------------------------------------------------
    # Build: compile db_bench and prepare the test database
    # ------------------------------------------------------------------
    >>> build_ctx = BuildContext.from_fetch(
    ...     fetch_ctx=fetch_ctx,
    ...     fetch_result=fetch_result,
    ... )
    >>> build_result = bench.build(ctx=build_ctx)

    # ------------------------------------------------------------------
    # Run: execute a benchmark workload
    # ------------------------------------------------------------------
    >>> run_ctx = RunContext.from_build(
    ...     build_ctx=build_ctx,
    ...     build_result=build_result,
    ...     duration_s=1.0,
    ... )
    >>> run_result = bench.run(
    ...     ctx=run_ctx,
    ...     bench_name="readrandom",
    ...     nb_threads=4,
    ... )

    # ------------------------------------------------------------------
    # Collect: parse performance metrics from db_bench output
    # ------------------------------------------------------------------
    >>> collect_ctx = CollectContext.from_run(
    ...     run_ctx=run_ctx,
    ...     run_result=run_result,
    ... )
    >>> record = bench.collect(
    ...     ctx=collect_ctx,
    ...     bench_name="readrandom",
    ... )

    >>> record["operations/second"]
    5500

"""

import re
from pathlib import Path

from benchkit.core.bktypes import RecordResult
from benchkit.core.bktypes.callresults import BuildResult, FetchResult, RunResult
from benchkit.core.bktypes.contexts import BuildContext, CollectContext, FetchContext, RunContext
from benchkit.dependencies.packages import PackageDependency
from benchkit.utils.buildtools import build_dir_from_ctx, cmake_build
from benchkit.utils.dir import benchkit_dir, get_benches_dir, caller_dir


class MatrixTraversal:

    def fetch(
        self,
        ctx: FetchContext,
        parent_dir: Path | None = None
    ) -> FetchResult:

        parent_dir = get_benches_dir(parent_dir=parent_dir)
        bench_dir = parent_dir / "mattrav"
        src_file = caller_dir() / "matrix_traversal.c"

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
        optimization: str = "2",
    ) -> BuildResult:

        platform = ctx.platform
        src_dir = ctx.fetch_result.src_dir
        src_file = src_dir/"matrix_traversal.c"
        obj_dir = build_dir_from_ctx(ctx=ctx)
        mattrav_path = obj_dir / "mattrav"

        platform.comm.makedirs(path=obj_dir, exist_ok=True)

        ctx.exec(
            argv=[
                "gcc",
                f"{src_file}",
                f"-O{optimization}",
                f"-o",
                f"{mattrav_path}",
            ],
            cwd=src_dir,
            output_is_log=True
        )

        result = BuildResult(build_dir=obj_dir)

        return result

    def run(
        self,
        ctx: RunContext,
        N: int = 100,
        order: int = 0  # 0 = row-major, 1 = column-major
    ) -> RunResult:

        build_dir = ctx.build_result.build_dir

        run_command = [
            "./mattrav",
            f"{N}",
            f"{order}",
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

        duration_s = ctx.run_result.outputs[-1].duration_s

        result_dict = {
            "duration_s": duration_s,
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
