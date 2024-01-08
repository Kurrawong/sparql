import pytest

from tests import files_from_data_directory


@pytest.mark.parametrize(
    "file",
    [
        *files_from_data_directory(
            "sparql11_federated_spec_examples",
        )
    ],
)
def test(file: str, test_roundtrip):
    test_roundtrip(file)
