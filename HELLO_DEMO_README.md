# Hello World NLQ2SPARQL Demonstration

This document describes the simple "Hello World" demonstration for the linkedmusic-queries NLQ2SPARQL system.

## Overview

The `hello_world_nlq2sparql.py` script provides a minimal demonstration of how natural language queries can be processed and converted to SPARQL queries in the context of music knowledge bases.

## Usage

### Basic Usage (Default "hello" query)
```bash
python3 hello_world_nlq2sparql.py
```

### Custom Query
```bash
python3 hello_world_nlq2sparql.py "your query here"
```

### Examples

1. **Greeting queries** (hello, hi, hey, greetings):
   ```bash
   python3 hello_world_nlq2sparql.py "hello"
   python3 hello_world_nlq2sparql.py "hi there"
   ```
   These will generate a SPARQL query demonstrating how greetings can be processed.

2. **Other queries**:
   ```bash
   python3 hello_world_nlq2sparql.py "what instruments are there"
   ```
   These will show a general response and direct users to more complex examples.

## What It Demonstrates

1. **Basic NLQ Processing**: Simple natural language understanding for greetings
2. **SPARQL Generation**: Automatic generation of appropriate SPARQL queries
3. **RDF Graph Creation**: Creation of simple RDF graphs for demonstration
4. **Query Execution**: Execution of generated SPARQL queries against sample data

## Output

The script provides:
- Natural language response
- Generated SPARQL query (for greeting-type queries)
- Demonstration with sample data execution
- Explanation of the process

## Integration with Existing System

This demonstration is designed to complement the existing research codebase in the `ChineseTraditionalMusicKnowledgeBase/NLQ2SPARQLworkflow/` directory without modifying the existing research implementation.

For more complex NLQ2SPARQL examples involving music knowledge bases, refer to:
- `ChineseTraditionalMusicKnowledgeBase/NLQ2SPARQLworkflow/sampleQuestions/`
- `ChineseTraditionalMusicKnowledgeBase/NLQ2SPARQLworkflow/2_subGraphAssemblyFromOntology_3_SPARQLgeneration.py`

## Requirements

- Python 3.x
- rdflib library (`pip install rdflib`)