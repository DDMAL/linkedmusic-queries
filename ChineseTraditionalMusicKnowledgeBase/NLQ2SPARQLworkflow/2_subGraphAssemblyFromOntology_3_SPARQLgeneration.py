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

def process_rdf_list(graph, list_node): # 处理RDF列表（用于owl:unionOf或owl:intersectionOf）并返回类URI集合
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
    
    函数功能：从OWL本体中提取"连通子图"：给定一组类和属性作为"种子"，找出所有能在这些类之间建立连接的属性，以及这些属性涉及的相关类。
    连通性判断标准：
        对象属性：domain和range中都必须有给定类 → 确保类之间有双向连接
        数据属性：只要domain中有给定类即可 → 因为range通常是字面值
    当遇到OWL的复合类表达式时：
        ✅ 支持 owl:unionOf（并集）：A ∪ B ∪ C → 提取所有类
        ✅ 支持 owl:intersectionOf（交集）：A ∩ B ∩ C → 提取所有类
        ❌ 忽略 owl:complementOf（补集）：¬A → 直接跳过
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

# 注意：原有的 main() 函数已被移除，所有逻辑已整合到 if __name__ == '__main__': 部分
# 这样避免了重复定义和混淆

def retrieve_specific_subset(owl_file_path, extracted_classes, extracted_properties): 
    """
    从 OWL 本体文件中提取以指定的类和属性为主语的所有三元组，即构成所需的子图。
    
    使用广度优先搜索（BFS）从给定的类和属性开始，提取所有以它们为主语的三元组，
    并递归处理遇到的空白节点以确保完整性。
    
    Args:
        owl_file_path: OWL本体文件的完整路径
        extracted_classes: 提取的类集合
        extracted_properties: 提取的属性集合
    
    Returns:
        list: 包含所有相关三元组的列表，每个三元组形如 (主语, 谓语, 宾语)
    """
    import rdflib
    from rdflib import URIRef, BNode

    g = rdflib.Graph()
    g.parse(owl_file_path, format='ttl')

    # Convert classes and properties to URI refs if possible
    seeds = []
    for item in set(extracted_classes).union(extracted_properties):
        if item.startswith('http'):
            seeds.append(URIRef(item))
        elif ':' in item:
            # CURIE format - resolve it
            resolved_uri = resolve_curie(g, item)
            seeds.append(resolved_uri)
        # Skip items that are neither full URIs nor CURIEs
    print(f"Debug: Total seeds found: {len(seeds)}")
    for seed in seeds:
        print(f"  Seed: {seed}")

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
    print(f"Debug: Total triples extracted: {len(subset_triples)}")
    return subset_triples


if __name__ == '__main__':
    # 获取初始配置
    owl_file_path = "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl"
    
    # Function to load set from file
    def load_set_from_file(filename):
        """Load a Python set from a text file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Remove the outer braces and parse as set
                content = content.strip('{}')
                items = []
                for line in content.split(',\n'):
                    line = line.strip()
                    if line:
                        # Remove quotes and whitespace
                        item = line.strip().strip('"').strip("'")
                        if item:
                            items.append(item)
                return set(items)
        except FileNotFoundError:
            print(f"Warning: {filename} not found. Using default values.")
            return set()
        except Exception as e:
            print(f"Error reading {filename}: {e}. Using default values.")
            return set()
    
    # Try to load from files first, fallback to default values
    given_classes = load_set_from_file("transformed_class_list.txt")
    given_properties = load_set_from_file("transformed_property_list.txt")
    
    # If files don't exist or are empty, use default values
    if not given_classes:
        print("Using default class list since file is empty or not found.")
        given_classes = {"bf:MusicInstrument", "cidoc-crm:E55_Type", "rdfs:Literal"}
    
    if not given_properties:
        print("Using default property list since file is empty or not found.")
        given_properties = {"bf:instrument", "bf:subject", "ctm:hasFullNameOf"}
    
    print(f"Loaded classes from file: {given_classes}")
    print(f"Loaded properties from file: {given_properties}")
    
    # 统计给定实体的总数
    total_entities = len(given_classes) + len(given_properties)
    print(f"Total given entities: {total_entities} (classes: {len(given_classes)}, properties: {len(given_properties)})")
    
    # 根据实体数量决定处理策略
    if total_entities <= 25: # 如果给定的实体（类+属性）的总数小于或等于该值，就不用采用“连通性过滤”策略（默认值为20，可以想象，如果大模型的能力越强，这个值可以更大）
        print("Entity count ≤ 25: Using direct extraction without connectivity filtering")
        # 直接使用给定的类和属性进行三元组提取
        extracted_classes = given_classes
        extracted_properties = given_properties
        
        print("Given Classes:")
        for c in sorted(extracted_classes):
            print("  ", c)
        print("Given Properties:")
        for p in sorted(extracted_properties):
            print("  ", p)
    else:
        print("Entity count > 25: Using connectivity filtering first")
        # 先进行连通性过滤，再提取三元组
        owl_file_path, extracted_classes, extracted_properties = extract_connected_subgraph_from_owl(
            owl_file_path, given_classes, given_properties
        )
        
        print("Extracted Classes (after connectivity filtering):")
        for c in sorted(extracted_classes):
            print("  ", c)
        print("Extracted Properties (after connectivity filtering):")
        for p in sorted(extracted_properties):
            print("  ", p)
    
    # 无论采用哪种策略，最终都调用retrieve_specific_subset进行三元组提取
    triple_subset = retrieve_specific_subset(
        owl_file_path, extracted_classes, extracted_properties
    )

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
    api_key="",
    base_url="https://oneapi.xty.app/v1"
)
def callGPT(prompt):
    completion = client.chat.completions.create(
        model="claude-sonnet-4-20250514", # We can use "gpt-4o" or "o1-preview" or "claude-3-7-sonnet-20250219" model
        max_tokens=4096,
        temperature=0.1,
        messages=[
            {"role": "user", "content": "You are an expert in converting natural language question to SPARQL in context of music metadata or ontology."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

with open("sampleQuestions/question_random7.txt", 'r') as f:
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
0. In addition to `rdfs:label`, the classes and properties in the SPARQL query should be consistent with the ontology snippet
1. Don't use language tag for the rdfs:Literals value in the SPARQL query
2. The question is associated with the domain of Chinese or East-and-Southeast-Asian music, so you may understand the entities priorly that you can correspond them to the classes in the given ontology
3. For each instance variable in the SPARQL, ensure that the labels for them are represented using `rdfs:label` property even if it is not explicitly mentioned in the ontology snippet. 但要注意，对象属性的值是一个对象，可能有rdfs:label；而数据属性的值是一个字面值，通常没有rdfs:label 
4. After examination and cross-checking, if modifications are required, do return only the modified SPARQL query without any additional text
5. Do ensure the SPARQL query's logic is inherently consistent with the natural language question and the ontology snippet
6. Don't forget the clarification of namespaces in the SPARQL query; Delete the needless prefixes clarification (which are not used in the query)
7. If you are uncertain about precision of specific classes or properties, you can broaden the retrieval scope using syntax such as: 
    7.1 The UNION keyword: to include multiple options to interpretate a question, especially when the question can be divided into multiple sub-questions, or in case of handling an objectProperty and a dataProperty which have the similar semantic meanings
    7.2 The | operator to represent a logical OR for properties
    7.3 The OPTIONAL keyword: 
        7.2.1 also useful when handling an objectProperty and a dataProperty which have the similar semantic meaning, etc.
        7.2.2 to allow partial matches, ensuring that queries remain valid even when certain properties or property values are missing. It is particularly beneficial for handling uncertain or "if, possibly" relationships (e.g., "Something may relate to something else") or when managing properties with similar semantics
8. 以封闭世界假设的思维来看待本体，譬如，一个属性的定义域或值域规定了哪些类，就用哪些类，其他类的实例不要轻易地连接这些属性     
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

# Export SPARQL query to .sparql file with the natural language question as comment
sparql_filename = "generated_sparql_query.sparql"
with open(sparql_filename, 'w', encoding='utf-8') as f:
    # Write the natural language question as a comment on the first line
    question_text = ''.join(question).strip()  # Convert list to string and strip whitespace
    f.write(f"# {question_text}\n")
    f.write(sparql_query)
print(f"\n\nSPARQL query has been saved to: {sparql_filename}")

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
import json
from datetime import datetime
sparql_results = query_sparql(sparql_endpoint, sparql_query, graph_iri)

# Generate timestamp for unique filename:
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_QueryResultInJson = f"sparql_results_{timestamp}.json"

# Write results to JSON file:
with open(output_QueryResultInJson, 'w', encoding='utf-8') as f:
    json.dump(sparql_results, f, ensure_ascii=False, indent=2) # This will save the SPARQL query results in a JSON file with a timestamp in its name （将 SPARQL query 的结果保存成一个 json 文件）
print(f"\n\nQuery results have been saved to: {output_QueryResultInJson}")
# print('\n\nsparql_results:', sparql_results) # rendered in JSON format


def truncate_sparql_results_for_prompts(results, max_rows=120):
    """
    Truncate(删节、截取) SPARQL results to approximately max_rows while maintaining JSON structure.
    
    Args:
        results: The original SPARQL results (dict)
        max_rows: Maximum number of rows to include (default: 1000)
    
    Returns:
        Truncated results maintaining JSON structure
    """
    # 1. 检查数据结构是否有效
    if not isinstance(results, dict) or 'results' not in results:
        return results
    
    bindings = results.get('results', {}).get('bindings', [])
    
    # 2. If we have fewer than max_rows, return the original (如果数据量≤1000行，返回原始数据)
    if len(bindings) <= max_rows:
        return results
    
    # 3. 如果数据量>120个 bindings，Create truncated version
    truncated_results = {
        'head': results.get('head', {}),
        'results': {
            'bindings': bindings[:max_rows] # 只取前120 个bindings
        }
    }
    
    # 4. Add metadata about truncation
    if 'head' in truncated_results:
        truncated_results['head']['truncated'] = True
        truncated_results['head']['original_count'] = len(bindings) # 原始数量
        truncated_results['head']['truncated_count'] = max_rows # 截取数量
    
    return truncated_results

# Create truncated version for prompts
sparql_results_for_prompts = truncate_sparql_results_for_prompts(sparql_results) # 这里的sparql_results是从SPARQL Endpoint查询得到的结果，sparql_results_for_prompts是“截取后的结果”（最多120 个bindings）
# ——sparql_results_for_prompts既包括如果文件大于120 个bindings的截取后的结果，也包括如果文件小于120 个bindings的即保留的原结果

# Optional: Save truncated version to a separate file for inspection
if sparql_results_for_prompts != sparql_results: # 如果截取（判别）后的数据与原始数据不相等（即发生了截取），就执行下面的代码块
    truncated_filename = f"sparql_results_truncated_{timestamp}.json" # 构造截取后的json文件的文件名
    with open(truncated_filename, 'w', encoding='utf-8') as f: # with为上下文管理器，自动处理文件打开和关闭
        # 将截取后的结果写入文件
        json.dump(sparql_results_for_prompts, f, ensure_ascii=False, indent=2) # 括弧中，第一个参数是要写入的对象，第二个参数是文件对象，ensure_ascii=False表示不转义非ASCII字符，indent=2表示缩进为2个空格
    print(f"Truncated results (for prompts) saved to: {truncated_filename}")


# Retrieval Augmented Generation (RAG): 
prompt7 = f"""
Based on a natural language question: {question},

and the related ontology snippet: {turtle_output}, 

and the subsequent SPARQL query: {sparql_query}, 

from visiting a SPARQL Endpoint we retrieved the result, part of which is shown as: {sparql_results_for_prompts}. 

1. Explain the query result based on the question, the ontology snippet, and the SPARQL query.
2. If the result is too large, you can conduct a statistical analysis with a summary.
3. Compare the result with your own knowledge about the domain. Find out whether there is any inadquacy or inconsistency in the result. Enrich the explaination via comparison.
...
4. Last but not least, if the result is too small or even empty, 
please "broaden the retrieval scope" by relaxing query conditions/constraints in the SPARQL or ...
For example:
    4.1 may use the UNION keyword to include multiple options to interpretate a question, especially when the question can be divided into multiple sub-questions, or in case of handling an objectProperty and a dataProperty which have the similar semantic meanings
    4.2 use the | operator to represent a logical OR for properties
    4.3 use the OPTIONAL keyword:
        4.3.1 also useful when handling an objectProperty and a dataProperty which have the similar semantic meaning, etc.
        4.3.2 to allow partial matches, ensuring that queries remain valid even when certain properties or property values are missing. It is particularly beneficial for handling uncertain or "if, possibly" relationships (e.g., "Something may relate to something else") or when managing properties with similar semantics
    ...
    4.4 remove class constraint on a variable to broaden the retrieval scope
    4.5 cancel FILTER condition to broaden the retrieval scope
        4.6 switch from exact matching to partial/containing matching to broaden the retrieval scope, especially when you determine that a term might be an abbreviation and has a full name behind it
        e.g., you may use `filter(contains())` or `filter(regex())`
    4.7 break down multiple-hop queries into fewer hops, to relieve the constraints of meeting all conditions across multiple hops
    ...
5. 但是还是要谨记，除了 rdfs:label 之外，SPARQL查询中涉及的类和属性应与本体片段保持一致。不要捏造本体中不存在的类或属性
"""

RAG_result = callGPT(prompt7)
print('\n\nprompt7_RAG_result:', RAG_result)

# Ontology-based Recommendation System
prompt8 = f"""
Based on a natural language question: {question}, 

and the related ontology snippet: {turtle_output}, 

and the subsequent SPARQL query: {sparql_query}, 

from visiting a SPARQL Endpoint we retrieved the result, part of which is shown as: {sparql_results_for_prompts}. 

Please recommend other potential SPARQL query patterns:
These are tips of generating the recommendations, only for your reference:
    1. **Identify the classes and properties in the ontology snippet that are used in the existing SPARQL query;
    2. **Determine their current relationships and position in the ontology snippet;
    3. **Expand to other adjacent classes or properties in the ontology snippet to recommend other possible query patterns that can yield more results;
- **This idea is regarding the ontology as a graph/network, and the recommendation is to explore other nodes (classes or properties) that are connected/adjacent to the ones embodied in the existing SPARQL query.
- **(以封闭世界假设的思维来看待本体，譬如，一个属性的定义域或值域规定了哪些类，就用哪些类，其他类的实例不要轻易地连接这些属性)

Return several SPARQL query patterns, along with the corresponding natural language questions, in a structured format.
"""

Recommendation_result = callGPT(prompt8)
print('\n\nprompt8_recommendation_result:', Recommendation_result)


# Other tips for RAG: For the retrieved results from the SPARQL visiting the Endpoint, please
    # Access the accessible URI and provide a brief summary



# 其他灵感：
# 依然准备一个样本库，包含了各种问题及相应的SPARQL
# 如果在prompt6_verification基础上生成的SPARQL，其通过 Endpoint无法返回结果（或报错），那么，我们可以：
# （1）根据它生成的SPARQL所反映的本体结构、SPARQL语句中的关键词、特殊函数等，通过相似度匹配样本库中的SPARQL
# （2）同时根据自然语言问题的Edit distance (Levenshtein distance)匹配样本库中相似的问题
# （3）对(1)(2)做一个折中，即选定一个最合适的 example（NLQ+SPARQL），再用这个新的 context 训练 LLMs，以重新生成 SPARQL
