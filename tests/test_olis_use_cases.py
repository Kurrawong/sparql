import pytest

from tests import files_from_data_directory


@pytest.mark.parametrize("file", [*files_from_data_directory("olis_use_cases")])
def test(file: str, test_roundtrip):
    test_roundtrip(file)
