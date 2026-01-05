"""
The Financial Detective
Extracts entities and relationships from Reliance Annual Report using LLM
Outputs to JSON Knowledge Graph format
"""

import json
import os
import sys
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

class FinancialDetective:
    """Extract financial entities and relationships using LLM"""
    
    # JSON Schema for Knowledge Graph
    KNOWLEDGE_GRAPH_SCHEMA = {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string", "enum": ["Company", "RiskFactor", "Amount"]},
                        "name": {"type": "string"},
                        "value": {"type": ["string", "number", "null"]},
                        "metadata": {"type": "object"}
                    },
                    "required": ["id", "type", "name"]
                }
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "type": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["source", "target", "type"]
                }
            }
        },
        "required": ["entities", "relationships"]
    }
    
    def __init__(self, api_provider: str = "groq", api_key: Optional[str] = None):
        """
        Initialize Financial Detective
        
        Args:
            api_provider: "groq" or "openai"
            api_key: API key (if None, reads from environment)
        """
        self.api_provider = api_provider.lower()
        
        if api_key:
            self.api_key = api_key
        else:
            if self.api_provider == "groq":
                self.api_key = os.getenv("GROQ_API_KEY")
            elif self.api_provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
            else:
                raise ValueError(f"Unknown API provider: {api_provider}")
        
        if not self.api_key:
            raise ValueError(f"{self.api_provider.upper()}_API_KEY not found in environment")
        
        # Set API endpoints
        if self.api_provider == "groq":
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.3-70b-versatile"
        else:  # openai
            self.api_url = "https://api.openai.com/v1/chat/completions"
            self.model = "gpt-4o"
        
        self.max_retries = 3
    
    def _build_extraction_prompt(self, text: str) -> str:
        """Build prompt for LLM to extract entities and relationships"""
        return f"""You are a financial data extraction expert. Extract entities and relationships from the following text from a Reliance Annual Report.

EXTRACTION REQUIREMENTS:
1. ENTITIES to extract:
   - Company Names: All company names mentioned (e.g., "Reliance Retail", "Jio", "Hamleys")
   - Risk Factors: Any risk factors mentioned (e.g., "Market volatility", "Regulatory changes")
   - Dollar Amounts: Financial figures in USD, INR, or other currencies (e.g., "$1.5 billion", "₹50,000 crores")

2. RELATIONSHIPS to extract:
   - Ownership: "Company A OWNS Company B" (e.g., "Reliance Retail OWNS Hamleys")
   - Financial: "Company HAS Amount" (e.g., "Reliance Retail HAS $2.5 billion revenue")
   - Risk: "Company FACES RiskFactor" (e.g., "Reliance FACES Market volatility")
   - Partnership: "Company PARTNERS_WITH Company" (e.g., "Jio PARTNERS_WITH Google")

OUTPUT FORMAT (strict JSON):
{{
  "entities": [
    {{
      "id": "unique_id_1",
      "type": "Company",
      "name": "Reliance Retail",
      "value": null,
      "metadata": {{}}
    }},
    {{
      "id": "unique_id_2",
      "type": "Amount",
      "name": "Revenue 2023",
      "value": "$2.5 billion",
      "metadata": {{"currency": "USD", "year": 2023}}
    }},
    {{
      "id": "unique_id_3",
      "type": "RiskFactor",
      "name": "Market volatility",
      "value": null,
      "metadata": {{}}
    }}
  ],
  "relationships": [
    {{
      "source": "unique_id_1",
      "target": "unique_id_4",
      "type": "OWNS",
      "metadata": {{"year": 2023}}
    }},
    {{
      "source": "unique_id_1",
      "target": "unique_id_2",
      "type": "HAS",
      "metadata": {{}}
    }}
  ]
}}

RULES:
- Use unique IDs for each entity (e.g., "company_reliance_retail", "amount_revenue_2023")
- Extract ALL company names, risk factors, and dollar amounts mentioned
- Extract ALL relationships between entities
- Ensure JSON is valid and properly formatted
- Do not use regex - use your understanding of the text

TEXT TO ANALYZE:
{text}

Return ONLY the JSON object, no additional text or explanation."""

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API with retry logic"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a financial data extraction expert. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Low temperature for consistent extraction
            "max_tokens": 4000,
            "response_format": {"type": "json_object"} if self.api_provider == "openai" else None
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
                
                if response.status_code == 429:
                    wait_time = (2 ** attempt) * 2
                    print(f"Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code != 200:
                    error_msg = f"API error {response.status_code}: {response.text}"
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise Exception(error_msg)
                
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"]
                
                # Clean up response (remove markdown code blocks if present)
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                return content
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    time.sleep(2 ** attempt)
                    continue
                raise
    
    def _validate_json_schema(self, data: Dict) -> bool:
        """Basic validation of JSON structure"""
        if not isinstance(data, dict):
            return False
        
        if "entities" not in data or "relationships" not in data:
            return False
        
        if not isinstance(data["entities"], list) or not isinstance(data["relationships"], list):
            return False
        
        # Validate entities
        for entity in data["entities"]:
            if not isinstance(entity, dict):
                return False
            if "id" not in entity or "type" not in entity or "name" not in entity:
                return False
            if entity["type"] not in ["Company", "RiskFactor", "Amount"]:
                return False
        
        # Validate relationships
        for rel in data["relationships"]:
            if not isinstance(rel, dict):
                return False
            if "source" not in rel or "target" not in rel or "type" not in rel:
                return False
        
        return True
    
    def extract_knowledge_graph(self, text_file_path: str) -> Dict:
        """
        Extract knowledge graph from text file
        
        Args:
            text_file_path: Path to input text file
            
        Returns:
            Dictionary with entities and relationships
        """
        # Read input file
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"📄 Read {len(text)} characters from {text_file_path}")
        print(f"🤖 Using {self.api_provider.upper()} API with model {self.model}")
        print("🔍 Extracting entities and relationships...")
        
        # Build prompt
        prompt = self._build_extraction_prompt(text)
        
        # Call LLM
        response_text = self._call_llm(prompt)
        
        # Parse JSON
        try:
            graph_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}...")
            raise
        
        # Validate schema
        if not self._validate_json_schema(graph_data):
            print("⚠️ Warning: JSON structure doesn't match expected schema")
            print("Attempting to fix...")
            # Try to fix common issues
            if "entities" not in graph_data:
                graph_data["entities"] = []
            if "relationships" not in graph_data:
                graph_data["relationships"] = []
        
        print(f"✅ Extracted {len(graph_data['entities'])} entities and {len(graph_data['relationships'])} relationships")
        
        return graph_data
    
    def save_graph_json(self, graph_data: Dict, output_path: str = "graph_output.json"):
        """Save knowledge graph to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved knowledge graph to {output_path}")
    
    def visualize_graph(self, graph_data: Dict, output_path: str = "graph_visualization.png"):
        """Create NetworkX visualization of the knowledge graph"""
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes with attributes
        entity_map = {}
        for entity in graph_data["entities"]:
            entity_id = entity["id"]
            entity_map[entity_id] = entity
            node_label = entity["name"]
            if entity.get("value"):
                node_label += f"\n({entity['value']})"
            
            G.add_node(entity_id, 
                      label=node_label,
                      type=entity["type"],
                      name=entity["name"])
        
        # Add edges
        for rel in graph_data["relationships"]:
            source = rel["source"]
            target = rel["target"]
            if source in entity_map and target in entity_map:
                G.add_edge(source, target, 
                          type=rel["type"],
                          label=rel["type"])
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Color nodes by type
        node_colors = []
        for node_id in G.nodes():
            entity_type = G.nodes[node_id]["type"]
            if entity_type == "Company":
                node_colors.append("#4A90E2")  # Blue
            elif entity_type == "RiskFactor":
                node_colors.append("#E24A4A")  # Red
            elif entity_type == "Amount":
                node_colors.append("#4AE24A")  # Green
            else:
                node_colors.append("#E2E24A")  # Yellow
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=2000,
                              alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos,
                               edge_color='gray',
                               arrows=True,
                               arrowsize=20,
                               alpha=0.6,
                               connectionstyle='arc3,rad=0.1')
        
        # Draw labels
        labels = {node_id: G.nodes[node_id]["name"][:20] for node_id in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        # Draw edge labels
        edge_labels = {(u, v): G[u][v]["label"] for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7)
        
        plt.title("Financial Knowledge Graph\n(Blue=Company, Red=Risk, Green=Amount)", 
                 fontsize=16, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"📊 Saved visualization to {output_path}")
        plt.close()
    
    def generate_mermaid_chart(self, graph_data: Dict, output_path: str = "graph_mermaid.md"):
        """Generate Mermaid chart representation"""
        mermaid_lines = ["graph TD"]
        
        # Add nodes
        for entity in graph_data["entities"]:
            entity_id = entity["id"].replace(" ", "_").replace("-", "_")
            name = entity["name"]
            entity_type = entity["type"]
            
            # Style based on type
            if entity_type == "Company":
                style = "fill:#4A90E2,stroke:#333,stroke-width:2px"
            elif entity_type == "RiskFactor":
                style = "fill:#E24A4A,stroke:#333,stroke-width:2px"
            elif entity_type == "Amount":
                style = "fill:#4AE24A,stroke:#333,stroke-width:2px"
            else:
                style = "fill:#E2E24A,stroke:#333,stroke-width:2px"
            
            mermaid_lines.append(f'    {entity_id}["{name}"]')
            mermaid_lines.append(f'    style {entity_id} {style}')
        
        # Add edges
        for rel in graph_data["relationships"]:
            source = rel["source"].replace(" ", "_").replace("-", "_")
            target = rel["target"].replace(" ", "_").replace("-", "_")
            rel_type = rel["type"]
            mermaid_lines.append(f'    {source} -->|{rel_type}| {target}')
        
        mermaid_content = "\n".join(mermaid_lines)
        
        # Wrap in markdown code block
        full_content = f"""# Financial Knowledge Graph (Mermaid)

```mermaid
{mermaid_content}
```

## Entities
{len(graph_data['entities'])} entities extracted

## Relationships
{len(graph_data['relationships'])} relationships extracted
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"📈 Saved Mermaid chart to {output_path}")


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Financial Detective - Extract knowledge graph from annual report")
    parser.add_argument("--input", "-i", required=True, help="Path to input text file")
    parser.add_argument("--output", "-o", default="graph_output.json", help="Output JSON file path")
    parser.add_argument("--provider", "-p", choices=["groq", "openai"], default="groq", 
                       help="LLM provider (groq or openai)")
    parser.add_argument("--api-key", "-k", help="API key (or set GROQ_API_KEY/OPENAI_API_KEY env var)")
    parser.add_argument("--visualize", "-v", action="store_true", help="Generate NetworkX visualization")
    parser.add_argument("--mermaid", "-m", action="store_true", help="Generate Mermaid chart")
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    # Initialize detector
    try:
        detector = FinancialDetective(api_provider=args.provider, api_key=args.api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Extract knowledge graph
    try:
        graph_data = detector.extract_knowledge_graph(args.input)
        
        # Save JSON
        detector.save_graph_json(graph_data, args.output)
        
        # Generate visualizations if requested
        if args.visualize:
            detector.visualize_graph(graph_data, "graph_visualization.png")
        
        if args.mermaid:
            detector.generate_mermaid_chart(graph_data, "graph_mermaid.md")
        
        print("\n✅ Extraction complete!")
        print(f"   Entities: {len(graph_data['entities'])}")
        print(f"   Relationships: {len(graph_data['relationships'])}")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

