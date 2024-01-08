from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer

query = """
PREFIX aGeo: <http://example.org/geo#>

SELECT ?neighbor
WHERE { ?a aGeo:placeName "Grenoble" .
        ?a aGeo:locationX ?axLoc .
        ?a aGeo:locationY ?ayLoc .

        ?b aGeo:placeName ?neighbor .
        ?b aGeo:locationX ?bxLoc .
        ?b aGeo:locationY ?byLoc .

        FILTER ( aGeo:distance(?axLoc, ?ayLoc, ?bxLoc, ?byLoc) < 10 ) .
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
