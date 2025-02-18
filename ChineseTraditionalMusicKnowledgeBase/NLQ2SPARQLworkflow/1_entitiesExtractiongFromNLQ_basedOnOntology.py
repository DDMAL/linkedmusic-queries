# Note: to activate virtual enviroment for python, please exectue `source /directory/of/your/virtual/environment/folder/bin/activate`, e.g., `source /Users/caojunjun/venv_extractSubgraphForLLMsGeneratingSPARQL/bin/activate`
import json
# import pandas as pd 
from openai import OpenAI
from SPARQLWrapper import SPARQLWrapper, JSON # SPARQLWrapper is a Python wrapper around a SPARQL service; is also a library for executing SPARQL queries on an RDF endpoint and retrieving the results.


# 1. SubGraph Extraction
# Invoke the OpenAI API:
client = OpenAI(
    api_key="",
    base_url="https://oneapi.xty.app/v1"
)

def callGPT(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=4096,
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are an expert in SPARQL in terms of music metadata or ontology."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


# Read the context and question from the file:
# The classes ontology snippets are divided into two parts to avoid exceeding the token limit of the OpenAI API:
with open("ontologySnippet_classes1_simplified.ttl", "r") as context1: 
    context_ontology_class1 = context1.readlines()
with open("ontologySnippet_classes2_simplified.ttl", "r") as context2: 
    context_ontology_class2 = context2.readlines()
# The object and data properties ontology snippets are read separately:
with open("ontologySnippet_objectProperties_simplified.ttl", "r") as context3: 
    context_ontology_objectProperty = context3.readlines()
with open("ontologySnippet_dataProperties_simplified.ttl", "r") as context4:
    context_ontology_dataProperty = context4.readlines()
# The natural language question is read from a text file:
with open("sampleQuestions/question_MusicType_SpecialIndependentResource_Place.txt", 'r') as f:
    question = f.readlines()

# Identify and extract the relevant classes and properties from the given natural language question. Match them with the corresponding entities (classes or properties) defined in the provided ontology and present the results exclusively in a list format.
prompt1 = f"""
### Task:
According to the given natural language question, extract relevant classes from the provided ontology and output them only in a json-formatted list (no adding redundant strings).
such as `["ex:class1", "ex:class2", "ex:class3"]`.
### Ontology:
{context_ontology_class1}
### Given the Natural Language Question:
{question}
### Instructions and Notes:
1. Retrieve classes from the ontology as long as any literals in the natural language question match the semantic content of their rdfs:label or rdfs:comment.
2. Ensure each retrieved class is represented by its namespace prefix defined in the ontology.
3. Extract all classes that are even minimally relevant to the question.
4. As long as any semantic fragment (such as a word, phrase, or expression) in the natural language question semantically matches the content of the `rdfs:label` of a class in the ontology, that class will be extracted from the ontology.
"""

prompt2 = f"""
### Task:
According to the given natural language question, extract relevant classes from the provided ontology and output them only in a json-formatted list (no adding redundant strings).
such as `["ex:class1", "ex:class2", "ex:class3"]`.
### Ontology:
{context_ontology_class2}
### Given the Natural Language Question:
{question}
### Instructions and Notes:
1. Retrieve classes from the ontology as long as any literals in the natural language question match the semantic content of their rdfs:label or rdfs:comment.
2. Ensure each retrieved class is represented by its namespace prefix defined in the ontology.
3. Extract all classes that are even minimally relevant to the question.
4. As long as any semantic fragment (such as a word, phrase, or expression) in the natural language question semantically matches the content of the `rdfs:label` of a class in the ontology, that class will be extracted from the ontology.
"""

prompt3 = f"""
### Task:
According to the given natural language question, extract relevant properties from the provided ontology and output them only in a json-formatted list (no adding redundant strings).
such as `["ex:property1", "ex:property2", "ex:property3"]`.
### Ontology:
{context_ontology_objectProperty}
### Given the Natural Language Question:
{question}
### Instructions and Notes:
1. Retrieve properties from the ontology as long as any literals in the natural language question match the semantic content of their rdfs:label or rdfs:comment.
2. Analyze the semantic structure of the natural language question carefully to identify all relevant properties.
3. Ensure each retrieved property is represented by its namespace prefix defined in the ontology.
4. Extract all properties that are even minimally relevant to the question.
5. Examine each property with its label and comment, one by one.
"""

prompt4 = f"""
### Task:
According to the given natural language question, extract relevant properties from the provided ontology and output them only in a json-formatted list (no adding redundant strings).
such as `["ex:property1", "ex:property2", "ex:property3"]`.
### Ontology:
{context_ontology_dataProperty}
### Given the Natural Language Question:
{question}
### Instructions and Notes:
1. Retrieve properties from the ontology as long as any literals in the natural language question match the semantic content of their rdfs:label or rdfs:comment.
2. Analyze the semantic structure of the natural language question carefully to identify all relevant properties.
3. Ensure each retrieved property is represented by its namespace prefix defined in the ontology.
4. Extract all properties that are even minimally relevant to the question.
"""

# Retrieve the classes that are not explicitly stated in the question but are related to the entities extracted from the question.
prompt5 = f"""
Please extract the entities from the natural language question: 
{question}
E.g., 
    (1)if the question is "打溜子会用到什么乐器，这些乐器中，哪些又是桑植县的？", you can extract the entities in this format: `VALUES ?label {"打溜子" "乐器" "桑植县"}`.
    (2)if the entity is in 《》, please prepare 2 versions, with one maintaining the 《》, e.g., `VALUES ?label {"《彩云追月》" "彩云追月"}`.
Please embed the extracted entities in a SPARQL query to retrieve the classes of the entities, e.g.:
```
define input:inference 'urn:owl.ccmusicrules'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select ?class where {{
    ?entity rdfs:label ?label ;
            rdf:type ?class .
    VALUES ?label {{"打溜子" "乐器" "桑植县"}} .
}}
```
As to the extracted entities, please only provide one corresponding SPARQL query without any additional text.
"""


# Generate SPARQL query using GPT:
sparql_query = callGPT(prompt5).strip() # The .strip() method removes any unnecessary whitespace or newlines that might exist at the beginning or end of the string returned by callGPT.
sparql_query = sparql_query.replace("```sparql", "").strip("```") # The .replace() method replaces the "```sparql" string with an empty string, and the .strip("```") method removes the "```" string from the beginning and end of the string returned by callGPT.
print('The 1st round of sparql_query:', sparql_query)

# Define a function to query the SPARQL endpoint. The 1st parameter is the SPARQL endpoint, the 2nd parameter is the SPARQL query, and the 3rd parameter is the graph IRI:
def query_sparql(endpoint, query, graph_iri):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    if graph_iri:
        sparql.addParameter("default-graph-uri", graph_iri)
    results = sparql.query().convert()
    return results

# Query the SPARQL endpoint:
sparql_endpoint = "http://www.usources.cn:8891/sparql" # We can also use the endpoint "https://virtuoso.staging.simssa.ca/sparql"
graph_iri = "https://lib.ccmusic.edu.cn/graph/music" # We can also use the graph IRI "http://ChineseTraditionalMusicCultureKnowledgeBase"
sparql_results = query_sparql(sparql_endpoint, sparql_query, graph_iri)
print('sparql_results:', sparql_results) # rendered in JSON format
# # Save sparql_results to a .json file:
# with open('sparql_results.json', 'w') as json_file:
#     json.dump(sparql_results, json_file, indent=4)


result1 = callGPT(prompt1)
print('result1:', result1)
result2 = callGPT(prompt2)
print('result2:', result2)
result3 = callGPT(prompt3)
print('result3:', result3)
result4 = callGPT(prompt4)
print('result4:', result4)


# Function to parse the result1-4 (to parse the JSON strings into lists):
def parse_result(result):
    print(f"Parsing result: {result}")
    if isinstance(result, str):
        if result.startswith("```json") and result.endswith("```"):
            result = result[7:-3].strip()  # Strip off the "```json" prefix and "```" suffix
        try:
            parsed_result = json.loads(result)
            print(f"Parsed JSON result: {parsed_result}")
            return parsed_result
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {result}")
            return []
    elif isinstance(result, list):
        print(f"Result is already a list: {result}")
        return result
    else:
        print(f"Unexpected result format: {result}")
        return []

# Parse the JSON strings into "lists"
result1_list = parse_result(result1)
result2_list = parse_result(result2)
result3_list = parse_result(result3)
result4_list = parse_result(result4)

# Combine upper results into a single list and remove duplicates
combined_results = list(set(result1_list + result2_list + result3_list + result4_list)) # uses set(...) to remove duplicates before converting back to a list
# Sort items into classes and properties, and arrange them in ascending order
class_list = sorted([item for item in combined_results if item.split(":")[1][0].isupper()]) # `item.split(":")[1][0]`: The code splits the string “item” at the colon, takes the second part ([1]), then retrieves its first character ([0])
property_list = sorted([item for item in combined_results if item.split(":")[1][0].islower()])
# Print the sorted lists
    # print("ClassList =", class_list)
    # print("PropertyList =", property_list)
# Transform the format of ClassList and PropertyList
class_list_str = " ".join(class_list)
property_list_str = " ".join(property_list)


import rdflib  # 1) Import the rdflib library to handle RDF data
from rdflib import URIRef  # 2) We specifically need URIRef to convert strings into URI references

def shorten_uri(uri, graph):
    """Convert a full URI into a prefixed form using the graph's known namespaces."""
    # 3) Turn the URI string into a URIRef object
    uri_ref = URIRef(uri)
    # 4) Use graph.qname(...) to get the prefixed form of the URI (e.g., ctm:Instrument)
    return graph.qname(uri_ref)

def render_classes_with_prefix(sparql_results, class_list_str):
    """Parse the local TTL file to retrieve all namespace prefixes, then convert SPARQL results to prefixed URIs."""
    # 5) Create an empty graph
    g = rdflib.Graph()
    # 6) Parse the local TTL file to load its prefixes and triples
    g.parse(
        "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl",
        format="ttl"
    )
    
    # 2) Process the SPARQL results to get prefixed URIs.
    sparql_classes = []
    for binding in sparql_results['results']['bindings']:
        # Extract the full URI from the SPARQL result.
        class_uri = binding['class']['value']
        # Convert the full URI to its prefixed form.
        short_name = shorten_uri(class_uri, g)
        sparql_classes.append(short_name)
    
    # 3) Process the original class_list_str.
    #    (Since class_list_str is defined as " ".join(class_list), we split it using space.)
    original_classes = class_list_str.split()
    
    # 4) Merge both lists and remove duplicates.
    merged_set = set(sparql_classes) | set(original_classes)
    # Optionally, sort the merged list (if desired).
    merged_list = sorted(merged_set)
    
    # 5) Build the final merged string.
    merged = " ".join(merged_list) + " rdfs:Literal"
    
    # 6) Print and return the merged result.
    print("Transformed ClassList =", "{" + ", ".join(f'"{item}"' for item in merged.split()) + "}")
    return merged

# Later in your code, call the function, for example:
merged_class_list = render_classes_with_prefix(sparql_results, class_list_str)
print("Transformed PropertyList =", "{" + ", ".join(f'"{item}"' for item in property_list_str.split()) + "}")


# 2. SubGraph Assembly

# According to the ontology snippet graph,...
# prompt = f"""
# Based on the given ontology snippet:
# {ontology_snippet} 
# --Please generate a SPARQL query for the natural language query:
# {question}
# Note: Only use the properties and classes in the ontology snippet.
# """