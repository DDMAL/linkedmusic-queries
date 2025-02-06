#!/usr/bin/env python3
"""
This script loads an OWL ontology (in Turtle format) from a file,
then extracts a “connected subgraph” based on a set of given classes and properties.

Extraction rules:
  - For an ObjectProperty: if at least one given class appears in its domain AND
    at least one given class appears in its range, then include that property and the matching classes.
  - For a DataProperty: if at least one given class appears in its domain, then include that property,
    the matching domain classes, and add rdfs:Literal.
    
The code handles owl:unionOf and owl:intersectionOf constructs and ignores any branch using owl:complementOf.
"""

from rdflib import Graph, URIRef, BNode, RDF, RDFS, OWL

def process_rdf_list(graph, list_node):
    """
    Process an RDF list (used for owl:unionOf or owl:intersectionOf)
    and return a set of class URIs.
    """
    items = set()
    while list_node and list_node != RDF.nil:
        first = graph.value(list_node, RDF.first)
        if first is not None:
            items.update(extract_valid_classes_from_node(graph, first))
        list_node = graph.value(list_node, RDF.rest)
    return items

def extract_valid_classes_from_node(graph, node):
    """
    Recursively extract “positive” class URIs from a class expression node.
    
    - If the node is a URIRef, it is a class.
    - If the node is a BNode with owl:unionOf or owl:intersectionOf, process its RDF list.
    - Any branch with owl:complementOf is ignored.
    """
    valid = set()
    if isinstance(node, URIRef):
        valid.add(str(node))
    elif isinstance(node, BNode):
        # Process owl:unionOf
        for union in graph.objects(node, OWL.unionOf):
            valid.update(process_rdf_list(graph, union))
        # Process owl:intersectionOf
        for inter in graph.objects(node, OWL.intersectionOf):
            valid.update(process_rdf_list(graph, inter))
        # Do not add anything for owl:complementOf branches.
    return valid

def get_property_type(graph, prop):
    """
    Determine the property type by first checking its explicit rdf:type values.
    If none of those indicate owl:DatatypeProperty or owl:ObjectProperty,
    then infer a data property if its range is (or ends with) "Literal".
    
    Returns:
      - "data" for a DatatypeProperty,
      - "object" for an ObjectProperty,
      - None if the type cannot be determined.
    """
    # Try explicit rdf:type declarations.
    types = set(graph.objects(prop, RDF.type))
    if OWL.DatatypeProperty in types:
        return "data"
    if OWL.ObjectProperty in types:
        return "object"
    
    # Otherwise, infer type by examining the rdfs:range.
    range_nodes = list(graph.objects(prop, RDFS.range))
    for r in range_nodes:
        # If the range is explicitly rdfs:Literal or its URI ends with "Literal", assume a data property.
        if r == RDFS.Literal or str(r).endswith("Literal"):
            return "data"
    return None

def resolve_curie(graph, curie):
    """
    Resolve a CURIE (e.g., "ctm:MusicType") to a full URI using the graph's namespace manager.
    If no colon is found, assume the input is already a full URI.
    """
    if ":" in curie:
        prefix, local = curie.split(":", 1)
        for ns_prefix, ns_uri in graph.namespace_manager.namespaces():
            if ns_prefix == prefix:
                return URIRef(ns_uri + local)
    return URIRef(curie)

def extract_connected_subgraph_from_owl(owl_file_path, given_classes, given_properties):
    """
    Load the OWL ontology from the specified file (in Turtle format) then extract and return
    the subgraph that meets the criteria.
    
    Parameters:
      - owl_file_path: Full path to the ontology file.
      - given_classes: A set of class names (in CURIE or full URI form).
      - given_properties: A set of property names (in CURIE or full URI form).
    
    Returns:
      A tuple (extracted_classes, extracted_properties) where each is a set of strings.
    """
    graph = Graph()
    # Parse the ontology file (format is Turtle).
    graph.parse(owl_file_path, format="turtle")
    
    # Resolve the given classes and properties to full URIs.
    given_classes_resolved = set()
    for c in given_classes:
        uri = resolve_curie(graph, c)
        given_classes_resolved.add(str(uri))
    given_properties_resolved = set()
    for p in given_properties:
        uri = resolve_curie(graph, p)
        given_properties_resolved.add(str(uri))
    
    extracted_properties = set()
    extracted_classes = set()
    
    # Process each given property.
    for prop_str in given_properties_resolved:
        prop = URIRef(prop_str)
        ptype = get_property_type(graph, prop)
        if ptype is None:
            continue  # Skip if the type cannot be determined.
    
        # Process rdfs:domain.
        domain_nodes = list(graph.objects(prop, RDFS.domain))
        domain_valid = set()
        for d in domain_nodes:
            if isinstance(d, URIRef):
                domain_valid.add(str(d))
            else:
                domain_valid.update(extract_valid_classes_from_node(graph, d))
                
        if ptype == "object":
            # Process rdfs:range for ObjectProperties.
            range_nodes = list(graph.objects(prop, RDFS.range))
            range_valid = set()
            for r in range_nodes:
                if isinstance(r, URIRef):
                    range_valid.add(str(r))
                else:
                    range_valid.update(extract_valid_classes_from_node(graph, r))
            # For an ObjectProperty, require at least one matching class in both domain and range.
            if (domain_valid & given_classes_resolved) and (range_valid & given_classes_resolved):
                extracted_properties.add(prop_str)
                extracted_classes.update(domain_valid & given_classes_resolved)
                extracted_classes.update(range_valid & given_classes_resolved)
        elif ptype == "data":
            # For a DataProperty, if at least one given class is in its domain,
            # include that property and add matching domain classes plus "rdfs:Literal".
            if domain_valid & given_classes_resolved:
                extracted_properties.add(prop_str)
                extracted_classes.update(domain_valid & given_classes_resolved)
                extracted_classes.add("rdfs:Literal")
    
    return owl_file_path, extracted_classes, extracted_properties

def main():
    # =====================================================
    # FILL IN THE FOLLOWING VARIABLES WITH YOUR OWN VALUES
    # =====================================================
    
    # 1. Provide the full path (and file name) of your ontology file (in Turtle format).
    owl_file_path = "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl"  # e.g., "C:/ontologies/myontology.ttl"
    
    # 2. Provide the given classes.
    # For test case (*), for example, use:
    given_classes = {"ctm:PieceWithPerformance", "mo:Instrument"}
    
    # 3. Provide the given properties.
    # For test case (*), for example, use:
    given_properties = {"ctm:piecePrincipalInstrument", "ctm:pieceType"}
    
    # =====================================================
    # End of user configuration.
    # =====================================================
    
    owl_file_path, extracted_classes, extracted_properties = extract_connected_subgraph_from_owl(
        owl_file_path, given_classes, given_properties
    )
    
    print("Extracted Classes:")
    for c in sorted(extracted_classes):
        print("  ", c)
    print("Extracted Properties:")
    for p in sorted(extracted_properties):
        print("  ", p)
    return owl_file_path, extracted_classes, extracted_properties

if __name__ == '__main__':
    owl_file_path, extracted_classes, extracted_properties = main()
