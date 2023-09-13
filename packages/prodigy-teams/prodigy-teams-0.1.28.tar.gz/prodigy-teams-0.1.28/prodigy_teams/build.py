import ast
import itertools
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import warnings
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Literal, Optional, Set, Union

import packaging.tags
import packaging.utils
import pkginfo
import setuptools
from packaging.requirements import Requirement  # noqa: F401
from packaging.specifiers import SpecifierSet  # noqa: F401
from packaging.version import Version

from . import ty
from .appdirs import user_cache_dir

logger = logging.getLogger(__name__)

RecipeSourceKind = Literal["wheel", "distribution"]


class RecipeBuildVenvCreationFailed(Exception):
    pass


class RecipeSource(object):
    path: Path

    @classmethod
    def from_path(cls, path: Union[Path, str]) -> Optional["RecipeSource"]:
        if isinstance(path, str):
            path = Path(path)
        kind = cls._infer_kind(path)
        if kind == "wheel":
            return WheelSource(path)
        elif kind == "distribution":
            return DirectorySource(path)
        else:
            return None

    def __init__(
        self,
        path: Path,
    ):
        self.path = path

    @classmethod
    def _infer_kind(cls, path: Path) -> Optional[RecipeSourceKind]:
        if path.is_file() and path.suffix == ".whl":
            return "wheel"

        if path.is_dir() and (
            (path / "setup.py").is_file() or (path / "pyproject.toml").is_file()
        ):
            return "distribution"
        return None

    @cached_property
    def path_kind(self):
        return self._infer_kind(self.path)

    @cached_property
    def version(self) -> Optional[Version]:
        ...

    @cached_property
    def distribution_name(self) -> str:
        ...

    @cached_property
    def package_name(self) -> str:
        # TODO: this should be the name of the top level package, not the
        # distribution/wheel.
        assert self.distribution_name is not None

        package_name = re.sub(r"[^\w\d.]+", "_", self.distribution_name, re.UNICODE)
        return package_name

    @cached_property
    def pkginfo_metadata(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            maybe_pkginfo = pkginfo.get_metadata(str(self.path.resolve()))
            if maybe_pkginfo is not None and maybe_pkginfo.name is not None:
                return maybe_pkginfo
        return None

    @cached_property
    def requirements(self) -> Optional[Set[Requirement]]:
        if self.pkginfo_metadata is None:
            return None
        return set(Requirement(line) for line in self.pkginfo_metadata.requires_dist)


class WheelSource(RecipeSource):
    @cached_property
    def wheel_info(self) -> pkginfo.Wheel:
        metadata = self.pkginfo_metadata
        assert isinstance(
            metadata, pkginfo.Wheel
        ), f"expected pkginfo metadata to be Wheel, got {type(metadata)}"
        return metadata

    @cached_property
    def distribution_name(self) -> str:
        return self.wheel_info.name

    @cached_property
    def version(self) -> Version:
        return Version(self.wheel_info.version)

    def to_file_uri(self) -> str:
        return self.path.resolve().as_uri()


class DirectorySource(RecipeSource):
    def __init__(self, directory: Path):
        super().__init__(directory)
        # TODO: infer correctly
        name = self.package_name
        name_as_path = name.replace(".", os.sep)
        pkg_dir = directory / name_as_path
        src_pkg_dir = directory / "src" / name_as_path

        existing = set()
        if pkg_dir.is_dir():
            self.pkg_dir = pkg_dir
            self.prefix = ""
            existing.add(pkg_dir)
        if src_pkg_dir.is_dir():
            self.pkg_dir = src_pkg_dir
            self.prefix = "src"
            existing.add(src_pkg_dir)

        if len(existing) > 1:
            raise ValueError(
                "Multiple matches for package name {}: {}".format(
                    name, ", ".join([str(p) for p in sorted(existing)])
                )
            )
        elif not existing:
            raise ValueError("No package directory found for module {}".format(name))

        self.source_dir = directory / self.prefix
        self.directory = directory

        if "." in name:
            logger.warn(
                "Package name %s contains a dot and may not work as intended.", name
            )
            self.namespace_package_name = name.rpartition(".")[0]
            self.in_namespace_package = True

    @cached_property
    def version(self) -> Optional[Version]:
        from_ast = get_version_from_ast(self)
        if from_ast is not None:
            return Version(from_ast)
        # TODO: import in a subprocess or just build metadata eagerly using _build_meta
        # from_import = get_version_from_import(self)
        # if from_import is not None:
        #     return Version(from_import)
        return None

    @cached_property
    def distribution_name(self) -> str:
        cached_metadata = self.pkginfo_metadata
        if cached_metadata is not None:
            return cached_metadata.name
        # TODO: we probably need to do a wheel build to be sure
        distribution_name = re.sub(
            r"[^\w\d]+", "_", self.package_name, re.UNICODE
        ).replace("_", "-")
        return distribution_name

    @cached_property
    def discovered_packages(self):
        all_discovered = setuptools.find_packages(
            where=str(self.path), exclude=("tests", "tests.*")
        )
        return [p for p in all_discovered if p.find(".") == -1]

    @cached_property
    def package_name(self):
        discovered_packages = self.discovered_packages
        if len(discovered_packages) == 1:
            return discovered_packages[0]
        elif len(discovered_packages) == 0:
            raise ValueError(
                f"Could not infer package name from directory: {self.path}"
            )
        else:
            raise ValueError(
                f"Found multiple packages in directory {self.path}: {discovered_packages}"
            )

    @property
    def file(self):
        return self.pkg_dir / "__init__.py"

    @property
    def version_files(self):
        paths = [self.pkg_dir / "__init__.py"]
        for filename in ("about.py", "version.py", "_version.py", "__version__.py"):
            if (self.pkg_dir / filename).is_file():
                paths.insert(0, self.pkg_dir / filename)
        return paths

    def iter_files(self):
        def _include(path):
            name = os.path.basename(path)
            if (name == "__pycache__") or name.endswith(".pyc"):
                return False
            return True

        for dirpath, dirs, files in os.walk(str(self.pkg_dir)):
            for file in sorted(files):
                full_path = os.path.join(dirpath, file)
                if _include(full_path):
                    yield full_path

            dirs[:] = [d for d in sorted(dirs) if _include(d)]


def get_version_from_ast(target: DirectorySource):
    def _extract_version_assignment(node: ast.stmt) -> Optional[ast.Assign]:
        if not isinstance(node, ast.Assign):
            return None
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                # TODO: multiple assignment?
                return node
        return None

    def _extract_literal_version(node: ast.Assign) -> Optional[str]:
        if isinstance(node.value, ast.Str):
            return node.value.s
        return None

    version = None
    node = None
    for version_path in target.version_files:
        with version_path.open("rb") as f:
            node = ast.parse(f.read())
        for child in node.body:
            assignment = _extract_version_assignment(child)
            if assignment is not None:
                version = _extract_literal_version(assignment)
                if version is not None:
                    break
            else:
                # programmatically generated version - we need to use imports
                pass
    assert node is not None, f"no __version__ found in module {target.package_name}"
    return version


_IMPORT_COUNTER = 0


def get_version_from_import(target: DirectorySource):
    """
    Import the module and extract the version from it.
    """
    global _IMPORT_COUNTER
    from importlib.util import module_from_spec, spec_from_file_location

    @contextmanager
    def stash_global_state():
        """
        Stash global state that modules might change at import time.

        TODO: Can we stash sys.modules, recipe registry, here?
        """
        logging_handlers = logging.root.handlers[:]
        try:
            yield
        finally:
            logging.root.handlers = logging_handlers

    _IMPORT_COUNTER += 1

    mod_name = f"prodigy_teams.imported_recipe.{_IMPORT_COUNTER}"
    spec = spec_from_file_location(mod_name, target.file)
    assert spec is not None, f"Failed to load module from {target.file}"
    assert spec.loader is not None
    with stash_global_state():
        m = module_from_spec(spec)
        sys.modules[mod_name] = m
        try:
            spec.loader.exec_module(m)
        finally:
            imported_mods = [mod for mod in sys.modules if mod.startswith(mod_name)]
            for mod in imported_mods:
                sys.modules.pop(mod, None)

    version = m.__dict__.get("__version__", None)
    return version


def get_version_from_pkginfo(target: DirectorySource):
    """
    Get the version from the .egg-info/.dist-info folders

    This version is computed when the package is built, so it's not
    necessarily the same as the version in the source code.
    """

    meta = pkginfo.get_metadata(str(target.source_dir))
    assert meta is not None
    return meta.version


class Venv:
    def __init__(self, python_binary: str, cwd: ty.Optional[Path] = None) -> None:
        self.python = python_binary
        self._default_cwd = cwd

    @classmethod
    @contextmanager
    def from_active(cls, cwd: ty.Optional[Path]) -> ty.Iterator["Venv"]:
        yield cls(sys.executable, cwd=cwd)

    @classmethod
    @contextmanager
    def temporary(cls, cwd: ty.Optional[Path] = None) -> ty.Iterator["Venv"]:
        with _make_tempdir() as tmp:
            venv_path = Path(tmp) / "venv"
            _subprocess_run(
                [sys.executable, "-m", "venv", str(venv_path.absolute())],
                cwd or Path.cwd(),
            )
            yield cls(str(venv_path / "bin" / "python"), cwd)

    @classmethod
    def _get_venv_cache_path(cls, package_name: str, mkdir: bool = False) -> Path:
        cache_key = (package_name,)
        cache_path = user_cache_dir(
            # the version key here should be updated if we make breaking changes to the cache contents
            appname="Prodigy Teams",
            appauthor="Explosion",
            version="0.1",
        )
        cached_venv = (Path(cache_path) / "venvs" / "+".join(cache_key)).absolute()
        if mkdir:
            cached_venv.parent.mkdir(exist_ok=True, parents=True)
        return cached_venv

    @classmethod
    def _find_python_bin(cls, venv_base: Path) -> Optional[Path]:
        if sys.platform == "win32":
            return venv_base / "Scripts" / "python.exe"
        else:
            for candidate in ["local/bin", "bin"]:
                bin_path = venv_base / candidate / "python"
                if bin_path.exists():
                    return bin_path
        return None

    def cwd(self, override: ty.Optional[Path] = None) -> Path:
        return override or self._default_cwd or Path.cwd()

    def install(
        self,
        *packages: str,
        upgrade: bool = False,
        no_deps: bool = False,
        find_links: ty.List[Path] = [],
        cwd: ty.Optional[Path] = None,
    ) -> subprocess.CompletedProcess:
        args = [self.python, "-m", "pip", "install"]
        args.append("--disable-pip-version-check")
        if upgrade:
            args.append("--upgrade")
        if no_deps:
            args.append("--no-deps")
        if find_links:
            for dir in find_links:
                args.extend(["-f", str(dir)])
        args.extend(packages)
        return _subprocess_run(args, self.cwd(cwd))

    def _run(
        self, *args: str, cwd: ty.Optional[Path] = None, input: ty.Optional[str] = None
    ) -> subprocess.CompletedProcess:
        # XXX: Fixme. Run with the correct path for the virtual environment
        return _subprocess_run([*args], self.cwd(cwd), input=input)

    def run(
        self, *args: str, cwd: ty.Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        return _subprocess_run([self.python, *args], self.cwd(cwd))

    def run_module(
        self,
        entrypoint: str,
        *args: str,
        cwd: ty.Optional[Path] = None,
        input: ty.Optional[str] = None,
    ) -> subprocess.CompletedProcess:
        return _subprocess_run(
            [self.python, "-m", entrypoint, *args], self.cwd(cwd), input=input
        )

    @classmethod
    def cached(
        cls,
        package_name: str,
        build_venv: "Venv",
        cwd: ty.Optional[Path] = None,
    ) -> "Venv":
        cached_venv = cls._get_venv_cache_path(package_name, mkdir=True)
        python_bin = cls._find_python_bin(cached_venv)
        try:
            if python_bin is None or not python_bin.exists():
                shutil.rmtree(cached_venv, ignore_errors=True)
                build_venv.run_module("venv", str(cached_venv.absolute()))
                python_bin = cls._find_python_bin(cached_venv)
                assert (
                    python_bin is not None and python_bin.exists()
                ), f"Failed to locate python binary after creating venv: {cached_venv} ({python_bin=})"
        except subprocess.CalledProcessError as e:
            message = f"""Unexpected failure while creating virtualenv:
            ### Error: {e.__class__.__name__}
            cmd: {str(e.cmd)}
            return code: {str(e.returncode)}
            ### Stdout
            {e.stdout}
            ### Stderr
            {e.stderr}

            ### Debug Info:
            build_venv: {build_venv.python}
            - {Path(build_venv.python).exists()=}
            - {Path(build_venv.python).is_file()=}

            cached_venv: {str(cached_venv)}
            - {cached_venv.exists()=}
            - {cached_venv.absolute()=}
            - {list(cached_venv.glob("*"))=}
            - {python_bin=} ({"exists" if python_bin and python_bin.exists() else "not found"})
            """
            raise RecipeBuildVenvCreationFailed(message)

        return Venv(str(python_bin), cwd=cwd)


class RequirementSet:
    def __init__(self, requirements: ty.Iterable[ty.Union[Requirement, str]]) -> None:
        self._requirements = frozenset(
            [Requirement(r) if isinstance(r, str) else r for r in requirements]
        )

    def _validate(self, requirement: Requirement) -> None:
        if requirement.name is None:
            raise ValueError("Invalid requirement, must have a name")

    @cached_property
    def _by_name(self) -> ty.Dict[str, frozenset[Requirement]]:
        by_name = self.collect_by_name(self._requirements)
        return by_name

    def __iter__(self) -> ty.Iterator[Requirement]:
        return iter(sorted(self._requirements, key=lambda r: str(r)))

    def __len__(self) -> int:
        return len(self._requirements)

    def __contains__(self, item: ty.Any) -> bool:
        if isinstance(item, str):
            # item must be a distribution name
            return item in self._by_name
        elif isinstance(item, Requirement):
            # item is an exact requirement
            return item in self._requirements
        else:
            raise TypeError(f"Expected str or Requirement, got {type(item)}")

    def __getitem__(self, item: str) -> ty.Optional[frozenset[Requirement]]:
        return self._by_name.get(item, frozenset())

    def __repr__(self) -> str:
        return f"RequirementSet({list(self)})"

    def __eq__(self, other: ty.Any) -> bool:
        if not isinstance(other, RequirementSet):
            return NotImplemented
        return self._requirements == other._requirements

    def __hash__(self) -> int:
        return hash(self._requirements)

    @classmethod
    def collect_by_name(
        cls, *iterables: ty.Iterable[ty.Union[Requirement, str]]
    ) -> ty.Dict[str, frozenset[Requirement]]:
        by_name = defaultdict(set)
        for r in itertools.chain(*iterables):
            req = Requirement(r) if isinstance(r, str) else r
            by_name[req.name].add(req)
        return {k: frozenset(v) for k, v in by_name.items()}

    def partition(
        self, include: ty.Callable[[Requirement], bool]
    ) -> ty.Tuple["RequirementSet", "RequirementSet"]:
        included = []
        excluded = []
        for req in self:
            if include(req):
                included.append(req)
            else:
                excluded.append(req)
        return RequirementSet(included), RequirementSet(excluded)

    def merge(
        self, *others: ty.Iterable[ty.Union[str, Requirement]]
    ) -> "RequirementSet":
        return RequirementSet(itertools.chain(self, *others))

    def replace_local_wheel_links(
        self, wheels_to_replace: ty.Optional[ty.Set[str]] = None
    ) -> "RequirementSet":
        def _should_replace(req: Requirement):
            name_matches = (
                wheels_to_replace is not None and req.name in wheels_to_replace
            )
            return name_matches and _get_local_wheel_url(req) is not None

        replace, keep = self.partition(_should_replace)
        replaced = []
        for req in replace:
            wheel_path = _get_local_wheel_url(req)
            assert (
                wheel_path is not None
            ), "expected local wheel to have a file:// url in compiled requirements file"
            parsed = WheelName.from_filename(wheel_path.name)
            replaced.append(Requirement(f"{parsed.name}=={str(parsed.version)}"))
        return keep.merge(replaced)

    @classmethod
    def from_txt(
        cls, txt: ty.Union[str, Path], ignore_comments: bool = True
    ) -> "RequirementSet":
        if isinstance(txt, Path):
            txt = txt.read_text()
        lines = txt.splitlines()
        lines = (line for line in lines if line.strip())
        if ignore_comments:
            lines = (line for line in lines if not line.lstrip().startswith("#"))

        return RequirementSet(lines)

    def to_txt(self) -> str:
        return "\n".join(str(req) for req in self)

    def to_lines(self) -> ty.List[str]:
        return [str(req) for req in self]


@dataclass
class WheelName:
    filename: str
    name: packaging.utils.NormalizedName
    version: str
    build: ty.Optional[ty.Tuple[int, str]]
    tags: ty.Set[packaging.tags.Tag]

    @classmethod
    def from_filename(cls, filename: str) -> "WheelName":
        name, version, build, tags = packaging.utils.parse_wheel_filename(filename)
        return cls(
            filename=filename,
            name=name,
            version=str(version),
            build=build if build else None,
            tags=set(tags),
        )


def _get_local_wheel_url(req: Requirement) -> ty.Optional[Path]:
    if req.url is not None and req.url.startswith("file://"):
        url_path = Path(req.url)
        if url_path.suffix == ".whl":
            return url_path
    return None


def _subprocess_run(
    args: ty.List[str], cwd: Path, input: ty.Optional[str] = None
) -> subprocess.CompletedProcess:
    try:
        ret = subprocess.run(
            args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=True,
            input=input,
            encoding="utf8",
        )
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise
    return ret


@contextmanager
def _make_tempdir() -> ty.Generator[Path, None, None]:
    """Execute a block in a temporary directory and remove the directory and
    its contents at the end of the with block.

    YIELDS (Path): The path of the temp directory.
    """
    d = Path(tempfile.mkdtemp())
    yield d
    shutil.rmtree(str(d))
