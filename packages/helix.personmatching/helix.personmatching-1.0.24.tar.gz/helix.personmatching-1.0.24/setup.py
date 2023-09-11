# noinspection Mypy
from typing import Any

from setuptools import setup, find_packages
from os import path, getcwd

# from https://packaging.python.org/tutorials/packaging-projects/

# noinspection SpellCheckingInspection
package_name = "helix.personmatching"

with open("README.md", "r") as fh:
    long_description = fh.read()

try:
    with open(path.join(getcwd(), "VERSION")) as version_file:
        version = version_file.read().strip()
except IOError:
    raise


def fix_setuptools() -> None:
    """Work around bugs in setuptools.

    Some versions of setuptools are broken and raise SandboxViolation for normal
    operations in a virtualenv. We therefore disable the sandbox to avoid these
    issues.
    """
    try:
        from setuptools.sandbox import DirectorySandbox

        # noinspection PyUnusedLocal
        def violation(operation: Any, *args: Any, **_: Any) -> None:
            print("SandboxViolation: %s" % (args,))

        DirectorySandbox._violation = violation
    except ImportError:
        pass


# Fix bugs in setuptools.
fix_setuptools()


# classifiers list is here: https://pypi.org/classifiers/

# create the package setup
setup(
    name=package_name,
    version=version,
    author="Imran Qureshi",
    author_email="imran@icanbwell.com",
    description="helix.personmatching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/icanbwell/helix.personmatching",
    packages=find_packages(),
    install_requires=[
        "rapidfuzz>=2.0.0",
        "fhir.resources>=7.0.2",
        "usaddress>=0.5.0",
        "usaddress-scourgify>=0.2.0",
        "phonenumbers>=8.0.0",
        "phonetics>=1.0.0",
        "nominally>=1.1.0",
        "nicknames>=0.1.3",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    dependency_links=[],
    include_package_data=True,
    zip_safe=False,
    package_data={"helix_personmatching": ["py.typed"]},
)
