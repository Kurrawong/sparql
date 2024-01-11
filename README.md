# Python SPARQL

This package provides parsers and serializers for the [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/).

## Usage

```python
from sparql.parser import sparql_parser, sparql_update_parser
from sparql.serializer import SparqlSerializer

query = r'''
PREFIX : <http://www.example.org/>

INSERT DATA { 
              GRAPH<g1> { _:b1 :p :o } 
              GRAPH<g2> { _:b1 :p :o } 
            }

'''

# For SPARQL 1.1 Update, use sparql_update_parser
tree = sparql_parser.parse(query)

sparql_serializer = SparqlSerializer()
sparql_serializer.visit_topdown(tree)

print(query)
print(f"Tree: {tree}")
print(f"\nNew query:\n{sparql_serializer.result}")

new_tree = sparql_parser.parse(sparql_serializer.result)
print(f"\nQuery is the same: {tree == new_tree}")
assert tree == new_tree

```

## Conformance

The parser and serializer is passing all positive tests found online, examples from the specification, and also the tests from the https://github.com/w3c/rdf-tests repository.

One single test is marked as an `xfail` in the [test_sparql_test_suite_from_rdf_tests.py](tests/test_sparql_test_suite_from_rdf_tests.py) test due to the limitation of the serializer's implementation. The serializer creates an output string by walking the AST in a recursive manner. In cases where a very large query is provided, this will hit the default Python recursion limit. Future updates to this package may refactor the code to convert its recursive serializer into an interative one.
