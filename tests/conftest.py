import pytest

from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer


@pytest.fixture
def test_roundtrip():
    def _test_roundtrip(query: str):
        tree = sparql_parser.parse(query)

        sparql_serializer = SparqlSerializer()
        sparql_serializer.visit_topdown(tree)

        new_tree = sparql_parser.parse(sparql_serializer.result)
        assert tree == new_tree, sparql_serializer.result

    return _test_roundtrip