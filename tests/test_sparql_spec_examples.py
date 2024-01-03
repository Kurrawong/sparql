def test_2_1_writing_a_simple_query(test_roundtrip):
    query = """
        SELECT ?title
        WHERE
        {
          <http://example.org/book/book1> <http://purl.org/dc/elements/1.1/title> ?title .
        }
    """
    test_roundtrip(query)


def test_2_2_multiple_matches(test_roundtrip):
    query = """
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?mbox
        WHERE
          { ?x foaf:name ?name .
            ?x foaf:mbox ?mbox }
    """
    test_roundtrip(query)


def test_2_3_1_matching_literals(test_roundtrip):
    query = """
        SELECT ?v WHERE { ?v ?p "cat" }
    """
    test_roundtrip(query)


def test_2_3_1_matching_literals_with_lang_tag(test_roundtrip):
    query = """
        SELECT ?v WHERE { ?v ?p "cat"@en }
    """
    test_roundtrip(query)


def test_2_3_2_matching_literals_with_numeric_types(test_roundtrip):
    query = """
        SELECT ?v WHERE { ?v ?p 42 }
    """
    test_roundtrip(query)


def test_2_3_3_matching_literals_with_arbitrary_datatypes(test_roundtrip):
    query = """
        SELECT ?v WHERE { ?v ?p "abc"^^<http://example.org/datatype#specialDatatype> }
    """
    test_roundtrip(query)


def test_2_4_blank_node_labels(test_roundtrip):
    query = """
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        SELECT ?x ?name
        WHERE  { ?x foaf:name ?name }
    """
    test_roundtrip(query)


def test_2_5_creating_values_with_expressions(test_roundtrip):
    query = """
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        SELECT ( CONCAT(?G, " ", ?S) AS ?name )
        WHERE  { ?P foaf:givenName ?G ; foaf:surname ?S }
    """
    test_roundtrip(query)


def test_2_5_creating_values_with_expressions_2(test_roundtrip):
    query = """
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        SELECT ?name
        WHERE  { 
           ?P foaf:givenName ?G ; 
              foaf:surname ?S 
           BIND(CONCAT(?G, " ", ?S) AS ?name)
        }
    """
    test_roundtrip(query)


def test_2_6_building_rdf_graphs(test_roundtrip):
    query = """
        PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
        PREFIX org:    <http://example.com/ns#>
        
        CONSTRUCT { ?x foaf:name ?name }
        WHERE  { ?x org:employeeName ?name }
    """
    test_roundtrip(query)


def test_17_4_2_5_str(test_roundtrip):
    query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT ?name ?mbox
         WHERE { ?x foaf:name  ?name ;
                    foaf:mbox  ?mbox .
                 FILTER regex(str(?mbox), "@work\\.example$") }
    """
    test_roundtrip(query)
