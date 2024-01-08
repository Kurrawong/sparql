import pytest

from tests import files_from_data_directory


@pytest.mark.parametrize(
    "file",
    [
        *files_from_data_directory(
            "sparql_spec_examples",
            {
                "data/sparql_spec_examples/16.4.2_identifying_resources_3.rq": "Grammar rule error: PN_CHARS_BASE"
            },
        ),
    ],
)
def test(file: str, test_roundtrip):
    test_roundtrip(file)
