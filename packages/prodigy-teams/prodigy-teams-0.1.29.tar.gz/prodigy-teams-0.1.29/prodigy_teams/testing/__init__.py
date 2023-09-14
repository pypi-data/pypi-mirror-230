import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, Union

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version, parse
from pydantic import BaseModel
from pydantic.decorator import validator


class PackageSpec(BaseModel):
    package_name: str
    root_name_override: Optional[str] = None
    version: Version = Version("0.0.1")
    requirements: List[Requirement] = []

    @validator("version", pre=True)
    def _validate_version(cls, v: Union[str, Version]):
        if isinstance(v, Version):
            return v
        return parse(v)

    @property
    def root_name(self) -> str:

        if self.root_name_override is None:
            return self.package_name
        return self.root_name_override

    @classmethod
    def _parse_requirement(
        cls, package: str, specifier: Union[Version, SpecifierSet, None] = None
    ) -> Requirement:
        if specifier is None:
            specifier = SpecifierSet()
        elif isinstance(specifier, Version):
            specifier = SpecifierSet(f"=={specifier}")
        return Requirement(f"{package}{specifier}")

    def add_requirement(
        self, package: str, specifier: Union[Version, SpecifierSet, None] = None
    ) -> Requirement:
        req = self._parse_requirement(package, specifier)
        self.requirements.append(req)
        return req

    class Config:
        arbitrary_types_allowed = True


class PackageBuilder:
    def __init__(
        self,
        parent_dir: Path,
        spec: PackageSpec,
    ):
        self.parent_dir = (
            parent_dir if isinstance(parent_dir, Path) else Path(parent_dir)
        )
        self.spec = spec.copy(deep=True)

    @property
    def root_path(self) -> Path:
        return self.parent_dir / self.spec.root_name

    @property
    def package_path(self) -> Path:
        return self.root_path / self.spec.package_name

    def write_setup(self):
        setup_path = self.root_path / "setup.py"
        setup_path.write_text(
            f"""#!/usr/bin/env python
from setuptools import setup
from pathlib import Path

PWD = Path(__file__).parent
root = PWD.resolve()

about_path = root / {repr(self.spec.package_name)} / "about.py"
with about_path.open("r", encoding="utf8") as f:
    about = {{}}
    exec(f.read(), about)

requirements_path = root / "requirements.in"
with requirements_path.open("r", encoding="utf8") as f:
    requirements = [line.strip() for line in f]

setup(name=about["__name__"],
      version=about["__version__"],
      description=about["__summary__"],
      url=about["__url__"],
      author=about["__author__],
      author_email=about["__email__"],
      license='MIT',
      packages=[about["__name__"]],
      zip_safe=False)
"""
        )

    def write_about(self):
        about_path = self.package_path / "about.py"
        about_path.write_text(
            f"""__title__ = {repr(self.spec.package_name)}
__name__ = {repr(self.spec.package_name)}
__version__ = {repr(str(self.spec.version))}
__summary__ = 'Mock package'
__email__ = 'contact@explosion.ai'
__author__ = 'Explosion'
__uri__ = 'https://explosion.rocks'
__license__ = 'MIT'
            """
        )

    def write_requirements(self):
        requirements_path = self.root_path / "requirements.in"
        requirements_path.write_text(
            "\n".join([str(r) for r in self.spec.requirements])
        )

    def write_init(self):
        init_path = self.package_path / "__init__.py"
        init_path.write_text(f"""from .about import *""")

    def write(self, exists_ok: bool = False):
        self.root_path.mkdir(exist_ok=exists_ok)
        self.package_path.mkdir(exist_ok=exists_ok)
        self.write_setup()
        self.write_about()
        self.write_requirements()
        self.write_init()

    def delete(self):
        shutil.rmtree(self.root_path)

    def __enter__(self):
        self.write()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()
