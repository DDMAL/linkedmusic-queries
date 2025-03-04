# 1_Step1_entitiesExtractiongFromNLQ_basedOnOntology.py
# Note: to activate virtual enviroment for python, please exectue `source /directory/of/your/virtual/environment/folder/bin/activate`, e.g., `source /Users/caojunjun/venv_extractSubgraphForLLMsGeneratingSPARQL/bin/activate`
# If you want to extact part of the script to a new file, e.g., to extract from the beginning to Line 50, please execute, `head -n 50 1_entitiesExtractiongFromNLQ_basedOnOntology.py > partialScript.py`
import json
# import pandas as pd 
from openai import OpenAI
from SPARQLWrapper import SPARQLWrapper, JSON # SPARQLWrapper is a Python wrapper around a SPARQL service; is also a library for executing SPARQL queries on an RDF endpoint and retrieving the results


# 1. SubGraph Extraction
# Invoke the OpenAI API:
client = OpenAI(
    api_key="LHAV5AoeevPPQ2iZKCIwCg2i9Jm5axE9mL5cJf0L71p6Iosl",
    base_url="https://oneapi.xty.app/v1"
)

def callGPT(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o", # We can use "gpt-4o" or "o1-preview" model
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
with open("sampleQuestions/question_FolkMusician_MusicType.txt", 'r') as f:
    question = f.readlines()

prompt0 = f"""
Extract the entities from the natural language question: {question}. 
Return only the extracted entities(represented in Chinese characters, words or phrases), in a json-formatted list (no adding redundant strings).
such as `["实体1", "实体2"]`.
"""
result0 = callGPT(prompt0)
print('result0(entities and properties extracted):', result0)
