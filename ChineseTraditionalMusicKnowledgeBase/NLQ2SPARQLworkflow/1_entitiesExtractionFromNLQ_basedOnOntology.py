# 1_Step1_entities Extraction From NLQ_based On Ontology.py
# Note: to activate virtual enviroment for python, please exectue `source /directory/of/your/virtual/environment/folder/bin/activate`, e.g., `source /Users/caojunjun/venv_extractSubgraphForLLMsGeneratingSPARQL/bin/activate`
# If you want to extact part of the script to a new file, e.g., to extract from the beginning to Line 50, please execute, `head -n 50 1_entitiesExtractiongFromNLQ_basedOnOntology.py > partialScript.py`
import json
from openai import OpenAI
from SPARQLWrapper import SPARQLWrapper, JSON # SPARQLWrapper is a Python wrapper around a SPARQL service; is also a library for executing SPARQL queries on an RDF endpoint and retrieving the results


# 1. SubGraph Extraction
# Invoke the OpenAI API:
client = OpenAI( # We initiatively set the model to "gpt-4o" for the first call so the function name is OpenAI
    api_key="", # To check the consumption of the API key, please visit https://cx.xty.app/#/. Put "sk-" before the API key then query the consumption
    base_url="https://oneapi.xty.app/v1"
)

def callGPT(prompt): # We initiatively set the model to "gpt-4o" for the first call so the function name is callGPT
    completion = client.chat.completions.create(
        model="gpt-4.1-2025-04-14", # We can use "gpt-4o" or "o1-preview" or "deepseek-r1" model (currently, it's not stable using "deepseek-r1" model and by using that, the final output of Transformed PropertyList is empty for unknown reason)
        max_tokens=4096,
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are an expert in extracting classes and properties from natural language questions about Chinese traditional music and mapping them to RDF/OWL ontology elements."},
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
with open("ontologySnippet_objectProperties1_simplified.ttl", "r") as context3: 
    context_ontology_objectProperty3 = context3.readlines()
with open("ontologySnippet_objectProperties2_simplified.ttl", "r") as context4: 
    context_ontology_objectProperty4 = context4.readlines() # The `+=` operator appends the lines from the second file to the list of lines from the first file
with open("ontologySnippet_dataProperties_simplified.ttl", "r") as context5:
    context_ontology_dataProperty = context5.readlines()
# The natural language question is read from a text file:
with open("sampleQuestions/question_random7.txt", 'r') as f:
    question = f.readlines()

prompt0 = f"""
Extract the classes or entities from the natural language question: {question}. 
E.g., for the question 河南大调曲子板头曲这个乐种用了什么民族乐器？--return `["民族乐器", "民族", "乐器", "河南大调曲子板头曲", "河南", "河南省", "板头曲"]`, which allows overlapping classes or entities.
Note:
1. If the entity is in 《》, please prepare 2 versions, with one maintaining the 《》, while the other not, e.g., `["《彩云追月》", "彩云追月"]`.
2. If a literal part is enclosed by "" or “”, view the part as a whole, e.g., 请问“河南大调曲子板头曲”主要用了什么乐器？--you can extract the entities in this format: `["河南大调曲子板头曲", "乐器"]`. 
3. Return only the extracted classes or entities (represented in Chinese characters, words or phrases), in such json format `["thing1", "thing2", "thing3"]`(no adding redundant strings).
"""
result0 = callGPT(prompt0).replace("```json", "").replace("```", "").strip() # The .replace() method removes the "```json" string from the beginning and "```" string from the end of the string returned by callGPT, and the .strip() method removes any unnecessary whitespace or newlines that might exist at the beginning or end of the string returned by callGPT.
print('result0(entities or classes extracted):', result0) # The result is rendered in JSON format

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
5. As long as an entity(or class) in the natural language question exactly matches one value of the `rdfs:label` of a class in the ontology, that class must be extracted from the ontology.
For the entity(or class) list, you can refer to {result0}. 
6. 如果问句中涉及…类乐器，也不妨参考`wd:Q7403902 rdfs:label "乐器的类（声学）".`

最后，你要学会根据自然语言中的实例推测它们可能对应的类，然后再从本体中寻找这些潜在的类。根据这个原则，请再复查一遍，把潜在的类补上
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
5. As long as an entity(or class) in the natural language question exactly matches one value of the `rdfs:label` of a class in the ontology, that class must be extracted from the ontology.
For the entity(or class) list, you can refer to {result0}.

最后，你要学会根据自然语言中的实例推测它们可能对应的类，然后再从本体中寻找这些潜在的类。根据这个原则，请再复查一遍，把潜在的类补上
"""

prompt3 = f"""
### Task:
According to the given natural language question, extract relevant properties from the provided ontology and output them only in a json-formatted list (no adding redundant strings).
such as `["ex:property1", "ex:property2", "ex:property3"]`.
### Ontology:
{context_ontology_objectProperty3}
### Given the Natural Language Question:
{question}
### Instructions and Notes:
1. Retrieve properties from the ontology as long as any literals in the natural language question match the semantic content of their rdfs:label or rdfs:comment.
2. Analyze the semantic structure of the natural language question carefully to identify all relevant properties.
3. Ensure each retrieved property is represented by its namespace prefix defined in the ontology.
4. Extract all properties that are even minimally relevant to the question.
5. Examine each property with its label and comment, one by one.
6. As long as an entity in the natural language question matches one value of the `rdfs:label` of a property in the ontology, that property must be extracted from the ontology.
For the entity list, you can refer to {result0}.
"""

prompt4= f"""
### Task:
According to the given natural language question, extract relevant properties from the provided ontology and output them only in a json-formatted list (no adding redundant strings).
such as `["ex:property1", "ex:property2", "ex:property3"]`.
### Ontology:
{context_ontology_objectProperty4}
### Given the Natural Language Question:
{question}
### Instructions and Notes:
1. Retrieve properties from the ontology as long as any literals in the natural language question match the semantic content of their rdfs:label or rdfs:comment.
2. Analyze the semantic structure of the natural language question carefully to identify all relevant properties.
3. Ensure each retrieved property is represented by its namespace prefix defined in the ontology.
4. Extract all properties that are even minimally relevant to the question.
5. Examine each property with its label and comment, one by one.
6. As long as an entity in the natural language question matches one value of the `rdfs:label` of a property in the ontology, that property must be extracted from the ontology.
7. 句子中若存在形容词+名词的结构，也有可能从中提取出属性，比如，“某地域有哪些拉弦类乐器？”，它就可能涉及属性“rdfs:label: "乐器类型（声学角度）"”。
For the entity list, you can refer to {result0}.
"""

prompt5 = f"""
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
5. As long as an entity in the natural language question matches one value of the `rdfs:label` of a property in the ontology, that property must be extracted from the ontology.
For the entity list, you can refer to {result0}
"""

# Retrieve the classes that are not explicitly stated in the question but are related to the entities extracted from the question.
prompt6 = f"""
See the list of entities:
{result0}

Embed the entities in a SPARQL query to retrieve the classes of the entities, e.g., for extracted ["河南大调曲子板头曲", "乐器", "郑州市"], convert it into `VALUES ?label {"河南大调曲子板头曲" "乐器" "郑州市"}` which comforms to the SPARQL sytax:
```
define input:inference 'urn:owl.ccmusicrules0214'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
select distinct ?class where {{
    ?entity rdfs:label ?label ;
            rdf:type ?class .
    VALUES ?label {{"河南大调曲子板头曲" "乐器" "郑州市"}} .
}}
```
As to the extracted entities (or classes), do only provide one corresponding SPARQL query with no additional or redundant text, including backticks
"""
# --In the future, we may supplement the scope by updating `?entity rdfs:label ?label ;` to `?entity rdfs:lable|ctm:ethnicGroupAlias|ctm:musicianAlias|dbo:formerName|gn:alternateName ?label ;` to cover more cases

response = callGPT(prompt6).strip()
# print('\n\n','response:', response)

# Ensure only the SPARQL query is extracted from the response:
define_index = response.find("define") # This checks if the response contains the "define" keyword
if define_index != -1: # If "define" is found, the SPARQL query is extracted from the response
    sparql_query = response[define_index:]
else:
    # Fallback if "define" isn't found
    sparql_query = response.replace("```sparql", "").replace("```", "").strip()
sparql_query = sparql_query.strip("```")
print('\n\n','sparql_query to identify the implicit classes:\n',sparql_query) # This query is to identify the implicit classes of the entities in the natural language question

# Define a function to query the SPARQL endpoint. The 1st parameter is the SPARQL endpoint, the 2nd parameter is the SPARQL query, and the 3rd parameter is the graph IRI:
def query_sparql(endpoint, sparql_query_parameter, graph_iri_parameter):
    sparql = SPARQLWrapper(endpoint) # SPARQLWrapper is a Python wrapper around a SPARQL service; is also a library for executing SPARQL queries on an RDF endpoint and retrieving the results
    sparql.setQuery(sparql_query_parameter) # This initializes the query to be sent to the SPARQL endpoint using the string provided in `sparql_query_parameter`
    sparql.setReturnFormat(JSON) # This sets the return format of the query to JSON
    if graph_iri: # If a graph IRI is provided, it is added as a parameter to the SPARQL query
        sparql.addParameter("default-graph-uri", graph_iri_parameter) # This adds a parameter to the SPARQL query
    # print ("Debug_requestTheEntireURL:", sparql._getRequestURL())
    # print ("RequestHeader:", sparql.customHttpHeaders)
    # print ("RequestBody:", sparql.queryString)
    # print("Debug Request Endpoint:", endpoint)
    # print("Debug Query String:", sparql.queryString.strip("```"))
    results = sparql.query().convert() # This executes the query and converts the results into JSON format
    return results

# Query the SPARQL endpoint:
sparql_endpoint = "http://www.usources.cn:8891/sparql" # We can also use the endpoint "https://virtuoso.staging.simssa.ca/sparql"
graph_iri = "https://lib.ccmusic.edu.cn/graph/music" # We can also use the graph IRI "http://ChineseTraditionalMusicCultureKnowledgeBase"
sparql_results = query_sparql(sparql_endpoint, sparql_query, graph_iri) # It occasionally results in blank nodes here which won't interfere. Just ignore them
print('sparql_results:', sparql_results) # rendered in JSON format
# # Save sparql_results to a .json file:
# with open('sparql_results.json', 'w') as json_file:
#     json.dump(sparql_results, json_file, indent=4)


# Call the LLM to extract the classes and properties from the natural language question:
result1 = callGPT(prompt1)
print('\n\nresult1(classes extracted):', result1)
result2 = callGPT(prompt2)
print('\n\nresult2(classes extracted):', result2)
result3 = callGPT(prompt3)
print('\n\nresult3(objectProperty extracted):', result3)
result4 = callGPT(prompt4)
print('\n\nresult4(objectProperty extracted):', result4)
result5 = callGPT(prompt5)
print('\n\nresult5(dataProperty extracted):', result5)


# Function to parse the result1-n (to parse the JSON strings into lists):
def parse_result(result):
    # print(f"\n\nParsing result: {result}")
    if isinstance(result, str):
        if result.startswith("```json") and result.endswith("```"):
            result = result[7:-3].strip()  # Strip off the "```json" prefix and "```" suffix
        try:
            parsed_result = json.loads(result)
            # print(f"Parsed JSON result: {parsed_result}")
            return parsed_result
        except json.JSONDecodeError:
            # print(f"Error decoding JSON: {result}")
            return []
    elif isinstance(result, list):
        # print(f"Result is already a list: {result}")
        return result
    else:
        # print(f"Unexpected result format: {result}")
        return []

# Parse the JSON strings into "lists"
result1_list = parse_result(result1)
result2_list = parse_result(result2)
result3_list = parse_result(result3)
result4_list = parse_result(result4)
result5_list = parse_result(result5)

# Combine upper results into a single list and remove duplicates
combined_results = list(set(result1_list + result2_list + result3_list + result4_list + result5_list)) # uses set(...) to remove duplicates before converting back to a list
# Print('\n\ncombined_results:', combined_results) # This prints the combined results in a list format
# Sort items into classes and properties, and arrange them in ascending order
class_list = sorted([item for item in combined_results if not item.startswith("wdt:") and item.split(":")[1][0].isupper()]) # `item.split(":")[1][0]`: The code splits the string “item” at the colon, takes the second part ([1]), then retrieves its first character ([0])
property_list = sorted([item for item in combined_results if item.startswith("wdt:") or item.split(":")[1][0].islower()])
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
    # 1) Turn the URI string into a URIRef object
    uri_ref = URIRef(uri)
    # 2) Use graph.qname(...) to get the prefixed form of the URI (e.g., ctm:Instrument)
    return graph.qname(uri_ref)

def render_classes_with_prefix(sparql_results, class_list_str):
    """Parse the local TTL file to retrieve all namespace prefixes, then convert SPARQL results to prefixed URIs."""
    # 1) Create an empty graph
    g = rdflib.Graph()
    # 2) Parse the local TTL file to load its prefixes and triples
    g.parse(
        "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl",
        format="ttl"
    )
    
    # 1) Process the SPARQL results to get prefixed URIs.
    sparql_classes = []
    for binding in sparql_results['results']['bindings']:
        # Extract the full URI from the SPARQL result.
        class_uri = binding['class']['value']
        # Convert the full URI to its prefixed form.
        short_name = shorten_uri(class_uri, g)
        sparql_classes.append(short_name)
    
    # 2) Process the original class_list_str.
    #    (Since class_list_str is defined as " ".join(class_list), we split it using space.)
    original_classes = class_list_str.split()
    
    # 3) Merge both lists and remove duplicates.
    merged_set = set(sparql_classes) | set(original_classes)
    # Optionally, sort the merged list (if desired).
    merged_list = sorted(merged_set)
    
    # 4) Build the final merged string.
    merged = " ".join(merged_list) + " rdfs:Literal" # There may appear a blanknode occassionally. Just ignore it
    #print ("merged:", merged)

    # 5) Print and return the merged result.
    print("Transformed ClassList =", "{" + ", ".join(f'"{item}"' for item in merged.split()) + "}")
    return merged

# Later in your code, call the function, for example:
merged_class_list = render_classes_with_prefix(sparql_results, class_list_str)
print("Transformed PropertyList =", "{" + ", ".join(f'"{item}"' for item in property_list_str.split()) + "}")



# 2025 early March
# 整体思路：类是肯定能找全的；属性不好找，没关系，核心思路是“以全概偏”。三个要点策略：
# （1）“最坏的打算”就是，把一个类可能连接的所有属性都找到，然后拼装子图（可以用 Shapes等）
# （2）即使子图很大，我们可以迭代、收敛——在已有子图的基础上，再提取它的子图
# （3）将本体切片切得更细