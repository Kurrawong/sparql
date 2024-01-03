def test_query_from(test_roundtrip):
    query = """
            # Test to ensure the FROM keyword works with virtual graph query rewriting.

            SELECT DISTINCT ?o
            FROM <urn:graph:virtual:1>
            FROM <urn:graph:virtual:2>
            WHERE {
              ?s a ?o .
            }
    """
    test_roundtrip(query)


def test_query_test_graph(test_roundtrip):
    query = """
        SELECT DISTINCT ?o
        WHERE {
          GRAPH <urn:graph:virtual:1> {
            ?s a ?o .
          }
        }
    """
    test_roundtrip(query)


def test_query_test_graph_union(test_roundtrip):
    query = """
        SELECT DISTINCT ?o ?g
        WHERE {
          {
            GRAPH <urn:graph:virtual:1> {
              ?s a ?o .
            }
          }
          UNION {
            GRAPH <urn:graph:virtual:2> {
              ?s a ?o .
            }
          }
        }
    """
    test_roundtrip(query)


def test_query_test_values(test_roundtrip):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <https://schema.org/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX addr: <https://w3id.org/profile/anz-address/>
        
        SELECT distinct ?g ?s ?class
        WHERE {
          VALUES (?g ?class) {
            (<urn:graph:virtual:1> skos:Concept)
            (<urn:graph:virtual:2> addr:Address)
          }
        
          GRAPH ?g {
            ?s a ?class .
          }
        }
    """
    test_roundtrip(query)
