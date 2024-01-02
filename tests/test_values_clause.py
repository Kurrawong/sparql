from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer


def test_values_clause_single_var():
    # This also tests that the ignores characters combined with comments work.
    query = """
        # VALUES ?g {
        #     <urn:graph:1>
        #     <urn:graph:2>
        # }
    
        VALUES ?z { "abc" <urn:graph:1> }
    """

    tree = sparql_parser.parse(query)

    sparql_serializer = SparqlSerializer()
    sparql_serializer.visit_topdown(tree)

    new_tree = sparql_parser.parse(sparql_serializer.result)
    assert tree == new_tree, sparql_serializer.result


def test_values_clause_multiple_vars():
    # Also test base namespace and prefix declaration with different value types.
    # Test multi-line string
    query = """
        BASE <https://example.com/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        VALUES (?g ?s) {
            (<urn:graph:1> <urn:entity:1>)
            (<urn:graph:2> "some literal"@en)
            (<urn:graph:3> UNDEF)
            (<urn:graph:4> 123)
            (<urn:graph:5> true)
            (<urn:graph:6> false)
            (<urn:graph:7> "special token"^^xsd:token)
            (<urn:graph:8> '''some multi-line literal
blah'''@en)
        }
    """

    tree = sparql_parser.parse(query)

    sparql_serializer = SparqlSerializer()
    sparql_serializer.visit_topdown(tree)

    new_tree = sparql_parser.parse(sparql_serializer.result)
    assert tree == new_tree, sparql_serializer.result


def test_values_clause_lowercase_keywords():
    query = """
        base <https://example.com/>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        
        values (?g ?s) {
            (<urn:graph:1> <urn:entity:1>)
            (<urn:graph:2> "some literal"@en)
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

    new_tree = sparql_parser.parse(sparql_serializer.result)
    assert tree == new_tree, sparql_serializer.result
