import pytest

from tests import files_from_data_directory


@pytest.mark.parametrize(
    "file",
    [
        *files_from_data_directory(
            "sparql11_syntax_query_test_suite/positive",
            {
                "data/sparql11_syntax_query_test_suite/positive/syntax-bindings-03a.rq": "Fails roundtrip as the serializer drops the NIL value (empty open and close parenthesis)",
                "data/sparql11_syntax_query_test_suite/positive/syntax-bindings-02a.rq": "Fails roundtrip as the serializer drops the NIL value (empty open and close parenthesis)",
            },
        )
    ],
)
def test(file: str, test_roundtrip):
    test_roundtrip(file)
