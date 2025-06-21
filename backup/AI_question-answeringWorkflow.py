# AI_question-answeringWorkflow.py
# 完整的自然语言问题到SPARQL查询的AI问答工作流程
# 整合了实体提取、子图组装、SPARQL生成、验证、RAG和推荐系统
# Note: to activate virtual environment for python, please execute `source /directory/of/your/virtual/environment/folder/bin/activate`, e.g., `source /Users/caojunjun/venv_extractSubgraphForLLMsGeneratingSPARQL/bin/activate`

import json
import re
import rdflib
from rdflib import Graph, URIRef, BNode, RDF, RDFS, OWL
from openai import OpenAI
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime

# =============================================================================
# SECTION 1: CONFIGURATION AND SETUP
# =============================================================================

# Invoke the OpenAI API:
client = OpenAI(
    api_key="LHAV5AoeevPPQ2iZKCIwCg2i9Jm5axE9mL5cJf0L71p6Iosl", # To check the consumption of the API key, please visit https://cx.xty.app/#/. Put "sk-" before the API key then query the consumption
    base_url="https://oneapi.xty.app/v1"
)

def callGPT(prompt, model_name="gpt-4.1-2025-04-14"):
    """
    Call GPT API with different model options for different stages.
    For entity extraction: "gpt-4.1-2025-04-14" (stable for parsing)
    For SPARQL generation: "claude-sonnet-4-20250514" (better for structured queries)
    """
    completion = client.chat.completions.create(
        model=model_name, # We can use "gpt-4o" or "o1-preview" or "deepseek-r1" or "claude-sonnet-4-20250514" model
        max_tokens=4096,
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are an expert in extracting classes and properties from natural language questions about Chinese traditional music and mapping them to RDF/OWL ontology elements."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# =============================================================================
# SECTION 2: ENTITY EXTRACTION FROM NATURAL LANGUAGE QUESTION
# =============================================================================

def extract_entities_from_nlq():
    """
    Step 1: Extract entities, classes, and properties from natural language question.
    Returns the transformed class list and property list.
    """
    print("="*80)
    print("STEP 1: ENTITY EXTRACTION FROM NATURAL LANGUAGE QUESTION")
    print("="*80)
    
    # Read the context and question from the files:
    # The classes ontology snippets are divided into two parts to avoid exceeding the token limit of the OpenAI API:
    with open("ontologySnippet_classes1_simplified.ttl", "r") as context1: 
        context_ontology_class1 = context1.readlines()
    with open("ontologySnippet_classes2_simplified.ttl", "r") as context2: 
        context_ontology_class2 = context2.readlines()
    # The object and data properties ontology snippets are read separately:
    with open("ontologySnippet_objectProperties1_simplified.ttl", "r") as context3: 
        context_ontology_objectProperty3 = context3.readlines()
    with open("ontologySnippet_objectProperties2_simplified.ttl", "r") as context4: 
        context_ontology_objectProperty4 = context4.readlines()
    with open("ontologySnippet_dataProperties_simplified.ttl", "r") as context5:
        context_ontology_dataProperty = context5.readlines()
    
    # The natural language question is read from a text file:
    with open("sampleQuestions/anyQuestion.txt", 'r') as f:
        question = f.readlines()
    
    print(f"Natural Language Question: {question}")
    
    # Extract basic entities from the question
    prompt0 = f"""
    Extract the classes or entities from the natural language question: {question}. 
    E.g., for the question 河南大调曲子板头曲这个乐种用了什么民族乐器？--return `["民族乐器", "民族", "乐器", "河南大调曲子板头曲", "河南", "河南省", "板头曲"]`, which allows overlapping classes or entities.
    Note:
    1. If the entity is in 《》, please prepare 2 versions, with one maintaining the 《》, while the other not, e.g., `["《彩云追月》", "彩云追月"]`.
    2. If a literal part is enclosed by "" or "", view the part as a whole, e.g., 请问"河南大调曲子板头曲"主要用了什么乐器？--you can extract the entities in this format: `["河南大调曲子板头曲", "乐器"]`. 
    3. Return only the extracted classes or entities (represented in Chinese characters, words or phrases), in such json format `["thing1", "thing2", "thing3"]`(no adding redundant strings).
    """
    
    result0 = callGPT(prompt0).replace("```json", "").replace("```", "").strip()
    print('result0(entities or classes extracted):', result0)
    
    # Extract classes from ontology snippets
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

    # Extract properties from ontology snippets
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

    prompt4 = f"""
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
    7. 句子中若存在形容词+名词的结构，也有可能从中提取出属性，比如，"某地域有哪些拉弦类乐器？"，它就可能涉及属性"rdfs:label: "乐器类型（声学角度）""。
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

    # Query SPARQL endpoint to find implicit classes
    prompt6 = f"""
    See the list of entities:
    {result0}

    Embed the entities in a SPARQL query to retrieve the classes of the entities, e.g., for extracted ["河南大调曲子板头曲", "乐器", "郑州市"], convert it into `VALUES ?label {"河南大调曲子板头曲" "乐器" "郑州市"}` which conforms to the SPARQL syntax:
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

    response = callGPT(prompt6).strip()
    
    # Ensure only the SPARQL query is extracted from the response:
    define_index = response.find("define")
    if define_index != -1:
        sparql_query = response[define_index:]
    else:
        # Fallback if "define" isn't found
        sparql_query = response.replace("```sparql", "").replace("```", "").strip()
    sparql_query = sparql_query.strip("```")
    print('\n\nsparql_query to identify the implicit classes:\n', sparql_query)

    # Query the SPARQL endpoint:
    sparql_endpoint = "http://www.usources.cn:8891/sparql"
    graph_iri = "https://lib.ccmusic.edu.cn/graph/music"
    sparql_results = query_sparql(sparql_endpoint, sparql_query, graph_iri)
    print('sparql_results:', sparql_results)

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

    # Parse the JSON strings into lists
    def parse_result(result):
        if isinstance(result, str):
            if result.startswith("```json") and result.endswith("```"):
                result = result[7:-3].strip()
            try:
                parsed_result = json.loads(result)
                return parsed_result
            except json.JSONDecodeError:
                return []
        elif isinstance(result, list):
            return result
        else:
            return []

    # Parse the JSON strings into "lists"
    result1_list = parse_result(result1)
    result2_list = parse_result(result2)
    result3_list = parse_result(result3)
    result4_list = parse_result(result4)
    result5_list = parse_result(result5)

    # Combine results and remove duplicates
    combined_results = list(set(result1_list + result2_list + result3_list + result4_list + result5_list))
    
    # Sort items into classes and properties
    class_list = sorted([item for item in combined_results if not item.startswith("wdt:") and item.split(":")[1][0].isupper()])
    property_list = sorted([item for item in combined_results if item.startswith("wdt:") or item.split(":")[1][0].islower()])
    
    # Transform the format of ClassList and PropertyList
    class_list_str = " ".join(class_list)
    property_list_str = " ".join(property_list)

    # Process SPARQL results and merge with extracted classes
    merged_class_list = render_classes_with_prefix(sparql_results, class_list_str)
    
    print("Transformed ClassList =", "{" + ", ".join(f'"{item}"' for item in merged_class_list.split()) + "}")
    print("Transformed PropertyList =", "{" + ", ".join(f'"{item}"' for item in property_list_str.split()) + "}")

    # Export the transformed lists to files
    export_transformed_lists(merged_class_list, property_list_str)
    
    return question, merged_class_list, property_list_str

# =============================================================================
# SECTION 3: SUBGRAPH ASSEMBLY AND SPARQL GENERATION  
# =============================================================================

def assemble_subgraph_and_generate_sparql(question, merged_class_list, property_list_str):
    """
    Step 2: Assemble ontology subgraph and generate SPARQL query.
    """
    print("="*80)
    print("STEP 2: SUBGRAPH ASSEMBLY AND SPARQL GENERATION")
    print("="*80)
    
    # Configuration
    owl_file_path = "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl"
    
    # Convert string lists to sets
    given_classes = set(merged_class_list.split())
    given_properties = set(property_list_str.split())
    
    print(f"Loaded classes: {given_classes}")
    print(f"Loaded properties: {given_properties}")
    
    # 统计给定实体的总数
    total_entities = len(given_classes) + len(given_properties)
    print(f"Total given entities: {total_entities} (classes: {len(given_classes)}, properties: {len(given_properties)})")
    
    # 根据实体数量决定处理策略
    if total_entities <= 25:
        print("Entity count ≤ 25: Using direct extraction without connectivity filtering")
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
        owl_file_path, extracted_classes, extracted_properties = extract_connected_subgraph_from_owl(
            owl_file_path, given_classes, given_properties
        )
        
        print("Extracted Classes (after connectivity filtering):")
        for c in sorted(extracted_classes):
            print("  ", c)
        print("Extracted Properties (after connectivity filtering):")
        for p in sorted(extracted_properties):
            print("  ", p)
    
    # Extract subgraph triples
    triple_subset = retrieve_specific_subset(owl_file_path, extracted_classes, extracted_properties)

    # Create subgraph
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
        f.write(turtle_output)
    print("Assembled subgraph saved to: assembledSubgraphOfOntology.ttl")

    # Generate SPARQL query from the ontology subgraph
    print("="*50)
    print("SPARQL GENERATION")
    print("="*50)
    
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

    sparql_query = callGPT(prompt6, "claude-sonnet-4-20250514").strip().replace("```sparql", "").strip("```")
    print('\n\nThe sparql_query based on the ontology subgraph:\n', sparql_query)

    # Verify the generated SPARQL query
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

    # Clean and process the SPARQL response
    response = callGPT(prompt6_verification, "claude-sonnet-4-20250514").strip()
    clean_response = re.sub(r'```(?:sparql)?', '', response)
    clean_response = clean_response.strip()
    
    # Check if the response starts with PREFIX, if not, remove everything before SELECT
    prefix_index = clean_response.find("PREFIX")
    if prefix_index != -1:
        clean_response = clean_response[prefix_index:]
    else:
        select_index = clean_response.find("SELECT")
        if select_index != -1:
            clean_response = clean_response[select_index:]
    
    # Add the inference directive at the beginning
    sparql_query = "define input:inference 'urn:owl.ccmusicrules0214'\n" + clean_response
    print('\n\nThe sparql_query based on the ontology subgraph (verified):\n' + sparql_query)

    # Export SPARQL query to .sparql file with the natural language question as comment
    sparql_filename = "generated_sparql_query.sparql"
    with open(sparql_filename, 'w', encoding='utf-8') as f:
        question_text = ''.join(question).strip()
        f.write(f"# {question_text}\n")
        f.write(sparql_query)
    print(f"\n\nSPARQL query has been saved to: {sparql_filename}")
    
    return sparql_query, turtle_output

# =============================================================================
# SECTION 4: QUERY EXECUTION AND RESULTS PROCESSING
# =============================================================================

def execute_sparql_and_process_results(sparql_query, turtle_output, question):
    """
    Step 3: Execute SPARQL query and process results with RAG and recommendations.
    """
    print("="*80)
    print("STEP 3: QUERY EXECUTION AND RESULTS PROCESSING")
    print("="*80)
    
    # Query the SPARQL endpoint
    sparql_endpoint = "http://www.usources.cn:8891/sparql"
    graph_iri = "https://lib.ccmusic.edu.cn/graph/music"
    sparql_results = query_sparql(sparql_endpoint, sparql_query, graph_iri)

    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_QueryResultInJson = f"sparql_results_{timestamp}.json"

    # Write results to JSON file
    with open(output_QueryResultInJson, 'w', encoding='utf-8') as f:
        json.dump(sparql_results, f, ensure_ascii=False, indent=2)
    print(f"\n\nQuery results have been saved to: {output_QueryResultInJson}")

    # Create truncated version for prompts
    sparql_results_for_prompts = truncate_sparql_results_for_prompts(sparql_results)

    # Optional: Save truncated version to a separate file for inspection
    if sparql_results_for_prompts != sparql_results:
        truncated_filename = f"sparql_results_truncated_{timestamp}.json"
        with open(truncated_filename, 'w', encoding='utf-8') as f:
            json.dump(sparql_results_for_prompts, f, ensure_ascii=False, indent=2)
        print(f"Truncated results (for prompts) saved to: {truncated_filename}")

    # Retrieval Augmented Generation (RAG)
    print("="*50)
    print("RAG ANALYSIS")
    print("="*50)
    
    prompt7 = f"""
    Based on a natural language question: {question},

    and the related ontology snippet: {turtle_output}, 

    and the subsequent SPARQL query: {sparql_query}, 

    from visiting a SPARQL Endpoint we retrieved the result, part of which is shown as: {sparql_results_for_prompts}. 

    1. Explain the query result based on the question, the ontology snippet, and the SPARQL query.
    2. If the result is too large, you can conduct a statistical analysis with a summary.
    3. Compare the result with your own knowledge about the domain. Find out whether there is any inadequacy or inconsistency in the result. Enrich the explanation via comparison.
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

    RAG_result = callGPT(prompt7, "claude-sonnet-4-20250514")
    print('\n\nRAG Analysis Result:', RAG_result)

    # Ontology-based Recommendation System
    print("="*50)
    print("RECOMMENDATION SYSTEM")
    print("="*50)
    
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

    Recommendation_result = callGPT(prompt8, "claude-sonnet-4-20250514")
    print('\n\nRecommendation System Result:', Recommendation_result)
    
    return RAG_result, Recommendation_result

# =============================================================================
# SECTION 5: UTILITY FUNCTIONS
# =============================================================================

def query_sparql(endpoint, sparql_query_parameter, graph_iri_parameter):
    """Define a function to query the SPARQL endpoint."""
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(sparql_query_parameter)
    sparql.setReturnFormat(JSON)
    if graph_iri_parameter:
        sparql.addParameter("default-graph-uri", graph_iri_parameter)
    results = sparql.query().convert()
    return results

def shorten_uri(uri, graph):
    """Convert a full URI into a prefixed form using the graph's known namespaces."""
    uri_ref = URIRef(uri)
    return graph.qname(uri_ref)

def render_classes_with_prefix(sparql_results, class_list_str):
    """Parse the local TTL file to retrieve all namespace prefixes, then convert SPARQL results to prefixed URIs."""
    g = rdflib.Graph()
    g.parse(
        "/Users/caojunjun/WPS_Synchronized_Folder/McGill_DDMAL/GitHub/linkedmusic-queries/ChineseTraditionalMusicKnowledgeBase/3versionsOfOntology/ontologyForChineseTraditionalMusicKnowledgeBase_2025_withAdditionalAnnotationForLLM_extractingEntityFromOntology_simplifiedForOntologySegmentation.ttl",
        format="ttl"
    )
    
    # Process the SPARQL results to get prefixed URIs
    sparql_classes = []
    for binding in sparql_results['results']['bindings']:
        class_uri = binding['class']['value']
        short_name = shorten_uri(class_uri, g)
        sparql_classes.append(short_name)
    
    # Process the original class_list_str
    original_classes = class_list_str.split()
    
    # Merge both lists and remove duplicates
    merged_set = set(sparql_classes) | set(original_classes)
    merged_list = sorted(merged_set)
    
    # Build the final merged string
    merged = " ".join(merged_list) + " rdfs:Literal"
    
    return merged

def export_transformed_lists(class_list_str, property_list_str):
    """Export the transformed class list and property list to separate files."""
    # Process the class list
    class_items = class_list_str.split()
    class_set = set(class_items)
    
    # Process the property list  
    property_items = property_list_str.split()
    property_set = set(property_items)
    
    # Save class list to file
    with open("transformed_class_list.txt", "w", encoding="utf-8") as f:
        f.write("{\n")
        for i, item in enumerate(sorted(class_set)):
            if i < len(class_set) - 1:
                f.write(f'    "{item}",\n')
            else:
                f.write(f'    "{item}"\n')
        f.write("}")
    
    # Save property list to file  
    with open("transformed_property_list.txt", "w", encoding="utf-8") as f:
        f.write("{\n")
        for i, item in enumerate(sorted(property_set)):
            if i < len(property_set) - 1:
                f.write(f'    "{item}",\n')
            else:
                f.write(f'    "{item}"\n')
        f.write("}")
    
    print(f"\nTransformed lists exported to:")
    print(f"  - transformed_class_list.txt ({len(class_set)} items)")
    print(f"  - transformed_property_list.txt ({len(property_set)} items)")

def truncate_sparql_results_for_prompts(results, max_rows=50):
    """Truncate SPARQL results to approximately max_rows while maintaining JSON structure."""
    if not isinstance(results, dict) or 'results' not in results:
        return results
    
    bindings = results.get('results', {}).get('bindings', [])
    
    if len(bindings) <= max_rows:
        return results
    
    # Create truncated version
    truncated_results = {
        'head': results.get('head', {}),
        'results': {
            'bindings': bindings[:max_rows]
        }
    }
    
    # Add metadata about truncation
    if 'head' in truncated_results:
        truncated_results['head']['truncated'] = True
        truncated_results['head']['original_count'] = len(bindings)
        truncated_results['head']['truncated_count'] = max_rows
    
    return truncated_results

# Functions from subgraph assembly section
def process_rdf_list(graph, list_node):
    """Process an RDF list (used for owl:unionOf or owl:intersectionOf) and return a set of class URIs."""
    items = set()
    while list_node and list_node != RDF.nil:
        first = graph.value(list_node, RDF.first)
        if first is not None:
            items.update(extract_valid_classes_from_node(graph, first))
        list_node = graph.value(list_node, RDF.rest)
    return items

def extract_valid_classes_from_node(graph, node):
    """Recursively extract "positive" class URIs from a class expression node."""
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
    return valid

def get_property_type(graph, prop):
    """Determine the property type by checking explicit rdf:type values or inferring from rdfs:range."""
    types = set(graph.objects(prop, RDF.type))
    if OWL.DatatypeProperty in types:
        return "data"
    if OWL.ObjectProperty in types:
        return "object"
    
    # Infer type by examining the rdfs:range
    range_nodes = list(graph.objects(prop, RDFS.range))
    for r in range_nodes:
        if r == RDFS.Literal or str(r).endswith("Literal"):
            return "data"
    return None

def resolve_curie(graph, curie):
    """Resolve a CURIE (e.g., "ctm:MusicType") to a full URI using the graph's namespace manager."""
    if ":" in curie:
        prefix, local = curie.split(":", 1)
        for ns_prefix, ns_uri in graph.namespace_manager.namespaces():
            if ns_prefix == prefix:
                return URIRef(ns_uri + local)
    return URIRef(curie)

def extract_connected_subgraph_from_owl(owl_file_path, given_classes, given_properties):
    """Load the OWL ontology and extract the connected subgraph based on given classes and properties."""
    graph = Graph()
    graph.parse(owl_file_path, format="turtle")
    
    # Resolve the given classes and properties to full URIs
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
    
    # Process each given property
    for prop_str in given_properties_resolved:
        prop = URIRef(prop_str)
        ptype = get_property_type(graph, prop)
        if ptype is None:
            continue
    
        # Process rdfs:domain
        domain_nodes = list(graph.objects(prop, RDFS.domain))
        domain_valid = set()
        for d in domain_nodes:
            if isinstance(d, URIRef):
                domain_valid.add(str(d))
            else:
                domain_valid.update(extract_valid_classes_from_node(graph, d))
                
        if ptype == "object":
            # Process rdfs:range for ObjectProperties
            range_nodes = list(graph.objects(prop, RDFS.range))
            range_valid = set()
            for r in range_nodes:
                if isinstance(r, URIRef):
                    range_valid.add(str(r))
                else:
                    range_valid.update(extract_valid_classes_from_node(graph, r))
            # For an ObjectProperty, require at least one matching class in both domain and range
            if (domain_valid & given_classes_resolved) and (range_valid & given_classes_resolved):
                extracted_properties.add(prop_str)
                extracted_classes.update(domain_valid & given_classes_resolved)
                extracted_classes.update(range_valid & given_classes_resolved)
        elif ptype == "data":
            # For a DataProperty, if at least one given class is in its domain
            if domain_valid & given_classes_resolved:
                extracted_properties.add(prop_str)
                extracted_classes.update(domain_valid & given_classes_resolved)
                extracted_classes.add("rdfs:Literal")
    
    return owl_file_path, extracted_classes, extracted_properties

def retrieve_specific_subset(owl_file_path, extracted_classes, extracted_properties): 
    """从 OWL 本体文件中提取以指定的类和属性为主语的所有三元组，即构成所需的子图。"""
    g = rdflib.Graph()
    g.parse(owl_file_path, format='ttl')

    # Convert classes and properties to URI refs if possible
    seeds = []
    for item in set(extracted_classes).union(extracted_properties):
        if item.startswith('http'):
            seeds.append(URIRef(item))
        elif ':' in item:
            resolved_uri = resolve_curie(g, item)
            seeds.append(resolved_uri)
    
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

# =============================================================================
# MAIN WORKFLOW EXECUTION
# =============================================================================

if __name__ == '__main__':
    """
    Complete AI Question-Answering Workflow:
    1. Extract entities from natural language question
    2. Assemble ontology subgraph and generate SPARQL query
    3. Execute query and provide RAG analysis and recommendations
    """
    print("="*80)
    print("AI QUESTION-ANSWERING WORKFLOW")
    print("Integrating Entity Extraction, Subgraph Assembly, SPARQL Generation, RAG, and Recommendations")
    print("="*80)
    
    try:
        # Step 1: Entity Extraction
        question, merged_class_list, property_list_str = extract_entities_from_nlq()
        
        # Step 2: Subgraph Assembly and SPARQL Generation
        sparql_query, turtle_output = assemble_subgraph_and_generate_sparql(question, merged_class_list, property_list_str)
        
        # Step 3: Query Execution and Results Processing
        rag_result, recommendation_result = execute_sparql_and_process_results(sparql_query, turtle_output, question)
        
        print("="*80)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        print("Generated files:")
        print("  - transformed_class_list.txt")
        print("  - transformed_property_list.txt") 
        print("  - assembledSubgraphOfOntology.ttl")
        print("  - generated_sparql_query.sparql")
        print("  - sparql_results_[timestamp].json")
        print("  - sparql_results_truncated_[timestamp].json (if applicable)")
        print("="*80)
        
    except Exception as e:
        print(f"Error in workflow execution: {e}")
        import traceback
        traceback.print_exc()

# =============================================================================
# ADDITIONAL NOTES AND FUTURE IMPROVEMENTS
# =============================================================================

# 2025 early March
# 整体思路：类是肯定能找全的；属性不好找，没关系，核心思路是"以全概偏"。三个要点策略：
# （1）"最坏的打算"就是，把一个类可能连接的所有属性都找到，然后拼装子图（可以用 Shapes等）
# （2）即使子图很大，我们可以迭代、收敛——在已有子图的基础上，再提取它的子图
# （3）将本体切片切得更细

# 其他灵感：
# 依然准备一个样本库，包含了各种问题及相应的SPARQL
# 如果在prompt6_verification基础上生成的SPARQL，其通过 Endpoint无法返回结果（或报错），那么，我们可以：
# （1）根据它生成的SPARQL所反映的本体结构、SPARQL语句中的关键词、特殊函数等，通过相似度匹配样本库中的SPARQL
# （2）同时根据自然语言问题的Edit distance (Levenshtein distance)匹配样本库中相似的问题
# （3）对(1)(2)做一个折中，即选定一个最合适的 example（NLQ+SPARQL），再用这个新的 context 训练 LLMs，以重新生成 SPARQL

# Other tips for RAG: For the retrieved results from the SPARQL visiting the Endpoint, please
    # Access the accessible URI and provide a brief summary
