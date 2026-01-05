# The Financial Detective 🕵️

Extract entities and relationships from financial documents (like Reliance Annual Reports) using LLM-based extraction. Outputs structured JSON knowledge graphs with visualizations.

## Features

- ✅ **LLM-Based Extraction**: Uses Groq (Llama 3.3 70B) or OpenAI (GPT-4o) - NO regex
- ✅ **Strict JSON Schema**: Validated knowledge graph output
- ✅ **Multiple Visualizations**: NetworkX graphs and Mermaid charts
- ✅ **Entity Types**: Companies, Risk Factors, Dollar Amounts
- ✅ **Relationship Extraction**: Ownership, Financial, Risk, Partnership relationships

## Installation

```bash
# Install dependencies
pip install -r requirements_financial_detective.txt

# Set API key (choose one)
export GROQ_API_KEY="your-groq-api-key"
# OR
export OPENAI_API_KEY="your-openai-api-key"
```

## Usage

### Basic Usage

```bash
python financial_detective.py --input sample_reliance_report.txt --output graph_output.json
```

### With Visualizations

```bash
# Generate NetworkX visualization
python financial_detective.py -i sample_reliance_report.txt -o graph_output.json --visualize

# Generate Mermaid chart
python financial_detective.py -i sample_reliance_report.txt -o graph_output.json --mermaid

# Generate both
python financial_detective.py -i sample_reliance_report.txt -o graph_output.json --visualize --mermaid
```

### Using Different LLM Providers

```bash
# Use Groq (default, faster, free tier available)
python financial_detective.py -i sample_reliance_report.txt -p groq

# Use OpenAI GPT-4o (more accurate, paid)
python financial_detective.py -i sample_reliance_report.txt -p openai
```

### Command Line Options

```
--input, -i          Path to input text file (required)
--output, -o         Output JSON file path (default: graph_output.json)
--provider, -p       LLM provider: groq or openai (default: groq)
--api-key, -k        API key (or set env var)
--visualize, -v      Generate NetworkX visualization
--mermaid, -m        Generate Mermaid chart
```

## Output Format

### JSON Knowledge Graph Schema

```json
{
  "entities": [
    {
      "id": "company_reliance_retail",
      "type": "Company",
      "name": "Reliance Retail",
      "value": null,
      "metadata": {}
    },
    {
      "id": "amount_revenue_2023",
      "type": "Amount",
      "name": "Revenue 2023",
      "value": "$32.5 billion",
      "metadata": {"currency": "USD", "year": 2023}
    },
    {
      "id": "risk_market_volatility",
      "type": "RiskFactor",
      "name": "Market Volatility",
      "value": null,
      "metadata": {}
    }
  ],
  "relationships": [
    {
      "source": "company_reliance_retail",
      "target": "company_hamleys",
      "type": "OWNS",
      "metadata": {"year": 2019}
    },
    {
      "source": "company_reliance_retail",
      "target": "amount_revenue_2023",
      "type": "HAS",
      "metadata": {}
    }
  ]
}
```

### Entity Types

- **Company**: Company names and subsidiaries
- **RiskFactor**: Risk factors mentioned in the document
- **Amount**: Financial figures (revenues, investments, etc.)

### Relationship Types

- **OWNS**: Ownership relationships (e.g., Reliance Retail OWNS Hamleys)
- **HAS**: Financial relationships (e.g., Company HAS Amount)
- **FACES**: Risk relationships (e.g., Company FACES RiskFactor)
- **PARTNERS_WITH**: Partnership relationships (e.g., Jio PARTNERS_WITH Google)

## Visualization

### NetworkX Graph

Generates a PNG file (`graph_visualization.png`) with:
- **Blue nodes**: Companies
- **Red nodes**: Risk Factors
- **Green nodes**: Amounts
- **Edges**: Relationships with labels

### Mermaid Chart

Generates a markdown file (`graph_mermaid.md`) with Mermaid diagram syntax that can be rendered in:
- GitHub/GitLab markdown
- Notion
- Mermaid Live Editor (https://mermaid.live)

## Example Output

After running on `sample_reliance_report.txt`, you'll get:

1. **graph_output.json**: Structured knowledge graph
2. **graph_visualization.png**: NetworkX visualization (if `--visualize` used)
3. **graph_mermaid.md**: Mermaid chart (if `--mermaid` used)

## Requirements

- Python 3.8+
- API key for Groq (free tier available) or OpenAI
- Dependencies listed in `requirements_financial_detective.txt`

## Notes

- The script uses LLM for extraction (no regex) as per requirements
- JSON schema is strictly validated
- Supports both Groq (faster, free tier) and OpenAI (more accurate)
- Handles rate limiting and retries automatically

