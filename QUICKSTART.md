# Quick Start Guide - Financial Detective

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements_financial_detective.txt
```

### 2. Set API Key

**Option A: Groq (Recommended - Free tier available)**
```bash
export GROQ_API_KEY="your-groq-api-key"
```

**Option B: OpenAI GPT-4o**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Run the Script

**Basic usage:**
```bash
python financial_detective.py --input sample_reliance_report.txt
```

**With all visualizations:**
```bash
python financial_detective.py \
  --input sample_reliance_report.txt \
  --output graph_output.json \
  --visualize \
  --mermaid
```

**Or use the example script:**
```bash
python run_example.py
```

## 📋 What You'll Get

After running, you'll have:

1. **graph_output.json** - Structured knowledge graph in JSON format
2. **graph_visualization.png** - NetworkX graph visualization (if `--visualize` used)
3. **graph_mermaid.md** - Mermaid chart (if `--mermaid` used)

## 📊 Example Output Structure

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
      "id": "relationship_owns_hamleys",
      "type": "Relationship",
      "name": "Owns Hamleys",
      "value": "$88 million",
      "metadata": {"year": 2019}
    }
  ],
  "relationships": [
    {
      "source": "company_reliance_retail",
      "target": "company_hamleys",
      "type": "OWNS",
      "metadata": {}
    }
  ]
}
```

## 🎯 Key Features

- ✅ **No Regex**: Uses LLM for intelligent extraction
- ✅ **Strict JSON Schema**: Validated output format
- ✅ **Multiple Visualizations**: NetworkX and Mermaid
- ✅ **Entity Types**: Companies, Risk Factors, Amounts
- ✅ **Relationship Types**: OWNS, HAS, FACES, PARTNERS_WITH

## 🔧 Troubleshooting

**"API key not found"**
- Make sure you've set the environment variable
- Check: `echo $GROQ_API_KEY` (Linux/Mac) or `echo %GROQ_API_KEY%` (Windows)

**"Module not found"**
- Install dependencies: `pip install -r requirements_financial_detective.txt`

**"Input file not found"**
- Make sure `sample_reliance_report.txt` exists in the same directory
- Or provide full path: `--input /path/to/your/file.txt`

## 📝 Custom Input File

You can use any text file as input:

```bash
python financial_detective.py --input your_annual_report.txt --output custom_output.json
```

The script will extract:
- Company names
- Risk factors
- Dollar amounts
- Relationships between entities

