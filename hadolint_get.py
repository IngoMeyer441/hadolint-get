#!/usr/bin/env python3

import argparse
import os
import pathlib
import platform
import re
import shutil
import stat
import subprocess
import sys
import urllib.request
from typing import List, NamedTuple, Optional, Tuple

__author__ = "Ingo Meyer"
__email__ = "i.meyer@fz-juelich.de"
__copyright__ = "Copyright © 2021 Forschungszentrum Jülich GmbH. All rights reserved."
__license__ = "MIT"
__version_info__ = (0, 1, 0)
__version__ = ".".join(map(str, __version_info__))


HADOLINT_GIT_URL = "https://github.com/hadolint/hadolint.git"
HADOLINT_EXECUTABLE_URL_TEMPLATE = (
    "https://github.com/hadolint/hadolint/releases/download/{version}/hadolint-{platform}-x86_64{suffix}"
)
SUPPORTED_PLATFORMS = (
    "Darwin",
    "Linux",
    "Windows",
)
PLATFORM_SUFFIX = {
    "Darwin": "",
    "Linux": "",
    "Windows": ".exe",
}


class PlatformUnsupportedError(Exception):
    def __init__(self, unsupported_platform: str) -> None:
        super().__init__(
            'The platform "{}" is unsupported. Supported platforms: "{}"'.format(
                unsupported_platform, '", "'.join(SUPPORTED_PLATFORMS)
            )
        )


class ExecutableNotFetchableError(Exception):
    pass


VersionMatch = NamedTuple("VersionMatch", [("match", str), ("version_components", Tuple[int, ...])])


def get_cache_directory_path(create: bool = True, clean: bool = False) -> str:
    def linux() -> str:
        try:
            return os.environ["XDG_CACHE_HOME"]
        except KeyError:
            return os.path.join(os.environ["HOME"], ".cache")

    def macos() -> str:
        return os.path.join(os.environ["HOME"], "Library/Caches")

    def windows() -> str:
        return os.environ["LOCALAPPDATA"]

    operating_system = platform.system()
    if operating_system not in SUPPORTED_PLATFORMS:
        raise PlatformUnsupportedError(operating_system)
    cache_directory_path = os.path.join(
        {
            "Linux": linux,
            "Darwin": macos,
            "Windows": windows,
        }[operating_system](),
        "hadolint-get",
    )
    if clean:
        shutil.rmtree(cache_directory_path)
    if create:
        pathlib.Path(cache_directory_path).mkdir(parents=True, exist_ok=True)
    return cache_directory_path


def get_latest_git_tag(url: str, version_regex: str = r"[vV]?(\d+)\.(\d+)(?:\.(\d+))?$") -> str:
    version_tag_regex = re.compile(r"(?<=refs/tags/)" + version_regex)
    git_ls_remote_output = subprocess.check_output(["git", "ls-remote", url], universal_newlines=True)
    git_tags = []
    for line in git_ls_remote_output.split("\n"):
        match_obj = version_tag_regex.search(line)
        if match_obj:
            git_tags.append(VersionMatch(match_obj.group(0), tuple(int(c) for c in match_obj.groups() if c)))
    latest_git_tag = max(git_tags, key=lambda version_match: version_match.version_components)
    return latest_git_tag.match


def fetch_hadolint(version: Optional[str] = None) -> str:
    if version is None or version == "latest":
        version = get_latest_git_tag(HADOLINT_GIT_URL)
    if not version.startswith("v"):
        version = "v" + version
    operating_system = platform.system()
    if operating_system not in SUPPORTED_PLATFORMS:
        raise PlatformUnsupportedError(operating_system)
    platform_suffix = PLATFORM_SUFFIX[operating_system]
    cache_directory_path = get_cache_directory_path()
    hadolint_executable_filepath = os.path.join(cache_directory_path, "hadolint-{}{}".format(version, platform_suffix))
    if not os.path.exists(hadolint_executable_filepath):
        download_url = HADOLINT_EXECUTABLE_URL_TEMPLATE.format(
            version=version, platform=operating_system, suffix=platform_suffix
        )
        try:
            with urllib.request.urlopen(download_url) as response:
                with open(hadolint_executable_filepath, "wb") as hadolint_executable:
                    shutil.copyfileobj(response, hadolint_executable)
            os.chmod(hadolint_executable_filepath, stat.S_IRUSR | stat.S_IXUSR)  # chmod 0500
        except urllib.error.URLError as e:
            raise ExecutableNotFetchableError(
                'Cannot fetch hadolint version "{}" for platform "{}".'.format(version, operating_system)
            ) from e
    return hadolint_executable_filepath


def get_argumentparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
%(prog)s downloads a specific hadolint version and executes it with given parameters.
Separate hadolint parameters with ` -- `.
""",
    )
    parser.add_argument(
        "-V",
        "--hadolint-version",
        action="store",
        dest="hadolint_version",
        help="hadolint version you would like to use; if omitted, use the latest available release",
    )
    parser.add_argument(
        "--print-tool-version",
        action="store_true",
        dest="print_tool_version",
        help="print the version number of this tool and exit",
    )
    return parser


def parse_arguments() -> Tuple[argparse.Namespace, List[str]]:
    def split_args() -> Tuple[List[str], List[str]]:
        try:
            split_index = sys.argv.index("--", 1)
            return sys.argv[1:split_index], sys.argv[split_index + 1 :]
        except ValueError:
            return sys.argv[1:], []

    this_arg_list, hadolint_arg_list = split_args()
    parser = get_argumentparser()
    args = parser.parse_args(this_arg_list)
    return args, hadolint_arg_list


def main() -> None:
    args, hadolint_args = parse_arguments()
    if args.print_tool_version:
        print("{}, version {}".format(os.path.basename(sys.argv[0]), __version__))
        sys.exit(0)
    exceptions = (
        PlatformUnsupportedError,
        ExecutableNotFetchableError,
        OSError,
    )
    try:
        hadolint_executable_filepath = fetch_hadolint(args.hadolint_version)
        subprocess.check_call([hadolint_executable_filepath] + hadolint_args)
    except exceptions as e:
        print(str(e), file=sys.stderr)
        for i, exception_class in enumerate(exceptions, start=3):
            if isinstance(e, exception_class):
                sys.exit(i)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
