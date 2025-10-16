"""
Tests for validation tools (schema.org validator and URL verifier)

These tests verify the validation tools work correctly with sample entities.
"""
import pytest
from api.schema_org_validator_tool import SchemaOrgValidator, validate_schema_org
from api.url_verifier_tool import URLVerifier, verify_urls


class TestSchemaOrgValidator:
    """Tests for schema.org validator tool"""
    
    def test_valid_person_entity(self):
        """Test validation of a valid Person entity"""
        entity = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Angela Merkel",
            "description": "Former Chancellor of Germany",
            "jobTitle": "Chancellor",
            "sameAs": [
                "https://en.wikipedia.org/wiki/Angela_Merkel",
                "https://www.wikidata.org/wiki/Q567"
            ]
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert result["entity_type"] == "Person"
        assert result["schema_url"] == "https://schema.org"
    
    def test_missing_context(self):
        """Test validation detects missing @context"""
        entity = {
            "@type": "Person",
            "name": "Test Person"
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is False
        assert "Missing @context field" in result["issues"]
        assert result["corrections"]["@context"] == "https://schema.org"
    
    def test_missing_type(self):
        """Test validation detects missing @type"""
        entity = {
            "@context": "https://schema.org",
            "name": "Test Entity"
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is False
        assert "Missing @type field" in result["issues"]
    
    def test_invalid_type(self):
        """Test validation detects invalid @type"""
        entity = {
            "@context": "https://schema.org",
            "@type": "InvalidType",
            "name": "Test Entity"
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is False
        assert any("Invalid @type" in issue for issue in result["issues"])
    
    def test_missing_name(self):
        """Test validation detects missing name"""
        entity = {
            "@context": "https://schema.org",
            "@type": "Person"
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is False
        assert "Missing required property: name" in result["issues"]
    
    def test_invalid_same_as_format(self):
        """Test validation detects invalid sameAs format"""
        entity = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": "Test Person",
            "sameAs": "https://example.com"  # Should be array
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is False
        assert "Property 'sameAs' should be an array of URLs" in result["issues"]
        assert "sameAs" in result["corrections"]
    
    def test_valid_organization_entity(self):
        """Test validation of a valid Organization entity"""
        entity = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Bundesministerium für Umwelt",
            "description": "German Federal Ministry for the Environment",
            "url": "https://www.bmuv.de"
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert result["entity_type"] == "Organization"
    
    def test_valid_event_entity(self):
        """Test validation of a valid Event entity"""
        entity = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": "Climate Summit 2024",
            "description": "International climate conference",
            "startDate": "2024-11-15",
            "location": "Berlin, Germany"
        }
        
        result = validate_schema_org(entity)
        
        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert result["entity_type"] == "Event"
    
    def test_apply_corrections(self):
        """Test applying corrections to an entity"""
        entity = {
            "@type": "Person",
            "name": "Test Person"
        }
        
        corrections = {
            "@context": "https://schema.org"
        }
        
        corrected = SchemaOrgValidator.apply_corrections(entity, corrections)
        
        assert corrected["@context"] == "https://schema.org"
        assert corrected["@type"] == "Person"
        assert corrected["name"] == "Test Person"
    
    def test_type_field_fallback(self):
        """Test that validator can use 'type' field if '@type' is missing"""
        entity = {
            "@context": "https://schema.org",
            "type": "Person",  # Using 'type' instead of '@type'
            "name": "Test Person"
        }
        
        result = validate_schema_org(entity)
        
        # Should suggest correction to use @type
        assert "@type" in result["corrections"]
        assert result["corrections"]["@type"] == "Person"


class TestURLVerifier:
    """Tests for URL verifier tool"""
    
    def test_valid_url_format(self):
        """Test validation of valid URL format"""
        url = "https://www.example.org/page"
        
        is_valid, issue = URLVerifier.is_valid_format(url)
        
        assert is_valid is True
        assert issue == ""
    
    def test_missing_scheme(self):
        """Test detection of missing URL scheme"""
        url = "www.example.com"
        
        is_valid, issue = URLVerifier.is_valid_format(url)
        
        assert is_valid is False
        assert "missing scheme" in issue.lower()
    
    def test_invalid_scheme(self):
        """Test detection of invalid URL scheme"""
        url = "ftp://example.com"
        
        is_valid, issue = URLVerifier.is_valid_format(url)
        
        assert is_valid is False
        assert "scheme" in issue.lower()
    
    def test_placeholder_url(self):
        """Test detection of placeholder URLs"""
        url = "https://example.com/test"
        
        is_valid, issue = URLVerifier.is_valid_format(url)
        
        assert is_valid is False
        assert "invalid pattern" in issue.lower()
    
    def test_localhost_url(self):
        """Test detection of localhost URLs"""
        url = "http://localhost:8000"
        
        is_valid, issue = URLVerifier.is_valid_format(url)
        
        assert is_valid is False
        assert "invalid pattern" in issue.lower()
    
    def test_empty_url(self):
        """Test handling of empty URL"""
        url = ""
        
        is_valid, issue = URLVerifier.is_valid_format(url)
        
        assert is_valid is False
        assert "empty" in issue.lower()
    
    def test_verify_single_url(self):
        """Test verification of a single URL"""
        # Use a reliable URL that should be accessible
        url = "https://www.wikipedia.org"
        
        result = URLVerifier.verify_url(url)
        
        assert result["url"] == url
        assert result["valid"] is True
        # Note: accessibility check may fail in test environment without internet
        # So we just check that the result has the expected structure
        assert "accessible" in result
        assert "status_code" in result
        assert "issue" in result
    
    def test_verify_multiple_urls(self):
        """Test verification of multiple URLs"""
        urls = [
            "https://www.wikipedia.org",
            "https://www.wikidata.org",
            "https://example.com/invalid"  # Invalid pattern
        ]
        
        result = verify_urls(urls)
        
        assert result["total_urls"] == 3
        assert len(result["results"]) == 3
        assert "valid_urls" in result
        assert "accessible_urls" in result
        assert "invalid_urls" in result
        assert "inaccessible_urls" in result
        
        # The example.com URL should be invalid
        example_result = [r for r in result["results"] if "example.com" in r["url"]][0]
        assert example_result["valid"] is False
    
    def test_verify_invalid_format_urls(self):
        """Test verification of URLs with invalid format"""
        urls = [
            "not-a-url",
            "ftp://invalid-scheme.com",
            ""
        ]
        
        result = verify_urls(urls)
        
        assert result["total_urls"] == 3
        assert result["valid_urls"] == 0
        assert result["invalid_urls"] == 3
    
    def test_verify_url_with_invalid_format(self):
        """Test that verify_url handles invalid format correctly"""
        url = "not-a-url"
        
        result = URLVerifier.verify_url(url)
        
        assert result["valid"] is False
        assert result["accessible"] is False
        assert len(result["issue"]) > 0


class TestIntegration:
    """Integration tests for validation tools"""
    
    def test_validate_entity_with_url_verification(self):
        """Test validating an entity and verifying its URLs"""
        entity = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Wikipedia",
            "description": "Free online encyclopedia",
            "url": "https://www.wikipedia.org",
            "sameAs": [
                "https://en.wikipedia.org/wiki/Wikipedia",
                "https://www.wikidata.org/wiki/Q52"
            ]
        }
        
        # Validate schema.org compliance
        schema_result = validate_schema_org(entity)
        assert schema_result["valid"] is True
        
        # Extract and verify URLs
        urls = [entity["url"]] + entity["sameAs"]
        url_result = verify_urls(urls)
        
        assert url_result["total_urls"] == 3
        # All URLs should have valid format
        assert url_result["valid_urls"] >= 1
    
    def test_validate_and_correct_entity(self):
        """Test validating an entity and applying corrections"""
        entity = {
            "type": "Person",  # Missing @context, using 'type' instead of '@type'
            "name": "Test Person",
            "sameAs": "https://www.wikipedia.org"  # Should be array
        }
        
        # Validate
        result = validate_schema_org(entity)
        assert result["valid"] is False
        assert len(result["corrections"]) > 0
        
        # Apply corrections
        corrected = SchemaOrgValidator.apply_corrections(entity, result["corrections"])
        
        # Validate again
        result2 = validate_schema_org(corrected)
        # Should have fewer issues after corrections
        assert len(result2["issues"]) < len(result["issues"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
