from sparql.parser import sparql_parser as sparql_parser
from sparql.serializer import SparqlSerializer

query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?name ?mbox
 WHERE { ?x foaf:name  ?name ;
            foaf:mbox  ?mbox .
         FILTER regex(str(?mbox), "@work\\.example$") }
"""


# with open("tests/data/sparql_test_suite_from_rdf_tests/sparql11/syntax-query/1val1STRING_LITERAL1_with_UTF8_boundaries_escaped.rq", "r", encoding="utf-8") as file:
#     query = file.read()
# with open("tests/data/sparql_test_suite_from_rdf_tests/sparql10/syntax-sparql1/syntax-lit-13.rq", "r", encoding="utf-8") as file:
#     query = file.read()
# with open("tests/data/sparql_spec_examples/17.4.2.5_functions_on_rdf_terms_str.rq", "r", encoding="utf-8") as file:
#     query = file.read()

tree = sparql_parser.parse(query)

sparql_serializer = SparqlSerializer()
sparql_serializer.visit_topdown(tree)

print(query)
print(f"Tree: {tree}")
print(f"\nNew query:\n{sparql_serializer.result}")

new_tree = sparql_parser.parse(sparql_serializer.result)
print(f"\nQuery is the same: {tree == new_tree}")
assert tree == new_tree
