#!/usr/bin/env python3
"""
Hello World NLQ2SPARQL Demonstration

This is a simple demonstration script that shows how a basic greeting like "hello" 
could be processed in the context of the linkedmusic-queries NLQ2SPARQL system.

This script demonstrates the concept of converting natural language queries to SPARQL
in the context of music knowledge bases, using a simple greeting as an example.
"""

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import sys
import os

def create_simple_music_graph():
    """
    Create a simple RDF graph with basic music-related data for demonstration.
    """
    g = Graph()
    
    # Define namespaces
    ex = Namespace("http://example.org/music#")
    foaf = Namespace("http://xmlns.com/foaf/0.1/")
    
    # Add some simple music-related triples
    g.add((ex.MusicSystem, RDF.type, ex.System))
    g.add((ex.MusicSystem, RDFS.label, Literal("Music Knowledge Base System")))
    g.add((ex.MusicSystem, foaf.name, Literal("LinkedMusic Query System")))
    
    # Add a greeting concept
    g.add((ex.Greeting, RDF.type, ex.Interaction))
    g.add((ex.Greeting, RDFS.label, Literal("Greeting")))
    g.add((ex.Hello, RDF.type, ex.Greeting))
    g.add((ex.Hello, RDFS.label, Literal("Hello")))
    g.add((ex.Hello, ex.hasResponse, Literal("Hello! Welcome to the LinkedMusic Query System!")))
    
    return g

def process_hello_query(query_text):
    """
    Process a simple hello query and return appropriate response.
    
    Args:
        query_text (str): The natural language query (e.g., "hello")
    
    Returns:
        dict: Contains both natural language response and SPARQL query demonstration
    """
    
    # Simple greeting detection
    query_lower = query_text.lower().strip()
    
    if any(greeting in query_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
        # Create demonstration SPARQL query for greeting
        sparql_query = """
        PREFIX ex: <http://example.org/music#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?greeting ?response WHERE {
            ?greeting a ex:Greeting ;
                     rdfs:label "Hello" ;
                     ex:hasResponse ?response .
        }
        """
        
        # Create response
        response = {
            'natural_language_response': "Hello! Welcome to the LinkedMusic Query System! This system converts natural language queries about music into SPARQL queries.",
            'sparql_query': sparql_query.strip(),
            'explanation': "This demonstrates how a simple greeting 'hello' can be processed into a SPARQL query that searches for greeting-related information in a music knowledge base."
        }
        
        return response
    else:
        return {
            'natural_language_response': f"I received your query: '{query_text}'. This is a demonstration system for NLQ2SPARQL conversion in music knowledge bases.",
            'sparql_query': None,
            'explanation': "For more complex music-related queries, please refer to the sample questions in the sampleQuestions directory."
        }

def main():
    """
    Main function to demonstrate the hello world NLQ2SPARQL functionality.
    """
    print("=" * 60)
    print("Hello World - NLQ2SPARQL Demo for LinkedMusic Queries")
    print("=" * 60)
    print()
    
    # Get query from command line argument or default to "hello"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "hello"
    
    print(f"Processing natural language query: '{query}'")
    print()
    
    # Process the query
    result = process_hello_query(query)
    
    # Display results
    print("NATURAL LANGUAGE RESPONSE:")
    print("-" * 30)
    print(result['natural_language_response'])
    print()
    
    if result['sparql_query']:
        print("CORRESPONDING SPARQL QUERY:")
        print("-" * 30)
        print(result['sparql_query'])
        print()
        
        # Demonstrate execution with sample data
        print("DEMONSTRATION WITH SAMPLE DATA:")
        print("-" * 30)
        g = create_simple_music_graph()
        
        # Execute the query
        results = g.query(result['sparql_query'])
        for row in results:
            print(f"Greeting: {row.greeting}, Response: {row.response}")
        print()
    
    print("EXPLANATION:")
    print("-" * 30)
    print(result['explanation'])
    print()
    
    print("=" * 60)
    print("Demo completed!")
    print("For more complex examples, see the ChineseTraditionalMusicKnowledgeBase/NLQ2SPARQLworkflow/ directory.")
    print("=" * 60)

if __name__ == "__main__":
    main()