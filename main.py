from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer

query = """
    select distinct ?s (count(?s) as ?count)
    FROM <http://dbpedia.org>
    FROM NAMED <http://dbpedia.org>
    where {
        ?s ?p ?o .
    }
"""

tree = sparql_parser.parse(query)

sparql_serializer = SparqlSerializer()
sparql_serializer.visit_topdown(tree)

print(query)
print(f"Tree: {tree}")
print(f"\nNew query:\n{sparql_serializer.result}")

new_tree = sparql_parser.parse(sparql_serializer.result)
print(f"\nQuery is the same: {tree == new_tree}")
assert tree == new_tree
