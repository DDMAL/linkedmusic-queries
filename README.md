# linkedmusic-queries
Various methods to query our data lake, e.g., Virtuoso graphs

## 2024Dec-2025Mar
Junjun Cao has been utlizing the Chinese Traditional Music KnowledgeBase (abbreviated as CTM) as a prior experiment because this knowledge base has a comprehensive ontology, which can serve as ready-made context for prompting ChatGPT to convert NLQ(natural language query) into SPARQL
> for issues marked with "CTM", it's specifically meant for Chinese Traditional Music knowledgeBase

This experiment has solved some problems/issues:
This experiment addresses the challenge of oversized ontologies hindering LLMs in generating accurate SPARQL queries. Our ontology-subgraph-extraction approach focuses the LLM on relevant local ontology snippets. For detailed information, please refer to the paper abstract at https://github.com/DDMAL/linkedmusic-queries/blob/main/ChineseTraditionalMusicKnowledgeBase/Knowledge%20Base%20for%20ESEA%20(East-and-Southeast-Asian)%20Traditional%20Music%20and%20its%20NLQ2SPARQL%20Intelligent%20Question-Answering%20System%20Development.pdf
For more details, please contact Junjun Cao for the entire paper on this subject.