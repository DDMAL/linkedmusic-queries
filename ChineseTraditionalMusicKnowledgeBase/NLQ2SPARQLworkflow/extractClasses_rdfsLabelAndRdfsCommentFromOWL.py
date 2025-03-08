import rdflib
import csv
from rdflib.namespace import RDF, RDFS, OWL

# Change these file paths as needed
input_ttl = "3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl"
output_csv = "NLQ2SPARQLworkflow/classesList.csv"

# Create RDF graph and parse the Turtle file
g = rdflib.Graph()
g.parse(input_ttl, format="turtle")

# Function to convert a URIRef to its compact prefixed notation if possible
def compact_uri(uri):
    try:
        return g.namespace_manager.qname(uri)
    except Exception:
        return str(uri)

# Prepare rows list with header
rows = [["class", "rdfs:label", "rdfs:comment"]]

# Find all subjects that are of type owl:Class
for s in g.subjects(RDF.type, OWL.Class):
    # Use compact URI
    cls = compact_uri(s)
    
    # Retrieve all labels and comments
    label_values = [str(l) for l in g.objects(s, RDFS.label)]
    comment_values = [str(c) for c in g.objects(s, RDFS.comment)]
    
    # Format each list: for each value, wrap it in quotes even if a single value.
    def format_values(values):
        if values:
            return ';'.join(f'"{v}"' for v in values)
        return ""
    
    labels_formatted = format_values(label_values)
    comments_formatted = format_values(comment_values)
    
    rows.append([cls, labels_formatted, comments_formatted])

# Write CSV file (the header is written without extra quoting)
with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    for row in rows:
        writer.writerow(row)

print(f"CSV output written to: {output_csv}")