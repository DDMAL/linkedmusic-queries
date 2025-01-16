from rdflib import Graph

# Create a new RDF Graph
g = Graph()

# Define the SPARQL endpoint and the query
sparql_endpoint = "http://localhost:8890/sparql"
sparql_query = """
PREFIX ex: <http://example/>

CONSTRUCT {
  ?subject ?predicate ?object .
} 
FROM <http://subGraph/connectivity_test>
WHERE {
  VALUES ?subject { ex:class_2 ex:class_3 ex:class_4 ex:class_5 ex:class_6 ex:class_9 }  # Members of set Y
  VALUES ?object { ex:class_2 ex:class_3 ex:class_4 ex:class_5 ex:class_6 ex:class_9 }  # Members of set Y
  ?subject ?predicate ?object .
}"""

# Perform the query
g.parse(sparql_endpoint, format="turtle", query=sparql_query)

# Export the results to a file (Turtle format)
output_file = "subgraph.ttl"
g.serialize(destination=output_file, format='turtle')
print(f"Constructed RDF triples exported to {output_file}")