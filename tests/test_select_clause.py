from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer


def test():
    query = """
        select distinct ?s (count(?s) as ?count)
        FROM <http://dbpedia.org>
        FROM NAMED <http://dbpedia.org>
        where {
            ?s ?p ?o .
            ?o ?pp ?oo ;
                ?ppp ?ooo .
            OPTIONAL {
                ?s a ?o .
            } .
            ?o2 ?p2 ?o3 .
        }
    """

    tree = sparql_parser.parse(query)

    sparql_serializer = SparqlSerializer()
    sparql_serializer.visit_topdown(tree)

    new_tree = sparql_parser.parse(sparql_serializer.result)
    assert tree == new_tree, sparql_serializer.result
