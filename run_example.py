"""
Example usage of Financial Detective
This script demonstrates how to use the Financial Detective
"""

import os
import sys
from financial_detective import FinancialDetective

def main():
    """Example usage"""
    
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  No API key found. Please set GROQ_API_KEY or OPENAI_API_KEY environment variable")
        print("\nExample:")
        print("  export GROQ_API_KEY='your-key-here'")
        print("  python run_example.py")
        return
    
    # Determine provider
    provider = "groq" if os.getenv("GROQ_API_KEY") else "openai"
    
    print(f"🔍 Financial Detective Example")
    print(f"Using {provider.upper()} API\n")
    
    # Initialize detector
    try:
        detector = FinancialDetective(api_provider=provider, api_key=api_key)
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        return
    
    # Input file
    input_file = "sample_reliance_report.txt"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file '{input_file}' not found")
        print("Please ensure sample_reliance_report.txt exists")
        return
    
    # Extract knowledge graph
    try:
        print(f"📄 Processing {input_file}...")
        graph_data = detector.extract_knowledge_graph(input_file)
        
        # Save JSON
        output_file = "graph_output.json"
        detector.save_graph_json(graph_data, output_file)
        
        # Generate visualizations
        print("\n📊 Generating visualizations...")
        detector.visualize_graph(graph_data, "graph_visualization.png")
        detector.generate_mermaid_chart(graph_data, "graph_mermaid.md")
        
        # Print summary
        print("\n" + "="*50)
        print("✅ EXTRACTION COMPLETE!")
        print("="*50)
        print(f"📊 Entities extracted: {len(graph_data['entities'])}")
        print(f"🔗 Relationships extracted: {len(graph_data['relationships'])}")
        print(f"\n📁 Output files:")
        print(f"   - {output_file}")
        print(f"   - graph_visualization.png")
        print(f"   - graph_mermaid.md")
        
        # Show sample entities
        print(f"\n📋 Sample Entities:")
        for i, entity in enumerate(graph_data['entities'][:5], 1):
            print(f"   {i}. {entity['name']} ({entity['type']})")
        
        if len(graph_data['entities']) > 5:
            print(f"   ... and {len(graph_data['entities']) - 5} more")
        
        # Show sample relationships
        print(f"\n🔗 Sample Relationships:")
        for i, rel in enumerate(graph_data['relationships'][:5], 1):
            source_name = next((e['name'] for e in graph_data['entities'] if e['id'] == rel['source']), rel['source'])
            target_name = next((e['name'] for e in graph_data['entities'] if e['id'] == rel['target']), rel['target'])
            print(f"   {i}. {source_name} --[{rel['type']}]--> {target_name}")
        
        if len(graph_data['relationships']) > 5:
            print(f"   ... and {len(graph_data['relationships']) - 5} more")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

