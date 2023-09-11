import pathlib
import typing as t

import setuptools
from dunamai import Version

SETUP_MODULE = pathlib.Path(__file__).absolute()
ROOTDIR = SETUP_MODULE.parent


def read_requirements_file(path: pathlib.Path) -> t.Tuple[t.List[str], t.List[str]]:
    if not (path.exists() and path.is_file()):
        raise RuntimeError(f'Did not find requirements file - {path.name}')
    dependencies = []
    dependencies_links = []
    for line in path.open("r").readlines():
        if "-f" in line or "--find-links" in line:
            dependencies_links.append(
                line
                .replace("-f", "")
                .replace("--find-links", "")
                .strip()
            )
        else:
            dependencies.append(line)
    return dependencies, dependencies_links


# ===============================================================

install_requires, dependency_links = read_requirements_file(ROOTDIR / 'requirements.txt')


setuptools.setup(
    name="deepchecks-llm-client",
    version="0.3.1",
    author="deepchecks",
    author_email="info@deepchecks.com",
    description="The SDK client for communicating with Deepchecks LLM service",
    packages=setuptools.find_packages(where=".", include=["deepchecks_llm_client", "deepchecks_llm_client.*"]),
    python_requires='>=3.8',
    install_requires=install_requires,
    dependency_links=dependency_links,
    include_package_data=True,
)