from sparql.parser import sparql_update_parser as sparql_parser
from sparql.serializer import SparqlSerializer

query = r'''
PREFIX : <http://www.example.org/>

INSERT DATA { 
              GRAPH<g1> { _:b1 :p :o } 
              GRAPH<g2> { _:b1 :p :o } 
            }

'''

tree = sparql_parser.parse(query)

sparql_serializer = SparqlSerializer()
sparql_serializer.visit_topdown(tree)

print(query)
print(f"Tree: {tree}")
print(f"\nNew query:\n{sparql_serializer.result}")

new_tree = sparql_parser.parse(sparql_serializer.result)
print(f"\nQuery is the same: {tree == new_tree}")
assert tree == new_tree
