"""Generate a wheel for a prodigy_teams_recipes package,
including updating its meta file and requirements files."""
import json
import re
import subprocess
from contextlib import ExitStack
from functools import cached_property
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version

from prodigy_teams.errors import RecipeBuildMetaFailed

from .. import ty
from ..build import DirectorySource, RequirementSet, Venv, WheelSource, _make_tempdir

RecipeInput = ty.Union[Requirement, WheelSource, DirectorySource]
ExtraWheelsInput = ty.Union[WheelSource, DirectorySource]


class RecipeBuilder:
    def __init__(
        self,
        src: RecipeInput,
        extras: ty.List[ExtraWheelsInput],
        wheelhouse: ty.Optional[Path] = None,
        cwd: ty.Optional[Path] = None,
    ):
        self._exit_stack = ExitStack()
        self.recipe_distribution_name = (
            src.name if isinstance(src, Requirement) else src.distribution_name
        )
        self.src = src
        self.extras = extras
        if wheelhouse is not None:
            self.wheelhouse = wheelhouse
        else:
            self.wheelhouse = self._exit_stack.enter_context(_make_tempdir())
        self._cwd = cwd
        self._upgrade_builder_venv = False

    def __enter__(self) -> "RecipeBuilder":
        return self

    def __exit__(self, _exc_type, _exc, _exc_tb):
        self._exit_stack.close()

    @cached_property
    def _builder_env_requirements(self) -> RequirementSet:
        return RequirementSet(
            ["setuptools==65.4.1", "wheel", "pip-tools>=6.13.0", "pip", "build>=0.10.0"]
        )

    @cached_property
    def _builder_venv(self) -> "Venv":
        with Venv.from_active(cwd=self._cwd) as venv:
            _builder_venv = Venv.cached(
                "__prodigy_teams__",
                build_venv=venv,
            )
            _builder_venv.install(
                *self._builder_env_requirements.to_lines(), upgrade=False
            )
        return _builder_venv

    @cached_property
    def recipe_version(self) -> Version:
        if isinstance(self.src, Requirement):
            version_spec = self.src.specifier
            if len(version_spec) == 1 and all(
                s.operator == "==" and s.version for s in version_spec
            ):
                return Version(next(iter(version_spec)).version)
            else:
                return self.prepared_wheelhouse[self.recipe_distribution_name].version
        elif isinstance(self.src, DirectorySource) and self.src.version is not None:
            return self.src.version
        else:
            return self.prepared_wheelhouse[self.recipe_distribution_name].version

    @cached_property
    def recipe_wheel(self) -> WheelSource:
        if isinstance(self.src, (Requirement, DirectorySource)):
            return self.prepared_wheelhouse[self.recipe_distribution_name]
        else:
            return self.src

    @cached_property
    def recipe_package_name(self) -> str:
        if isinstance(self.src, (Requirement, DirectorySource)):
            return self.prepared_wheelhouse[self.recipe_distribution_name].package_name
        else:
            return self.src.package_name

    @cached_property
    def resolved_input_requirements(self) -> RequirementSet:
        """
        Resolve the versions of the input packages.
        """
        requirements = set()
        for pkg in [self.src, *self.extras]:
            if isinstance(pkg, Requirement):
                requirements.add(pkg)
            elif pkg.version is not None:
                # requirements.add(Requirement(f"{pkg.distribution_name}=={pkg.version}"))
                requirements.add(Requirement(f"{pkg.distribution_name}=={pkg.version}"))
            else:
                # we need to build the wheel (metadata) to figure out the version
                built_wheels = self.prepared_wheelhouse
                wheel = built_wheels[pkg.distribution_name]
                requirements.add(
                    Requirement(f"{wheel.distribution_name}=={wheel.version}")
                )
        return RequirementSet(requirements)

    @cached_property
    def compiled_venv_requirements(
        self,
    ) -> ty.Tuple[Path, RequirementSet, ty.List[str]]:
        cached_venv = Venv._get_venv_cache_path(
            self.recipe_distribution_name, mkdir=True
        )
        requirements = []
        if isinstance(self.src, Requirement):
            requirements.append(self.src)
        requirements.extend(self.prepared_wheelhouse.values())
        upgrade_packages = [r.name for r in self.resolved_input_requirements]
        output_path = cached_venv / "requirements.txt"
        compile_requirements(
            self._builder_venv,
            requirements=requirements,
            wheelhouse=self.wheelhouse,
            output_path=output_path,
            upgrade_packages=upgrade_packages,
            upgrade=False,
            pip_tools_cache=self._get_pip_tools_cache(),
        )
        return output_path, RequirementSet.from_txt(output_path), upgrade_packages

    @cached_property
    def recipes_venv(
        self,
    ) -> "Venv":
        cached_venv = Venv._get_venv_cache_path(
            self.recipe_distribution_name, mkdir=True
        )
        cached_venv.mkdir(exist_ok=True, parents=True)
        extra_reqs_path = cached_venv / "extra-requirements.txt"
        extra_reqs_path.write_text(RequirementSet(["pip-tools"]).to_txt())
        python_bin = cached_venv / "bin" / "python"
        if not python_bin.exists():
            self._builder_venv.run_module("venv", str(cached_venv.absolute()))
        Venv(str(python_bin)).run_module(
            "pip",
            "install",
            "-r",
            str(extra_reqs_path.resolve()),
            cwd=cached_venv,
        )

        venv = Venv(str(python_bin))
        (
            requirements_path,
            _,
            _,
        ) = self.compiled_venv_requirements
        venv.run_module(
            "piptools",
            "sync",
            # "-r",
            str(extra_reqs_path.resolve()),
            str(requirements_path.resolve()),
            "-f",
            str(self.wheelhouse.resolve()),
            cwd=cached_venv,
        )
        return venv

    @cached_property
    def prepared_wheelhouse(self) -> ty.Dict[str, WheelSource]:
        """
        Builds all local dependencies, and returns a mapping from distribution name to wheels.
        """
        wheels = []
        to_build = []
        for src in [self.src, *self.extras]:
            if isinstance(src, WheelSource):
                wheels.append(src)
            elif isinstance(src, DirectorySource):
                to_build.append(src)
            else:
                _, requirements, _ = self.compiled_venv_requirements
                requirements[self.recipe_distribution_name]
        wheels.extend(
            self._build_wheels(
                [p.path for p in to_build], self.wheelhouse, no_deps=True
            )
        )
        return {w.distribution_name: w for w in wheels}

    def _build_wheels(
        self,
        srcs: ty.List[Path],
        dest: Path,
        no_deps: bool = False,
        find_links: ty.List[Path] = [],
        cwd: ty.Optional[Path] = None,
    ) -> ty.List[WheelSource]:
        pip_wheel_args = [*[str(p.resolve()) for p in srcs], "-w", str(dest.absolute())]
        if no_deps:
            pip_wheel_args.append("--no-deps")
        if find_links:
            for dir in find_links:
                pip_wheel_args.extend(["-f", str(dir)])
        result = self._builder_venv.run_module("pip", "wheel", *pip_wheel_args, cwd=cwd)
        wheels = re.findall(r"(?<=filename=)\S+", result.stdout)
        return [WheelSource((dest / wheel).absolute()) for wheel in wheels]

    def _get_depcache(self) -> ty.List[Path]:
        pip_tools_cache = self._get_pip_tools_cache()
        return [p for p in pip_tools_cache.glob("depcache-cp*.json")]

    def _get_pip_tools_cache(self) -> Path:
        venv_cache = self._builder_venv._get_venv_cache_path(
            "__prodigy_teams__", mkdir=True
        )
        pip_tools_cache = venv_cache / "pip-tools-cache"
        pip_tools_cache.mkdir(exist_ok=True)
        return pip_tools_cache

    def _recipe_venv_path(self) -> Path:
        return self._builder_venv._get_venv_cache_path(
            self.recipe_distribution_name, mkdir=True
        )

    @cached_property
    def recipes_meta(
        self,
    ) -> ty.Dict[str, ty.Any]:
        recipes_venv = self.recipes_venv
        wheels = self.prepared_wheelhouse
        requirements_path, _, _ = self.compiled_venv_requirements
        cleaned_requirements = RequirementSet.from_txt(
            requirements_path
        ).replace_local_wheel_links(set(wheels.keys()))

        try:
            recipes_meta = json.loads(
                recipes_venv.run_module(
                    "prodigy_teams_recipes_sdk", "create-meta", self.recipe_package_name
                ).stdout
            )
        except subprocess.CalledProcessError as e:
            raise RecipeBuildMetaFailed(
                self.recipe_package_name, stdout=e.stdout, stderr=e.stderr
            )

        pkg_meta = self.recipe_wheel.pkginfo_metadata
        meta = {
            "name": self.recipe_wheel.distribution_name,
            "version": str(self.recipe_wheel.version),
            "description": pkg_meta.summary if pkg_meta is not None else None,
            "author": pkg_meta.author if pkg_meta is not None else None,
            "email": pkg_meta.author_email if pkg_meta is not None else None,
            "url": pkg_meta.home_page if pkg_meta is not None else None,
            "license": pkg_meta.license if pkg_meta is not None else None,
            "assets": {},
            "recipes": recipes_meta,
            "requirements": cleaned_requirements.to_lines(),
        }
        # Check it's json serializable
        _ = json.dumps(meta, indent=2)
        return meta


def compile_requirements(
    venv: Venv,
    requirements: ty.List[ty.Union[Requirement, WheelSource, str]],
    wheelhouse: Path,
    output_path: Path,
    pip_tools_cache: Path,
    upgrade_packages: ty.Iterable[str] = [],
    upgrade: bool = False,
):
    # def collect_wheel_files(wheels: ty.List[WheelSource], wheelhouse: Path):
    #     """
    #     Get all of the local wheels we want to include so we can check
    #     if their requirements changed without a version change.
    #     """
    #     # TODO: this assumes the wheelhouse only includes the wheels we need
    #     # we should expand from the requirements in the initial wheels set
    #     # or send in the full set of wheels to be included
    #     all_wheels = {w.distribution_name: w for w in wheels}
    #     for wheel_path in wheelhouse.iterdir():
    #         if wheel_path.suffix == ".whl":
    #             wheel = WheelSource(wheel_path)
    #             if wheel.distribution_name not in all_wheels:
    #                 all_wheels[wheel.distribution_name] = wheel
    #             else:
    #                 # sanity check incase the wheelhouse contains multiple versions
    #                 assert (
    #                     all_wheels[wheel.distribution_name].version == wheel.version
    #                 ), f"Multiple versions of {wheel.distribution_name} found in wheelhouse (not implemented)"
    #     return all_wheels

    def refresh_pip_tools_cache(
        pip_tools_cache: Path, all_wheels: ty.Dict[str, WheelSource]
    ) -> Path:
        """
        Initializes the pip-compile cache, ensuring that the cache is not stale
        for any of the provided wheels.
        """

        for cache_file in pip_tools_cache.glob("depcache-cp*.json"):
            if not cache_file.is_file():
                continue

            cache = json.loads(cache_file.read_text())
            packages_to_refresh = {}

            for name, versions in cache.get("dependencies", {}).items():
                if (
                    name not in all_wheels
                    or str(all_wheels[name].version) not in versions
                ):
                    continue
                wheel = all_wheels[name]
                cached_reqs = versions.get(str(wheel.version), None)
                if set(Requirement(r) for r in cached_reqs) != wheel.requirements:
                    packages_to_refresh[(name, wheel.version)] = wheel.requirements

            if packages_to_refresh:
                for (name, version), requirements in packages_to_refresh.items():

                    package_cache = cache.setdefault("dependencies", {}).setdefault(
                        name, {}
                    )
                    if requirements is not None:
                        package_cache[str(version)] = [str(r) for r in requirements]
                    elif str(version) in package_cache:
                        del package_cache[str(version)]
                cache_file.write_text(json.dumps(cache))
        return pip_tools_cache

    wheels = []
    specs = []

    for req in requirements:
        if isinstance(req, WheelSource):
            wheels.append(req)
            wheel_path = req.path.resolve().as_uri()
            specs.append(f"{req.distribution_name} @ {wheel_path}")
        elif isinstance(req, str):
            specs.append(str(Requirement(req)))
        else:
            specs.append(str(req))

    if pip_tools_cache:
        refresh_pip_tools_cache(
            pip_tools_cache, {w.distribution_name: w for w in wheels}
        )
        cache_flag = ["--cache-dir", str(pip_tools_cache.resolve())]
    else:
        cache_flag = ["--rebuild"]

    upgrade_packages = list(
        set(upgrade_packages).union([w.distribution_name for w in wheels])
    )
    upgrade_packages_args = []
    if upgrade:
        upgrade_packages_args = ["--upgrade"]
    else:
        for to_upgrade in upgrade_packages:
            upgrade_packages_args.extend(["-P", to_upgrade])
    return venv.run_module(
        "piptools",
        "compile",
        "-",  # read specs from stdin
        "--output-file",
        str(output_path.resolve()),
        "-f",
        str(wheelhouse.absolute()),
        "--no-emit-find-links",
        *cache_flag,
        *upgrade_packages_args,
        input="\n".join(specs),
    )
