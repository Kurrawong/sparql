from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer

query = """
    base <https://example.com/>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    
    values (?g ?s) {
        (<urn:graph:1> <urn:entity:1>)
        (<urn:graph:2> "some literal"@en)
        (<urn:graph:2> '''some literal
        blah
        '''@en)
        (<urn:graph:3> UNDEF)
        (<urn:graph:4> 123)
        (<urn:graph:5> true)
        (<urn:graph:6> false)
        (<urn:graph:7> "special token"^^xsd:token)
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
