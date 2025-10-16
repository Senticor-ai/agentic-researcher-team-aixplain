"""
Schema.org Validator Tool

This module provides a Python function tool for validating entities against schema.org specifications.
Can be registered with aixplain SDK for use by agents.
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SchemaOrgValidator:
    """
    Validates entities against schema.org specifications
    """
    
    # Valid schema.org types
    VALID_TYPES = {
        "Person", "Organization", "GovernmentOrganization", "Topic", "Thing",
        "Event", "ConferenceEvent", "Policy", "Legislation", "CreativeWork",
        "Place", "Action", "Intangible", "Product", "Service"
    }
    
    # Valid properties by type (subset of most common properties)
    VALID_PROPERTIES = {
        "Person": {
            "name", "description", "jobTitle", "url", "sameAs", "wikidata_id",
            "wikipedia_links", "sources", "email", "telephone", "address",
            "worksFor", "alumniOf", "birthDate", "nationality", "image",
            "alternateName", "givenName", "familyName"
        },
        "Organization": {
            "name", "description", "url", "sameAs", "wikidata_id", "wikipedia_links",
            "sources", "email", "telephone", "address", "foundingDate", "founder",
            "parentOrganization", "subOrganization", "member", "location",
            "alternateName", "logo", "slogan"
        },
        "GovernmentOrganization": {
            "name", "description", "url", "sameAs", "wikidata_id", "wikipedia_links",
            "sources", "email", "telephone", "address", "foundingDate", "founder",
            "parentOrganization", "subOrganization", "member", "location",
            "alternateName", "logo", "slogan"
        },
        "Topic": {
            "name", "description", "about", "url", "sameAs", "wikidata_id",
            "wikipedia_links", "sources", "alternateName", "image"
        },
        "Thing": {
            "name", "description", "url", "sameAs", "wikidata_id", "wikipedia_links",
            "sources", "alternateName", "image", "identifier"
        },
        "Event": {
            "name", "description", "startDate", "endDate", "location", "organizer",
            "url", "sameAs", "wikidata_id", "wikipedia_links", "sources",
            "eventStatus", "eventAttendanceMode", "performer", "sponsor",
            "alternateName", "image"
        },
        "ConferenceEvent": {
            "name", "description", "startDate", "endDate", "location", "organizer",
            "url", "sameAs", "wikidata_id", "wikipedia_links", "sources",
            "eventStatus", "eventAttendanceMode", "performer", "sponsor",
            "alternateName", "image", "superEvent", "subEvent"
        },
        "Policy": {
            "name", "description", "legislationIdentifier", "dateCreated",
            "dateModified", "legislationDate", "expirationDate",
            "legislationJurisdiction", "url", "sameAs", "wikidata_id",
            "wikipedia_links", "sources", "alternateName", "legislationType"
        },
        "Legislation": {
            "name", "description", "legislationIdentifier", "dateCreated",
            "dateModified", "legislationDate", "expirationDate",
            "legislationJurisdiction", "url", "sameAs", "wikidata_id",
            "wikipedia_links", "sources", "alternateName", "legislationType"
        }
    }
    
    # Common properties that apply to all types
    COMMON_PROPERTIES = {
        "@context", "@type", "type", "quality_score", "validation_status",
        "validation_issues", "has_authoritative_source", "has_wikipedia",
        "quality_badge"
    }
    
    @staticmethod
    def validate_schema_org(entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate entity against schema.org specifications
        
        Args:
            entity: Entity dictionary to validate
            
        Returns:
            {
                "valid": bool,
                "issues": [list of validation issues],
                "corrections": {dict of suggested corrections},
                "entity_type": str,
                "schema_url": str
            }
        """
        issues = []
        corrections = {}
        
        # Check @context field
        context = entity.get("@context") or entity.get("context")
        if not context:
            issues.append("Missing @context field")
            corrections["@context"] = "https://schema.org"
        elif context != "https://schema.org":
            issues.append(f"Invalid @context: {context} (should be https://schema.org)")
            corrections["@context"] = "https://schema.org"
        
        # Check @type field
        entity_type = entity.get("@type") or entity.get("type")
        if not entity_type:
            issues.append("Missing @type field")
        else:
            # If using 'type' instead of '@type', suggest correction
            if not entity.get("@type") and entity.get("type"):
                corrections["@type"] = entity_type
            
            if entity_type not in SchemaOrgValidator.VALID_TYPES:
                issues.append(f"Invalid @type: {entity_type} (not a recognized schema.org type)")
                # Suggest closest match if possible
                if entity_type.lower() == "person":
                    corrections["@type"] = "Person"
                elif entity_type.lower() == "organization":
                    corrections["@type"] = "Organization"
                elif entity_type.lower() == "event":
                    corrections["@type"] = "Event"
                elif entity_type.lower() == "policy" or entity_type.lower() == "legislation":
                    corrections["@type"] = "Legislation"
        
        # Check required properties
        if not entity.get("name"):
            issues.append("Missing required property: name")
        
        # Check property validity for the entity type
        if entity_type and entity_type in SchemaOrgValidator.VALID_PROPERTIES:
            valid_props = SchemaOrgValidator.VALID_PROPERTIES[entity_type]
            for prop in entity.keys():
                if prop not in valid_props and prop not in SchemaOrgValidator.COMMON_PROPERTIES:
                    issues.append(f"Property '{prop}' is not valid for type {entity_type}")
        
        # Check sameAs property format
        same_as = entity.get("sameAs")
        if same_as:
            if not isinstance(same_as, list):
                issues.append("Property 'sameAs' should be an array of URLs")
                corrections["sameAs"] = [same_as] if isinstance(same_as, str) else []
            else:
                # Validate URLs in sameAs
                for url in same_as:
                    if not isinstance(url, str) or not url.startswith("http"):
                        issues.append(f"Invalid URL in sameAs: {url}")
        
        # Determine if valid
        valid = len(issues) == 0
        
        result = {
            "valid": valid,
            "issues": issues,
            "corrections": corrections,
            "entity_type": entity_type or "Unknown",
            "schema_url": "https://schema.org"
        }
        
        logger.info(
            f"Schema.org validation for '{entity.get('name', 'Unknown')}': "
            f"{'VALID' if valid else 'INVALID'} ({len(issues)} issues)"
        )
        
        return result
    
    @staticmethod
    def apply_corrections(entity: Dict[str, Any], corrections: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply suggested corrections to an entity
        
        Args:
            entity: Entity dictionary
            corrections: Corrections dictionary from validate_schema_org
            
        Returns:
            Corrected entity dictionary
        """
        corrected_entity = entity.copy()
        
        for key, value in corrections.items():
            corrected_entity[key] = value
            logger.info(f"Applied correction: {key} = {value}")
        
        return corrected_entity


def validate_schema_org(entity: dict) -> dict:
    """
    Validate entity against schema.org (accepts dict - for Python use)
    
    Args:
        entity: Entity dictionary to validate
        
    Returns:
        Validation result dictionary
    """
    validator = SchemaOrgValidator()
    return validator.validate(entity)


def validate_schema_org_json(entity_json: str) -> str:
    """
    Validate entity against schema.org (accepts JSON string - for aixplain tool registration)
    
    Validates entity against schema.org specifications
    
    Args:
        entity: Entity JSON object
        
    Returns:
        {
            "valid": bool,
            "issues": [list of validation issues],
            "corrections": {dict of suggested corrections},
            "entity_type": str,
            "schema_url": str
        }
    """
    return SchemaOrgValidator.validate_schema_org(entity)


def validate_schema_org_json(entity_json: str) -> str:
    """
    Validate entity against schema.org (accepts JSON string - for aixplain tool registration)
    
    This function accepts a JSON string and returns a JSON string,
    making it compatible with aixplain utility model registration.
    
    Args:
        entity_json: JSON string representing the entity to validate
        
    Returns:
        JSON string with validation results
        
    Example:
        >>> entity_json = '{"@context": "https://schema.org", "@type": "Person", "name": "John"}'
        >>> result_json = validate_schema_org_json(entity_json)
        >>> result = json.loads(result_json)
        >>> print(result['valid'])
        True
    """
    import json
    
    try:
        # Parse input JSON
        entity = json.loads(entity_json)
        
        # Validate
        validator = SchemaOrgValidator()
        result = validator.validate(entity)
        
        # Return as JSON string
        return json.dumps(result)
        
    except json.JSONDecodeError as e:
        # Return error as JSON
        error_result = {
            "valid": False,
            "issues": [f"Invalid JSON input: {str(e)}"],
            "corrections": {},
            "entity_type": "Unknown",
            "schema_url": "https://schema.org"
        }
        return json.dumps(error_result)
    except Exception as e:
        # Return error as JSON
        error_result = {
            "valid": False,
            "issues": [f"Validation error: {str(e)}"],
            "corrections": {},
            "entity_type": "Unknown",
            "schema_url": "https://schema.org"
        }
        return json.dumps(error_result)
