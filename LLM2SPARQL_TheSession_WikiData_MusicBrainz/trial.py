import pandas as pd
from openai import OpenAI
from SPARQLWrapper import SPARQLWrapper, JSON

client = OpenAI(
    api_key="sk-lIjVysUlrOO0Ywpk34FdCa7719C544B4B90e6d316cC68e2f",
    base_url="https://oneapi.xty.app/v1"
)


def callGPT(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1000,
        temperature=0.1,
        messages=[
            {"role": "system", "content": "You are an expert in SPARQL in terms of music metadata or ontology."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


def query_sparql(endpoint, query, graph_iri):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.addDefaultGraph(graph_iri)

    results = sparql.query().convert()
    return results


with open("QueryMetaBrainz_context.txt", "r") as f:
    context = f.readlines()
with open("question_0.txt", 'r') as f:
    question = f.readlines()

context = "".join(context)
question = "".join(question)
prompt = question + "\n" + context

# Generate SPARQL query using GPT
sparql_query_prompt = f"""
Given the following RDF context and question, generate SPARQL query to retrieve the relevant information:

Context:
{context}

Question:
{question}

Caution:
1. Please provide only the SPARQL query without any additional text. 
2. *
3. We may request query across different graphs, so you may use the "GRAPH" Keyword or "SERVICE" Keyword in your SPARQL 
generation!
4. Please do the work by steps: 
    4.1 Generate the SPARQL query accordingly.
    4.2 Examine the SPARQL you generated to make sure it is syntactically correct!! If not correct, please fix it.
    4.3 Then give the SPARQL query that is correct.
"""
sparql_query = callGPT(sparql_query_prompt).strip()
# print(sparql_query)
sparql_query = sparql_query.replace("```sparql", "").strip("```")
print('The 1st round of sparql_query:', sparql_query)


# Query the SPARQL endpoint
sparql_endpoint = "https://virtuoso.staging.simssa.ca/sparql"
graph_iri = ""
sparql_results = query_sparql(sparql_endpoint, sparql_query, graph_iri)
# print(type(sparql_results))
print('sparql_results:', sparql_results)


# Process and display the results
def process_results(results):
    bindings = results['results']['bindings']
    processed_results = [{k: v['value'] for k, v in binding.items()} for binding in bindings]
    return pd.DataFrame(processed_results)


df_results = process_results(sparql_results)
print(df_results)

explanation_prompt = f"""
In terms of the "question"(which is like: {question}) I asked,
I executed the corresponding SPARQL query on the RDF data:
{sparql_query}
and obtained the following results:
{df_results.to_string(index=False)}
Please:
1. Explain whether the corresponding SPARQL query exactly matches the "question" provided. 
If not, please:
    1.1 Give give me a modified right solution of the SPARQL.
    1.2 You may adjust the "question" to a similar one that can be answered by the SPARQL query then give me
    the that SPARQL.
2. Explain those following results in natural language.
"""
explanation = callGPT(explanation_prompt)
print(explanation)
