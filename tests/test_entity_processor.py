"""
Tests for entity processor module

Architecture: Tests verify that we correctly receive and process entities
that the agent has already extracted (not that we extract them ourselves).
"""
import pytest
from datetime import datetime
from api.entity_processor import EntityProcessor


def test_receive_entities_from_agent():
    """Test receiving entities that the agent already extracted"""
    # Mock agent response with entities the agent extracted
    agent_response = {
        "output": """```json
{
  "entities": [
    {
      "type": "Person",
      "name": "Dr. Manfred Lucha",
      "description": "Minister for Social Affairs, Health and Integration",
      "jobTitle": "Minister",
      "url": "https://example.com/lucha",
      "sources": [
        {
          "url": "https://source1.com",
          "excerpt": "Dr. Manfred Lucha is the Minister..."
        }
      ]
    },
    {
      "type": "Organization",
      "name": "Ministry of Social Affairs",
      "description": "Government ministry",
      "url": "https://example.com/ministry",
      "sources": [
        {
          "url": "https://source2.com",
          "excerpt": "The Ministry of Social Affairs..."
        }
      ]
    }
  ]
}
```"""
    }
    
    result = EntityProcessor.receive_entities_from_agent(agent_response)
    
    assert "entities" in result
    assert len(result["entities"]) == 2
    assert result["entities"][0]["type"] == "Person"
    assert result["entities"][0]["name"] == "Dr. Manfred Lucha"
    assert result["entities"][1]["type"] == "Organization"


def test_validate_and_convert_entities():
    """Test entity validation and conversion"""
    entities_data = {
        "entities": [
            {
                "type": "Person",
                "name": "Dr. Manfred Lucha",
                "description": "Minister",
                "jobTitle": "Minister",
                "url": "https://example.com",
                "sources": [
                    {
                        "url": "https://source1.com",
                        "excerpt": "Test excerpt"
                    }
                ]
            }
        ]
    }
    
    result = EntityProcessor.validate_and_convert_entities(entities_data)
    
    assert len(result) == 1
    assert result[0]["type"] == "Person"
    assert result[0]["name"] == "Dr. Manfred Lucha"
    assert len(result[0]["sources"]) == 1


def test_generate_jsonld_sachstand():
    """Test JSON-LD Sachstand generation"""
    topic = "Test Topic"
    entities = [
        {
            "type": "Person",
            "name": "Dr. Manfred Lucha",
            "description": "Minister",
            "jobTitle": "Minister",
            "url": "https://example.com",
            "sources": [
                {
                    "url": "https://source1.com"
                }
            ]
        }
    ]
    
    result = EntityProcessor.generate_jsonld_sachstand(topic, entities, "complete")
    
    assert result["@context"] == "https://schema.org"
    assert result["@type"] == "ResearchReport"
    assert result["name"] == f"Sachstand: {topic}"
    assert result["completionStatus"] == "complete"
    assert len(result["hasPart"]) == 1
    assert result["hasPart"][0]["@type"] == "Person"
    assert result["hasPart"][0]["name"] == "Dr. Manfred Lucha"


def test_process_agent_response():
    """Test complete processing pipeline: receive agent entities and generate JSON-LD"""
    # Agent has already extracted these entities
    agent_response = {
        "output": """```json
{
  "entities": [
    {
      "type": "Person",
      "name": "Test Person",
      "description": "Test description",
      "sources": [
        {
          "url": "https://test.com",
          "excerpt": "Test excerpt"
        }
      ]
    }
  ]
}
```"""
    }
    
    topic = "Test Topic"
    result = EntityProcessor.process_agent_response(agent_response, topic, "complete")
    
    assert result["@context"] == "https://schema.org"
    assert result["@type"] == "ResearchReport"
    assert result["completionStatus"] == "complete"
    assert len(result["hasPart"]) == 1
    assert result["hasPart"][0]["name"] == "Test Person"


def test_receive_entities_no_json():
    """Test handling when agent doesn't return valid JSON"""
    agent_response = {
        "output": "This is just plain text without JSON"
    }
    
    result = EntityProcessor.receive_entities_from_agent(agent_response)
    
    assert "entities" in result
    assert len(result["entities"]) == 0


def test_receive_entities_empty_output():
    """Test handling when agent returns empty output"""
    agent_response = {
        "output": ""
    }
    
    result = EntityProcessor.receive_entities_from_agent(agent_response)
    
    assert "entities" in result
    assert len(result["entities"]) == 0
