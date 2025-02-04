from rdflib import Graph, URIRef, RDF, RDFS, OWL, BNode
import itertools

def extract_connected_subgraph(ontology, classes, properties):
    g = Graph()
    g.parse(ontology, format='ttl')

    classes_uris = set(URIRef(cls) for cls in classes)
    properties_uris = set(URIRef(prop) for prop in properties)

    extracted_classes = set()
    extracted_properties = set()

    for prop in itertools.chain(g.subjects(RDF.type, OWL.ObjectProperty), g.subjects(RDF.type, OWL.DatatypeProperty)):
        if prop not in properties_uris:
            continue

        domain_classes = set()
        range_classes = set()

        for domain in g.objects(prop, RDFS.domain):
            if isinstance(domain, BNode):
                for cls in g.objects(domain, OWL.unionOf):
                    domain_classes.update(g.items(cls))
                for cls in g.objects(domain, OWL.intersectionOf):
                    domain_classes.update(g.items(cls))
                for cls in g.objects(domain, OWL.complementOf):
                    domain_classes.discard(cls)
            else:
                domain_classes.add(domain)

        for range_ in g.objects(prop, RDFS.range):
            if isinstance(range_, BNode):
                for cls in g.objects(range_, OWL.unionOf):
                    range_classes.update(g.items(cls))
                for cls in g.objects(range_, OWL.intersectionOf):
                    range_classes.update(g.items(cls))
                for cls in g.objects(range_, OWL.complementOf):
                    range_classes.discard(cls)
            else:
                range_classes.add(range_)

        if (classes_uris & domain_classes) and (classes_uris & range_classes):
            extracted_properties.add(prop)
            extracted_classes |= domain_classes
            extracted_classes |= range_classes

    for prop in g.subjects(RDF.type, OWL.DatatypeProperty):
        if prop in extracted_properties:
            extracted_classes.add(RDFS.Literal)

    extracted_classes = {cls for cls in extracted_classes if cls is not None}

    return extracted_classes, extracted_properties

# Example usage
ontology_file = "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/subgraphConnectivityTest_ontology.ttl"

# Test case 1 # corresponding to (4) in the original prompt
classes = ["http://id.loc.gov/ontologies/bibframe/Place", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C2", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C3"]
properties = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p2", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p4", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p5"]
extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("(4)Extracted Classes:", extracted_classes)
print("(4)Extracted Properties:", extracted_properties)

# Test case 2
classes = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C2", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C3"]
properties = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p3", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p4", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p6"]
extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("(5)Extracted Classes:", extracted_classes)
print("(5)Extracted Properties:", extracted_properties)

# Test case 3
classes = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#MusicType", "http://id.loc.gov/ontologies/bibframe/Place", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C"]
properties = ["http://id.loc.gov/ontologies/bibframe/place"]
extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("(6)Extracted Classes:", extracted_classes)
print("(6)Extracted Properties:", extracted_properties)

# Test case 4
classes = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C4", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C10"]
properties = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p10"]
extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("(7)Extracted Classes:", extracted_classes)
print("(7)Extracted Properties:", extracted_properties)

# Test case 5
classes = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C2", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C6", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C7", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C3"]
properties = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p0"]
extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("(8)Extracted Classes:", extracted_classes)
print("(8)Extracted Properties:", extracted_properties)

# Test case 6
classes = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C5", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C10", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C4"]
properties = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p8"]
extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("(9)Extracted Classes:", extracted_classes)
print("(9)Extracted Properties:", extracted_properties)

# Test case 7
classes = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C8", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C2", "https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#C3"]
properties = ["https://lib.ccmusic.edu.cn/ontologies/chinese_traditional_music#p9"]
extracted_classes, extracted_properties = extract_connected_subgraph(ontology_file, classes, properties)
print("(10)Extracted Classes:", extracted_classes)
print("(10)Extracted Properties:", extracted_properties)