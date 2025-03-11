# 2_Step2_subGraph Assembly From Ontology.py
#!/usr/bin/env python3
"""
This script loads an OWL ontology (in Turtle format) from a file,
then extracts a “connected subgraph” based on a set of given classes and properties.

Extraction rules:
  - For an ObjectProperty: if at least one given class appears in its domain AND
    at least one given class appears in its range, then include that property and the matching classes.
  - For a DataProperty: if at least one given class appears in its domain, then include that property,
    the matching domain classes, and add `rdfs:Literal`.
    
The code handles owl:unionOf and owl:intersectionOf constructs and ignores any branch using `owl:complementOf`.
"""

from rdflib import Graph, URIRef, BNode, RDF, RDFS, OWL
import rdflib

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
    given_classes = {"bf:MovingImage", "bf:MusicInstrument", "bf:Work", "cidoc-crm:E55_Type", "ctm:ChineseInstrument", "ctm:MusicType", "ctm:OrientalMusicalInstrument", "ctm:SpecialIndependentResource", "ctm:Video-InterviewOrFieldTrip", "dbpedia-owl:EthnicGroup", "mo:Instrument", "ns1:b8784457", "rdfs:Literal"}
    # --corresponding to Transformed ClassList

    # 3. Provide the given properties.
    # For test case (*), for example, use:
    given_properties = {"ctm:musicSystem", "ctm:nameOfMusicTypeOrInstrument", "ctm:relatesEthnicGroup", "ctm:relatesInstrument", "ctm:relatesMusicType", "dbo:formerName"}
    # --corresponding to Transformed PropertyList

    # =====================================================
    # End of user configuration.
    # =====================================================
    
    owl_file_path, extracted_classes, extracted_properties = extract_connected_subgraph_from_owl(
        owl_file_path, given_classes, given_properties
    )
    
    # print("Extracted Classes:")
    for c in sorted(extracted_classes):
        print("  ", c)
    # print("Extracted Properties:")
    for p in sorted(extracted_properties):
        print("  ", p)
    return owl_file_path, extracted_classes, extracted_properties

def retrieve_specific_subset(owl_file_path, extracted_classes, extracted_properties):
    import rdflib
    from rdflib import URIRef, BNode

    g = rdflib.Graph()
    g.parse(owl_file_path, format='ttl')

    # Convert classes and properties to URI refs if possible
    seeds = []
    for item in set(extracted_classes).union(extracted_properties):
        if item.startswith('http'):
            seeds.append(URIRef(item))

    visited = set()
    queue = list(seeds)
    subset_triples = []

    # BFS to include blank node details
    while queue:
        current = queue.pop(0)
        if current not in visited:
            visited.add(current)
            for s, p, o in g.triples((current, None, None)):
                subset_triples.append((s, p, o))
                if isinstance(o, BNode):
                    queue.append(o)

    return subset_triples


if __name__ == '__main__':
    owl_file_path, extracted_classes, extracted_properties = main()
    # owl_file_path = "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl"
    triple_subset = retrieve_specific_subset(
        owl_file_path, extracted_classes, extracted_properties
    )
        # Create a new rdflib Graph for the subgraph.
    subgraph = rdflib.Graph()
    for triple in triple_subset:
        subgraph.add(triple)
    
    # Parse the original ontology to bind all namespace prefixes.
    original = rdflib.Graph()
    original.parse(owl_file_path, format='ttl')
    for prefix, namespace in original.namespaces():
        subgraph.bind(prefix, namespace)
    
    # Serialize the subgraph in Turtle format.
    turtle_output = subgraph.serialize(format='turtle')
    print("\n\nAssembled Ontology as a Subgraph in Turtle format:")
    print("\n\n", turtle_output)

    # Write the Turtle output to a file
    with open("assembledSubgraphOfOntology.ttl", "w") as f:
        f.write(turtle_output) # turtle_output is the assembled ontology subgraph in Turtle format


# 3_Step3_SPARQL generation.py
from openai import OpenAI
# Invoke the OpenAI API:
client = OpenAI(
    api_key="LHAV5AoeevPPQ2iZKCIwCg2i9Jm5axE9mL5cJf0L71p6Iosl",
    base_url="https://oneapi.xty.app/v1"
)
def callGPT(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o", # We can use "gpt-4o" or "o1-preview" or "claude-3-7-sonnet-20250219" model
        max_tokens=4096,
        temperature=0.1,
        messages=[
            {"role": "user", "content": "You are an expert in converting natural language question to SPARQL in context of music metadata or ontology."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

with open("sampleQuestions/question_SpecialIndependentResource_MusicType,Instrument,EthnicGroup.txt", 'r') as f:
    question = f.readlines()


# Generate SPARQL query from the ontology subgraph:
prompt6 = f"""
Given the natural language question: {question} 

, and the related ontology snippet: {turtle_output}

--please generate a SPARQL query for the question.
Do return only the SPARQL query code. Don't add any extra text before or after the SPARQL query code.

Note: 
(1) Don't use language tag for the rdfs:Literals value in the SPARQL query
(2) The question is associated with the domain of Chinese or East-and-Southeast-Asian music, so you may understand the entities priorly that you can correspond them to the classes in the given ontology
(3) Usually, for each instance variable in the SPARQL, involve `rdfs:label` with the variable

!!!Caution again: Do return only the SPARQL query code. Don't add any additional text in your return. (Any non-comment text outside the query will cause a syntax error when executed in a SPARQL endpoint.)
"""

sparql_query = callGPT(prompt6).strip().replace("```sparql", "").strip("```")
# print("Type of the SPARQL query:", type(sparql_query)) # <class 'str'>
print('\n\nThe sparql_query based on the ontology subgraph:\n', sparql_query)


# Verify the generated SPARQL query, still based on the ontology subgraph:
prompt6_verification = f"""
Examine the following SPARQL query to ensure its syntax is correct. Then, cross-check it against the natural language question and the ontology snippet for consistency and accuracy. 
Refine it if necessary.

SPARQL query:
{sparql_query}

Ontology snippet:
{turtle_output}

Natural language question:
{question}

!Caution: in your feedback for this prompt, do return only the refined SPARQL query code.

Note: 
1. Don't use language tag for the rdfs:Literals value in the SPARQL query
2. The question is associated with the domain of Chinese or East-and-Southeast-Asian music, so you may understand the entities priorly that you can correspond them to the classes in the given ontology
3. For each instance variable in the SPARQL, ensure that the labels for them are represented using `rdfs:label` property even if it is not explicitly mentioned in the ontology snippet
4. After examination and cross-checking, if modifications are required, do return only the modified SPARQL query without any additional text
5. De ensure the SPARQL query's logic is inherently consistent with the natural language question and the ontology snippet
6. Don't forget the clarification of namespaces in the SPARQL query; Delete the needless prefixes clarification (which are not used in the query)
7. If you are uncertain about precision of specific classes or properties, you can broaden the retrieval scope using techniques such as: 
    7.1 The UNION keyword: to include multiple options to interpretate a question, especially when the question can be divided into multiple sub-questions, or in case of handling an objectProperty and a dataProperty which have the similar semantic meanings
    7.2 The | operator to represent a logical OR for properties
    7.3 The OPTIONAL keyword: 
        7.2.1 also useful when handling an objectProperty and a dataProperty which have the similar semantic meaning, etc.
        7.2.2 to allow partial matches, ensuring that queries remain valid even when certain properties or property values are missing. It is particularly beneficial for handling uncertain or "if, possibly" relationships (e.g., "Something may relate to something else") or when managing properties with similar semantics
        
!!!Caution: for this prompt, do return only the refined SPARQL query code. Don't add any extra text before or after the SPARQL query code. However, you may include comments preceded `#` symbol to explain the logic, enhancing user's understanding (these comments with `#` symbol will be ignored by the SPARQL endpoint)
"""

sparql_query = callGPT(prompt6_verification).strip().replace("```sparql", "define input:inference 'urn:owl.ccmusicrules0214'").strip("```") # Activate the OWL-based inference mechanism

# With this more robust coding, we can ensure that the SPARQL query is clearly stripped of any leading or trailing disturbances:
response = callGPT(prompt6_verification).strip()
import re
# First, completely remove all markdown code block markers
clean_response = re.sub(r'```(?:sparql)?', '', response)
clean_response = clean_response.strip()
# Second, check if the response starts with PREFIX, if not, remove everything before SELECT
prefix_index = clean_response.find("PREFIX")
if prefix_index != -1:
    clean_response = clean_response[prefix_index:]
else:
    # If PREFIX is not found, try to find SELECT
    select_index = clean_response.find("SELECT")
    if select_index != -1:
        clean_response = clean_response[select_index:]
# Third, add the inference directive at the beginning
sparql_query = "define input:inference 'urn:owl.ccmusicrules0214'\n" + clean_response # The type of sparql_query is <class 'str'>

print('\n\nThe sparql_query based on the ontology subgraph (verified):\n' + sparql_query)

from SPARQLWrapper import SPARQLWrapper, JSON

# Define a function to query the SPARQL endpoint. The 1st parameter is the SPARQL endpoint, the 2nd parameter is the SPARQL query, and the 3rd parameter is the graph IRI:
def query_sparql(endpoint, sparql_query_parameter, graph_iri_parameter):
    sparql = SPARQLWrapper(endpoint) # SPARQLWrapper is a Python wrapper around a SPARQL service; is also a library for executing SPARQL queries on an RDF endpoint and retrieving the results
    sparql.setQuery(sparql_query_parameter) # This initializes the query to be sent to the SPARQL endpoint using the string provided in `sparql_query_parameter`
    sparql.setReturnFormat(JSON) # This sets the return format of the query to JSON
    if graph_iri: # If a graph IRI is provided, it is added as a parameter to the SPARQL query
        sparql.addParameter("default-graph-uri", graph_iri_parameter) # This adds a parameter to the SPARQL query
    results = sparql.query().convert() # This executes the query and converts the results into JSON format
    return results

# Query the SPARQL endpoint:
sparql_endpoint = "http://www.usources.cn:8891/sparql" # We can also use the endpoint "https://virtuoso.staging.simssa.ca/sparql"
graph_iri = "https://lib.ccmusic.edu.cn/graph/music" # We can also use the graph IRI "http://ChineseTraditionalMusicCultureKnowledgeBase"
sparql_results = query_sparql(sparql_endpoint, sparql_query, graph_iri)
print('\n\nsparql_results:', sparql_results) # rendered in JSON format


# Retrieval Augmented Generation (RAG): 
prompt7 = f"""
Based on a natural language question: {question},

and the related ontology snippet: {turtle_output}, 

and the subsequent SPARQL query: {sparql_query}, 

we retrieved the result from visiting the SPARQL Endpoint: {sparql_results}. 

1. Explain the query result based on the question, the ontology snippet, and the SPARQL query.
2. If the result is too large, you can conduct a statistical analysis with a summary.
3. Compare the result with your own knowledge about the domain. Find out whether there is any inconsistency or inadquacy in the result. Contrast then enrich the explaination.

4. Last but not least, if the result is too small or even empty, 
please "broaden the retrieval scope" by loosening (defined) constraints in the SPARQL query or recommend other possible query patterns
"""


RAG_result = callGPT(prompt7)
print('\n\nRAG_result:', RAG_result)



# Other tips for RAG: For the retrieved results from the SPARQL visiting the Endpoint, please
    # Access the accessible URI and provide a brief summary



# 其他灵感：
# 依然准备一个样本库，包含了各种问题及相应的SPARQL
# 如果在prompt6_verification基础上生成的SPARQL，其通过 Endpoint无法返回结果（或报错），那么，我们可以：
# （1）根据它生成的SPARQL所反映的本体结构、SPARQL语句中的关键词、特殊函数等，通过相似度匹配样本库中的SPARQL
# （2）同时根据自然语言问题的Edit distance (Levenshtein distance)匹配样本库中相似的问题
# （3）对(1)(2)做一个折中，即选定一个最合适的 example（NLQ+SPARQL），再用这个新的 context 训练 LLMs，以重新生成 SPARQL
