# linkedmusic-queries
Various methods to query our data lake, e.g., Using SPARQL against Open Link Virtuoso's graphs. However, For music users, what if they don't know how to handle SPARQL coding, the accessibility of our data lake would be weakened. Therefore, the initial goal in this repository is to explore "How to convert the users' natural language queries to SPARQL query, with the efficacy of Large Language Models". Above all, it's about 

### Via Prompt Engineering on LLMs, Realize NLQ2SPARQL 


## 1. Use ontology snippet as context for prompte engineering (2024Dec-2025Mar)
Junjun Cao has been utlizing the Chinese Traditional Music KnowledgeBase (abbreviated as CTM) as a prior experiment because this knowledge base has a comprehensive ontology, which can serve as ready-made context for prompting ChatGPT to convert NLQ(natural language query) into SPARQL
> for issues marked with "CTM", it's specifically meant for Chinese Traditional Music knowledgeBase

This experiment has solved some problems/issues:

This experiment addresses the challenge of oversized ontologies hindering LLMs in generating accurate SPARQL queries. Our--

### "ontology-subgraph-extraction approach"

--focuses the LLM on relevant local ontology snippets. For detailed information, please refer to the paper abstract at https://github.com/DDMAL/linkedmusic-queries/blob/main/ChineseTraditionalMusicKnowledgeBase/Knowledge%20Base%20for%20ESEA%20(East-and-Southeast-Asian)%20Traditional%20Music%20and%20its%20NLQ2SPARQL%20Intelligent%20Question-Answering%20System%20Development.pdf

For more details, please contact Junjun Cao (alienmusedh@gmail.com)for the entire paper on this subject.


## 1.1 For other RDF databases, how to extract the ontology automatically?
There are at least 2 methods:
(1) Please locate to https://github.com/JervenBolleman/void-generator.
You can generate "shapes" for any given RDF graph, then prompt LLMs to convert shapes to a "norminal" ontology.
(2) For RDB2RDF in the internal process of Open Link Virtuoso, you can map a schema of a relational database to an ontology.

## 1.2 How to carry out NLQ2SPARQL in federal queries-query across different databases?
--especially when the different databases are all reconciled with Wikidata. This is to be explored.

## 2. There are other potential approaches especially when it's difficult to obtain the ontology or in other special cases
2.1 Please refer to https://github.com/DDMAL/linkedmusic-queries/discussions/27.

2.2 Junjun Cao has also conducted a primary literature review on NLQ2SPARQL which can be read on his paper to be published, titled _"Knowledge Base for ESEA (East-and-Southeast-Asian) Traditional Music and its Ontology-subgraph-driven NLQ2SPARQL Intelligent Question-Answering System Research"_.