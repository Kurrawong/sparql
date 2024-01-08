from typing import Iterator
from pathlib import Path

import pytest
from _pytest.mark import ParameterSet

TEST_DIR = Path(__file__).parent


def files_from_data_directory(
    data_directory: str, xfail: dict[str, str] = None
) -> Iterator[str | ParameterSet]:
    """Return an iterator of files for a paramtrized test.

    Currently, hardcoded to return files ending in .rq.
    This may be generalised to accept any file suffixes in the future.

    :param data_directory: The directory of files.
    :param xfail: A dictionary of file paths and the reason on why the test should be xfailed.
    """
    if xfail is None:
        xfail = {}

    source_path = TEST_DIR / "data" / data_directory
    file_paths = list(source_path.glob("*.rq"))

    for file_path in file_paths:
        value = str(file_path.relative_to(TEST_DIR))
        if value not in xfail:
            yield value
        else:
            yield pytest.param(value, marks=pytest.mark.xfail(reason=xfail[value]))
