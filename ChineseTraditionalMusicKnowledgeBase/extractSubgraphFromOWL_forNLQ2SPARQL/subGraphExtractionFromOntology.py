from rdflib import Graph, URIRef, RDF, RDFS, OWL

def extract_connected_subgraph(ontology_file, classes, properties):
    # Load the ontology into an RDF graph
    g = Graph()
    g.parse(ontology_file, format="turtle")

    extracted_classes = set()
    extracted_properties = set()

    classes_uris = {URIRef(cls) for cls in classes}
    properties_uris = {URIRef(prop) for prop in properties}

    # Helper functions to process complex domain/range cases
    def is_union(node):
        return (node, RDF.type, OWL.Class) in g and (node, OWL.unionOf, None) in g

    def is_intersection(node):
        return (node, RDF.type, OWL.Class) in g and (node, OWL.intersectionOf, None) in g

    def is_complement(node):
        return (node, RDF.type, OWL.Class) in g and (node, OWL.complementOf, None) in g

    def get_union_classes(node):
        union_list = g.value(node, OWL.unionOf)
        return {item for item in g.items(union_list)} if union_list else set()

    def get_intersection_classes(node):
        intersection_list = g.value(node, OWL.intersectionOf)
        return {item for item in g.items(intersection_list)} if intersection_list else set()

    def get_complement_class(node):
        return g.value(node, OWL.complementOf)

    # Iterate through all ObjectProperties and DataProperties in the ontology
    for prop in g.subjects(RDF.type, OWL.ObjectProperty) | g.subjects(RDF.type, OWL.DatatypeProperty):
        if prop not in properties_uris:
            continue

        domain = g.value(prop, RDFS.domain)
        range_ = g.value(prop, RDFS.range)

        # Resolve union, intersection, or complement in domain
        domain_classes = set()
        if is_union(domain):
            domain_classes |= get_union_classes(domain)
        elif is_intersection(domain):
            domain_classes |= get_intersection_classes(domain)
        elif is_complement(domain):
            complement_class = get_complement_class(domain)
            domain_classes -= {complement_class}
        else:
            domain_classes.add(domain)

        # Resolve union, intersection, or complement in range
        range_classes = set()
        if range_:
            if is_union(range_):
                range_classes |= get_union_classes(range_)
            elif is_intersection(range_):
                range_classes |= get_intersection_classes(range_)
            elif is_complement(range_):
                complement_class = get_complement_class(range_)
                range_classes -= {complement_class}
            else:
                range_classes.add(range_)

        # Check if any given class appears in domain/range
        if classes_uris & domain_classes or classes_uris & range_classes:
            extracted_properties.add(prop)
            extracted_classes |= domain_classes
            extracted_classes |= range_classes

    # Add rdfs:Literal for DataProperties
    for prop in g.subjects(RDF.type, OWL.DatatypeProperty):
        if prop in extracted_properties:
            extracted_classes.add(RDFS.Literal)

    # Filter out None values from the results
    extracted_classes = {cls for cls in extracted_classes if cls is not None}

    return extracted_classes, extracted_properties

# Example usage
ontology_file = "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/subgraphConnectivityTest_ontology.ttl"  # Path to the ontology file
classes = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#MusicType", "http://id.loc.gov/ontologies/bibframe/MusicInstrument"]
properties = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p11"]

extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("Extracted Classes:", extracted_classes)
print("Extracted Properties:", extracted_properties)
