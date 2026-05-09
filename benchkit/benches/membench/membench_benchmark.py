"""
Benchkit support for Membench benchmark.
See: https://github.com/nicktehrany/membench
"""

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from benchkit.core.bktypes import RecordResult
from benchkit.core.bktypes.callresults import BuildResult, FetchResult, RunResult
from benchkit.core.bktypes.contexts import BuildContext, CollectContext, FetchContext, RunContext
from benchkit.dependencies.packages import PackageDependency
from benchkit.utils.buildtools import build_dir_from_ctx, make
from benchkit.utils.dir import benchkit_home_dir
from benchkit.utils.fetchtools import git_clone

from benchkit.benchmark import Benchmark, CommandAttachment, PostRunHook, PreRunHook
from benchkit.campaign import CampaignCartesianProduct, Constants
from benchkit.commandwrappers import CommandWrapper
from benchkit.dependencies.packages import PackageDependency
from benchkit.platforms import Platform
from benchkit.sharedlibs import SharedLib
from benchkit.utils.types import PathType


class MemBenchBench:
    """Benchmark object for MemBench benchmark."""

    def fetch(
        self,
        ctx: FetchContext,
    ) -> FetchResult:
        """
        Fetch Membench source code from GitHub.

        Clones the Membench repository, uses the default branch (usually main).

        Args:
            ctx: FetchContext providing platform and execution capabilities.

        Returns:
            FetchResult containing the path to the cloned repository.
        """

        membench_dir = git_clone(
            ctx=ctx,
            url="https://github.com/nicktehrany/membench.git",
            parent_dir=benchkit_home_dir(),
            commit="91f4e5b142df05e501d8941b555d547ed4958152"
        )

        return FetchResult(src_dir=membench_dir)

    def build(
        self,
        ctx: BuildContext,
    ) -> BuildResult:
        """
        Build Membench's tool

        Args:
            ctx: BuildContext providing platform, fetch results, and execution capabilities.

        Returns:
            BuildResult containing:
                - build_dir: Path to the build directory (same as source for Membench)
        """

        platform = ctx.platform
        src_dir = ctx.fetch_result.src_dir
        membench_path = src_dir / "membench"

        """
        # initialize mem file
        if not platform.comm.isdir("/mnt/mem"):
            platform.comm.shell(
                command="mkdir -p /mnt/mem",
                current_dir=src_dir,
                output_is_log=True,
            )

        if not platform.comm.isfile("/mnt/mem/file"):
            ctx.exec(argv=["touch /mnt/mem/file"],
                     cwd=src_dir, output_is_log=False)

        ctx.exec(argv=["dd if=/dev/urandom of=/mnt/mem/file bs=100M count=8"],
                 cwd=src_dir, output_is_log=False)"""

        if not platform.comm.isfile(membench_path):
            make(
                ctx=ctx,
                src_dir=src_dir,
                targets=[],
                options={},
            )

        result = BuildResult(build_dir=src_dir)
        return result

    def run(
        self,
        ctx: RunContext,
        benchfile_name: str = "example1.txt",
    ) -> RunResult:

        build_dir = ctx.build_result.build_dir

        print(
            f"Running Membench with benchfile: {build_dir}/examples/{benchfile_name}")

        run_command = [
            "./membench",
            f"-file={build_dir / 'examples' / benchfile_name}",
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
            # "cache_references": cache_references,
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


"""
    def __init__(
        self,
        src_dir: PathType,
        command_wrappers: Iterable[CommandWrapper],
        command_attachments: Iterable[CommandAttachment],
        shared_libs: Iterable[SharedLib],
        pre_run_hooks: Iterable[PreRunHook],
        post_run_hooks: Iterable[PostRunHook],
        platform: Platform | None = None,
    ) -> None:
        super().__init__(
            command_wrappers=command_wrappers,
            command_attachments=command_attachments,
            shared_libs=shared_libs,
            pre_run_hooks=pre_run_hooks,
            post_run_hooks=post_run_hooks,
        )
        if platform is not None:
            self.platform = platform  # TODO Warning! overriding upper class platform

        bench_src_path = pathlib.Path(src_dir)
        if not self.platform.comm.isdir(bench_src_path):
            raise ValueError(
                f"Invalid MemBench source path: {bench_src_path}\n"
                "src_dir argument can be defined manually."
            )

        self._bench_src_path = bench_src_path

    @property
    def bench_src_path(self) -> pathlib.Path:
        return self._bench_src_path

    @staticmethod
    def get_build_var_names() -> List[str]:
        return []

    @staticmethod
    def get_run_var_names() -> List[str]:
        return [
            "benchfile_name",
        ]

    @staticmethod
    def get_tilt_var_names() -> List[str]:
        return []

    @staticmethod
    def _parse_results(
        output: str,
    ) -> Dict[str, str]:
        attributes = [
            "Engine",
            "Flags",
            "Iterations",
            "Memcpy Iterations",
            "Total Memcpy Calls",
            "Total Runtime",
            "File Size",
            "Copy Size",
            "Random Read",
            "Data Copied",
            "Minimum latency",
            "Maximum latency",
            "Average latency",
            "Buffer Size",
        ]

        section_data = MemBenchBench.parse_section(output.strip())
        result = [section_data.get(attr, "") for attr in attributes]

        result_dict = dict(zip(attributes, result))

        return result_dict

    @staticmethod
    def convert_units(value):
        unit_conversions = {
            "GiB": ("MiB", 1024),
            "KiB": ("MiB", 1 / 1024),
            "sec": ("usec", 1e6),
            "msec": ("usec", 1e3),
            "nsec": ("usec", 1e-3),
            "usec": ("usec", 1),
        }
        for unit, (new_unit, factor) in unit_conversions.items():
            if unit in value:
                number = float(re.search(r"[\d.]+", value).group())
                converted_value = number * factor
                return f"{converted_value:.2f} {new_unit}"
        return value

    @staticmethod
    def parse_section(section):
        section_data = {}
        for line in section.strip().split("\n"):
            key, value = re.match(r"(.*?):\s*(.*)", line).groups()
            section_data[key] = MemBenchBench.convert_units(value)
        return section_data

    def dependencies(self) -> List[PackageDependency]:
        return super().dependencies() + [
            PackageDependency("build-essential"),
            PackageDependency("make"),
            PackageDependency("gcc"),
        ]

    def build_tilt(self, **kwargs) -> None:
        self.tilt.build_single_lock(**kwargs)

    def prebuild_bench(self, **_kwargs) -> None:
        pass

    def build_bench(
        self,
        **kwargs,
    ) -> None:
        src_dir = self._bench_src_path

        # Make the project
        self.platform.comm.shell(
            command="make",
            current_dir=src_dir,
            output_is_log=True,
        )

        # Build benchmarking files to src_dir/out
        self.platform.comm.shell(
            command="touch benchfile",
            current_dir=src_dir,
            output_is_log=True,
        )

        # Generate file to be benchmarked
        # TODO using random values might introduce unpredictability in results, find a constant way
        self.platform.comm.shell(
            command="dd if=/dev/urandom of=benchfile bs=100M count=8",
            current_dir=src_dir,
            output_is_log=True,
        )

    def clean_bench(self) -> None:
        src_dir = self._bench_src_path

        # Generate file to be benchmarked
        self.platform.comm.shell(
            command="rm -f benchfile",
            current_dir=src_dir,
            output_is_log=True,
        )

    def single_run(  # pylint: disable=arguments-differ
        self,
        benchfile_name: str = "",
        **kwargs,
    ) -> str:
        environment = self._preload_env(
            **kwargs,
        )

        file_path = self._bench_src_path / "examples" / benchfile_name

        run_command = [
            "./membench",
            f"-file={file_path}",
        ]

        wrapped_run_command, wrapped_environment = self._wrap_command(
            run_command=run_command,
            environment=environment,
            **kwargs,
        )

        output = self.run_bench_command(
            run_command=run_command,
            wrapped_run_command=wrapped_run_command,
            current_dir=self._bench_src_path,
            environment=environment,
            wrapped_environment=wrapped_environment,
            print_output=False,
        )

        return output

    def parse_output_to_results(  # pylint: disable=arguments-differ
        self,
        command_output: str,
        **_kwargs,
    ) -> Dict[str, Any]:

        result_dict = self._parse_results(output=command_output)

        return result_dict
"""
