import os
import pathlib
import tempfile
from typing import Dict, Generator, List, Tuple

import pytest

from vessl.util.vesslignore import list_files_using_vesslignore


@pytest.fixture()
def vesslignore_test_files(tmp_path: pathlib.Path):
    """
    Pytest fixture function that prepares and removes files for .vesslignore test.
    """

    ignore_contents: Dict[str, List[str]] = {}
    files_to_write: List[Tuple[str, bool]] = []  # (path, should_exist)

    def _add_ignore(pattern, write_to=".vesslignore"):
        if write_to not in ignore_contents:
            ignore_contents[write_to] = []
        ignore_contents[write_to].append(pattern)

    def _expect_present(filename):
        nonlocal files_to_write
        files_to_write.append((filename, True))

    def _expect_ignored(filename):
        nonlocal files_to_write
        files_to_write.append((filename, False))

    # Comment
    _add_ignore("# Comments should work")

    # Simple bans
    _add_ignore("*.o")
    _add_ignore(".*.sw?")  # Vim swap files -- to test '?'
    _expect_present("SHOWN")
    _expect_ignored("HIDDEN.o")
    _expect_ignored(".HIDDEN.swp")
    _expect_ignored(".HIDDEN.swo")
    _expect_present("SHOWN.obj")  # do not allow the partial match 'SHOWN.o'
    # Simple bans in subdirectory
    _expect_present("data1/SHOWN")
    _expect_ignored("data1/HIDDEN.o")
    _expect_ignored("data1/.HIDDEN.swp")
    _expect_ignored("data1/.HIDDEN.swo")
    # Simple bans should match directory names, too
    _add_ignore("HIDDEN_DIR?")
    _expect_ignored("data1/HIDDEN_DIR3/HIDDEN.txt")

    # Patterns with '**/' should match in all places
    _add_ignore("**/animal/cat")
    _expect_present("data2/animal/dog")
    _expect_ignored("data2/animal/cat")
    _expect_ignored("data2/dist/animal/cat/mango")  # directory match
    _expect_present("data2/animal/catto")  # basename should match exactly, not prefixed
    # Trailing slash should force directory match
    _add_ignore("**/fruit/apples/")
    _expect_present("data2/fruit/apples")
    _expect_ignored("data2/dist/fruit/apples/Macintosh")

    # Relative path from root
    _add_ignore("data3/instrument/viol*")
    _expect_present("data3/instrument/trumpet")
    _expect_ignored("data3/instrument/violin")
    _expect_ignored("data3/instrument/viola/3")  # directory match
    # wildcard inside path
    _add_ignore("data3/f?sh/*/tail")
    _expect_present("data3/fish/tuna/head")
    _expect_ignored("data3/fish/tuna/tail")
    _expect_present("data3/fish/tuna/tailor")  # basename should not be prefixed
    # Trailing slash should force directory match
    _add_ignore("data3/fish/*/head/")
    _expect_present("data3/fish/cod/heading")
    _expect_present("data3/fish/cod/head")
    _expect_ignored("data3/fish/octopus/head/eye")

    # .vesslignore in subdirectory
    def _add_ignore_sub(pattern):
        _add_ignore(pattern, "subdir/.vesslignore")

    # Subdirectory pattern test
    _add_ignore_sub("cat")
    _add_ignore_sub("**/SHOWN")
    _add_ignore_sub("SUB_IGNORE/")
    _expect_ignored("subdir/cat")
    _expect_present("subdir/catto")
    _expect_ignored("subdir/data1/HIDDEN.o")
    _expect_present("subdir/data2/SUB_IGNORE/blob")
    _expect_present("subdir/data3/SUB_IGNORE")
    _expect_ignored("subdir/SUB_IGNORE/blob")
    _expect_present("SUB_IGNORE/SHOWN")  # subdir pattern should not affect parent

    for filename, present in files_to_write:
        path = tmp_path / filename
        path.parent.mkdir(exist_ok=True, parents=True)
        path.touch()
        pass

    for ignore_filename, ignore_lines in ignore_contents.items():
        path = tmp_path / ignore_filename
        path.parent.mkdir(exist_ok=True, parents=True)

        ignore_content = "\n".join(ignore_lines) + "\n"
        path.open("w").write(ignore_content)

    yield (tmp_path, files_to_write)


class TestVesslIgnore:
    def test_list_files_using_vesslignore(
        self, vesslignore_test_files: Tuple[pathlib.Path, List[Tuple[str, bool]]]
    ):
        root_path, files_to_write = vesslignore_test_files

        files_found = list_files_using_vesslignore(str(root_path))

        for filename, should_exist in files_to_write:
            assert (filename in files_found) == should_exist
