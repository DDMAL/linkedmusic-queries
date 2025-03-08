from rdflib import Graph, Namespace, RDF, RDFS

# Load the TTL file
g = Graph()
g.parse("/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/extractSubgraphFromOWL_forNLQ2SPARQL/ontologySnippet_dataProperties.ttl", format="ttl")

# Define namespaces
bf = Namespace("http://id.loc.gov/ontologies/bibframe/")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")

# Create a new graph to store the filtered triples
filtered_graph = Graph()

# Add namespace prefixes to the new graph
for prefix, namespace in g.namespaces():
    filtered_graph.bind(prefix, namespace)

# Filter triples
for s, p, o in g:
    if p in [RDFS.label, RDFS.comment]:
        filtered_graph.add((s, p, o))

# Serialize the filtered graph to a TTL file
filtered_graph.serialize(destination="/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/extractSubgraphFromOWL_forNLQ2SPARQL/ontologySnippet_dataProperties_simplified.ttl", format="ttl")