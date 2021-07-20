import os
import runpy
from typing import Optional, cast

from setuptools import setup


def get_version_from_pyfile(version_file: str = "hadolint_get.py") -> str:
    file_globals = runpy.run_path(version_file)
    return cast(str, file_globals["__version__"])


def get_long_description_from_readme(readme_filename: str = "README.md") -> Optional[str]:
    long_description = None
    if os.path.isfile(readme_filename):
        with open(readme_filename, "r", encoding="utf-8") as readme_file:
            long_description = readme_file.read()
    return long_description


version = get_version_from_pyfile()
long_description = get_long_description_from_readme()

setup(
    name="hadolint-get",
    version=version,
    py_modules=["hadolint_get"],
    python_requires="~=3.3",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "hadolint-get = hadolint_get:main",
        ]
    },
    author="Ingo Meyer",
    author_email="i.meyer@fz-juelich.de",
    description="A tool which downloads a specific hadolint version and executes it.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/IngoMeyer441/hadolint-get",
    keywords=["hadolint", "Dockerfile", "pre-commit", "linter"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: MS-DOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Utilities",
    ],
)
