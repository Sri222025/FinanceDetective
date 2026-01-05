"""
Test script for Financial Detective
Tests the script without making actual API calls
"""

import json
from financial_detective import FinancialDetective, FinancialDetective as FD

def test_schema_validation():
    """Test JSON schema validation"""
    print("Testing schema validation...")
    
    # Valid data
    valid_data = {
        "entities": [
            {
                "id": "company_1",
                "type": "Company",
                "name": "Reliance Retail",
                "value": None,
                "metadata": {}
            },
            {
                "id": "amount_1",
                "type": "Amount",
                "name": "Revenue",
                "value": "$32.5 billion",
                "metadata": {"currency": "USD"}
            }
        ],
        "relationships": [
            {
                "source": "company_1",
                "target": "amount_1",
                "type": "HAS",
                "metadata": {}
            }
        ]
    }
    
    detector = FD(api_provider="groq", api_key="test_key")
    assert detector._validate_json_schema(valid_data), "Valid schema should pass"
    print("✅ Schema validation test passed")
    
    # Invalid data
    invalid_data = {"entities": []}  # Missing relationships
    assert not detector._validate_json_schema(invalid_data), "Invalid schema should fail"
    print("✅ Invalid schema detection test passed")

def test_prompt_generation():
    """Test prompt building"""
    print("\nTesting prompt generation...")
    detector = FD(api_provider="groq", api_key="test_key")
    prompt = detector._build_extraction_prompt("Test text about Reliance Retail owning Hamleys.")
    
    assert "EXTRACTION REQUIREMENTS" in prompt
    assert "OUTPUT FORMAT" in prompt
    assert "Test text about" in prompt
    print("✅ Prompt generation test passed")

def test_mermaid_generation():
    """Test Mermaid chart generation"""
    print("\nTesting Mermaid chart generation...")
    
    test_data = {
        "entities": [
            {"id": "company_1", "type": "Company", "name": "Reliance Retail", "value": None, "metadata": {}},
            {"id": "company_2", "type": "Company", "name": "Hamleys", "value": None, "metadata": {}}
        ],
        "relationships": [
            {"source": "company_1", "target": "company_2", "type": "OWNS", "metadata": {}}
        ]
    }
    
    detector = FD(api_provider="groq", api_key="test_key")
    detector.generate_mermaid_chart(test_data, "test_mermaid.md")
    
    with open("test_mermaid.md", "r") as f:
        content = f.read()
        assert "graph TD" in content
        assert "Reliance Retail" in content
        assert "OWNS" in content
    
    print("✅ Mermaid chart generation test passed")
    
    # Cleanup
    import os
    if os.path.exists("test_mermaid.md"):
        os.remove("test_mermaid.md")

if __name__ == "__main__":
    print("🧪 Running Financial Detective tests...\n")
    try:
        test_schema_validation()
        test_prompt_generation()
        test_mermaid_generation()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

