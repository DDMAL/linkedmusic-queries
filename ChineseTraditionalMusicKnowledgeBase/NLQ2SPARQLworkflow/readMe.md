NLQ2SPARQL: short for converting Natural Language Question to SPARQL

# sampleQuestions:
questions to test NLQ2SPARQL's effect and accuracy. The name of the files reflect the underlying classes and their sequential positions in mutual relations

# storageOfPairsOfNLQ&correspondingCorrectSPARQL&others:
This is corresponding to "sampleQuestions"

# 1_entitiesExtractionFromNLQ_basedOnOntology.py
# 2_subGraphAssemblyFromOntology_3_SPARQLgeneration.py
--most important

# assembledSubgraphOfOntology.ttl:
This is a generated file from executinbg 2_subGraphAssemblyFromOntology_3_SPARQLgeneration.py. The content will change after each different execution

# classesList_example.csv & classesList.csv:
To enhace "entity extraction" from ontoloyg, we may render ontology as a list of vocabularies, so we have the drafts

# extractClasses_rdfsLabelAndRdfsCommentFromOWL.py:
This Python script is designed to extract information from an OWL (Web Ontology Language) ontology file and convert it to CSV format

# segmented ontology snippets:
    # ontologySnippet_classes1_simplified.ttl...
    # ontologySnippet_dataProperties_simplified.ttl
    # ontologySnippet_objectProperties_simplified.ttl
--refer to "3.2.2 Ontology Segmentation" of Junjun Cao's paper or refer to "1_entitiesExtractionFromNLQ_basedOnOntology.py"

# prompt_generatePythonForSubGraphExtraction：
