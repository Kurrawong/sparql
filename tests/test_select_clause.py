import pytest

from tests import content_from_data_directory


@pytest.mark.parametrize("file, query", [*content_from_data_directory("select_clause")])
def test(file: str, query: str, test_roundtrip):
    test_roundtrip(query)
