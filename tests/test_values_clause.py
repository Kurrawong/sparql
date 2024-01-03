def test_values_clause_single_var(test_roundtrip):
    # This also tests that the ignores characters combined with comments work.
    query = """
        SELECT *
        where {
            # VALUES ?g {
            #     <urn:graph:1>
            #     <urn:graph:2>
            # }
        
            VALUES ?z { "abc" <urn:graph:1> }
        }
    """
    test_roundtrip(query)


def test_values_clause_multiple_vars(test_roundtrip):
    # Also test base namespace and prefix declaration with different value types.
    # Test multi-line string
    query = """
        BASE <https://example.com/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        select * 
        where {
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
        }
    """
    test_roundtrip(query)


def test_values_clause_lowercase_keywords(test_roundtrip):
    query = """
        base <https://example.com/>
        prefix xsd: <http://www.w3.org/2001/XMLSchema#>
        
        select *
        where {
            values (?g ?s) {
                (<urn:graph:1> <urn:entity:1>)
                (<urn:graph:2> "some literal"@en)
                (<urn:graph:3> UNDEF)
                (<urn:graph:4> 123)
                (<urn:graph:5> true)
                (<urn:graph:6> false)
                (<urn:graph:7> "special token"^^xsd:token)
            }
        }
    """
    test_roundtrip(query)
