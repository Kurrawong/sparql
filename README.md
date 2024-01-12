# Python SPARQL

This package provides parsers and serializers for the [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/).

Note: This is not a SPARQL processing engine.

## Install

Replace `<version>` with the latest GitHub release.

```shell
pip install https://github.com/Kurrawong/sparql/archive/refs/tags/<version>.zip
```

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

## Convenience Functions

### Function `sparql.format_string`

For a given SPARQL query string, return a formatted SPARQL query string. This function by default will perform a guess on whether to use a SPARQL 1.1 parser or SPARQL 1.1 Update parser. Otherwise, a specific parser can be specified as a second argument.

```python
import sparql

result = sparql.format_string(
    """
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
)

assert result

result = sparql.format_string(
    """
    LOAD <http://example.org/faraway> INTO GRAPH <localCopy>
"""
)

assert result
```

## Conformance

The parser and serializer is passing all positive tests found online, examples from the specification, and also the tests from the https://github.com/w3c/rdf-tests repository.

One single test is marked as an `xfail` in the [test_sparql_test_suite_from_rdf_tests.py](tests/test_sparql_test_suite_from_rdf_tests.py) test due to the limitation of the serializer's implementation. The serializer creates an output string by walking the AST in a recursive manner. In cases where a very large query is provided, this will hit the default Python recursion limit. Future updates to this package may refactor the code to convert its recursive serializer into an interative one.
