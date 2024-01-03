from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer


def test_writing_a_simple_query():
    query = """
        SELECT ?title
        WHERE
        {
          <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title .
        }
    """

    tree = sparql_parser.parse(query)

    sparql_serializer = SparqlSerializer()
    sparql_serializer.visit_topdown(tree)

    new_tree = sparql_parser.parse(sparql_serializer.result)
    assert tree == new_tree, sparql_serializer.result


def test_str():
    query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?mbox
         WHERE { ?x foaf:name  ?name ;
                    foaf:mbox  ?mbox .
                 FILTER regex(str(?mbox), "@work\\.example$") }
    """

    tree = sparql_parser.parse(query)

    sparql_serializer = SparqlSerializer()
    sparql_serializer.visit_topdown(tree)

    new_tree = sparql_parser.parse(sparql_serializer.result)
    assert tree == new_tree, sparql_serializer.result
