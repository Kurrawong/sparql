from pathlib import Path

import pytest

from tests import files_from_data_directory

current_dir = Path(__file__).parent
data_dir = current_dir / 'data/sparql_test_suite_from_rdf_tests'


@pytest.mark.parametrize(
    "file",
    [
        *files_from_data_directory(
            data_dir,
            {
                (data_dir / "sparql11/syntax-update-2/large-request-01.ru").resolve(): "Downside to the current serializer is that it uses a recursive approach to walk the AST. This large query hits the standard Python recursion depth limit.",
            },
        )
    ],
)
def test(file: str, test_roundtrip):
    test_roundtrip(file)
