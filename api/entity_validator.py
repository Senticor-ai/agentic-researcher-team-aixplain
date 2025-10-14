"""
Entity Validation and Quality Checks

This module validates entities extracted by agents and assigns quality scores
based on source authority, completeness, and data quality.
"""
import logging
import re
from typing import Dict, List, Any, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class EntityValidator:
    """
    Validate entities and assign quality scores
    """
    
    # Authoritative domain patterns for German government and official sources
    AUTHORITATIVE_DOMAINS = [
        r'\.gov$',
        r'\.gov\..*$',
        r'\.bund\.de$',
        r'\.baden-wuerttemberg\.de$',
        r'\.de/.*ministerium',
        r'wikipedia\.org$',
        r'wikidata\.org$',
        r'europa\.eu$',
        r'bundestag\.de$',
        r'bundesrat\.de$',
    ]
    
    # Placeholder/invalid URL patterns
    INVALID_URL_PATTERNS = [
        r'example\.com',
        r'placeholder',
        r'test\.com',
        r'localhost',
        r'127\.0\.0\.1',
        r'dummy',
        r'fake',
    ]
    
    # Minimum quality thresholds
    MIN_DESCRIPTION_LENGTH = 10  # characters
    MIN_NAME_LENGTH = 2  # characters
    MIN_QUALITY_SCORE = 0.3  # entities below this are filtered out
    
    @staticmethod
    def _is_valid_date_format(date_str: str) -> bool:
        """
        Check if date string is in valid ISO 8601 format
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if date is in valid ISO 8601 format, False otherwise
        """
        if not date_str or not isinstance(date_str, str):
            return False
        
        # ISO 8601 patterns: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, YYYY-MM-DDTHH:MM:SSZ, etc.
        iso_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$',  # YYYY-MM-DDTHH:MM:SS
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$',  # YYYY-MM-DDTHH:MM:SSZ
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$',  # With timezone
        ]
        
        for pattern in iso_patterns:
            if re.match(pattern, date_str):
                return True
        
        return False
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Check if URL is valid and not a placeholder
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        url_lower = url.lower()
        
        # Check for invalid patterns
        for pattern in EntityValidator.INVALID_URL_PATTERNS:
            if re.search(pattern, url_lower):
                logger.warning(f"Invalid URL pattern detected: {url}")
                return False
        
        # Check URL structure
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                logger.warning(f"Invalid URL structure: {url}")
                return False
            
            # Must be http or https
            if parsed.scheme not in ['http', 'https']:
                logger.warning(f"Invalid URL scheme: {url}")
                return False
            
            return True
        except Exception as e:
            logger.warning(f"Error parsing URL {url}: {e}")
            return False
    
    @staticmethod
    def is_authoritative_source(url: str) -> bool:
        """
        Check if URL is from an authoritative source
        
        Args:
            url: URL string to check
            
        Returns:
            True if URL is from authoritative source, False otherwise
        """
        if not url:
            return False
        
        url_lower = url.lower()
        
        for pattern in EntityValidator.AUTHORITATIVE_DOMAINS:
            if re.search(pattern, url_lower):
                return True
        
        return False
    
    @staticmethod
    def calculate_quality_score(entity: Dict[str, Any]) -> float:
        """
        Calculate quality score for an entity (0.0 to 1.0)
        
        Scoring factors:
        - Has valid name: 0.2
        - Has description (>= min length): 0.2
        - Has valid sources: 0.2
        - Has authoritative sources: 0.2
        - Has job title (Person) or URL (Organization): 0.1
        - Has temporal info (Event/Policy): 0.1
        - Has location (Event) or identifier (Policy): 0.05
        - Has Wikipedia link: 0.1
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        
        # Check name
        name = entity.get("name", "")
        if name and len(name) >= EntityValidator.MIN_NAME_LENGTH:
            score += 0.2
        
        # Check description
        description = entity.get("description", "")
        if description and len(description) >= EntityValidator.MIN_DESCRIPTION_LENGTH:
            score += 0.2
        
        # Check sources
        sources = entity.get("sources", [])
        if sources and len(sources) > 0:
            valid_sources = [s for s in sources if EntityValidator.is_valid_url(s.get("url", ""))]
            if valid_sources:
                score += 0.2
                
                # Check for authoritative sources
                authoritative_sources = [
                    s for s in valid_sources 
                    if EntityValidator.is_authoritative_source(s.get("url", ""))
                ]
                if authoritative_sources:
                    score += 0.2
        
        # Check entity-specific fields
        entity_type = entity.get("type")
        if entity_type == "Person":
            if entity.get("jobTitle"):
                score += 0.1
        elif entity_type == "Organization":
            if entity.get("url") and EntityValidator.is_valid_url(entity.get("url")):
                score += 0.1
        elif entity_type == "Topic":
            # Topics get bonus for having 'about' field
            if entity.get("about"):
                score += 0.1
        elif entity_type == "Event":
            # Events get bonus for temporal information
            if entity.get("startDate"):
                score += 0.1
            # Additional bonus for location
            if entity.get("location"):
                score += 0.05
        elif entity_type == "Policy":
            # Policies get bonus for temporal information
            if entity.get("legislationDate") or entity.get("dateCreated"):
                score += 0.1
            # Additional bonus for identifier
            if entity.get("legislationIdentifier"):
                score += 0.05
        
        # Check Wikipedia enrichment
        if entity.get("sameAs") or entity.get("wikidata_id"):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    @staticmethod
    def validate_entity(entity: Dict[str, Any]) -> Tuple[bool, List[str], float]:
        """
        Validate an entity and return validation result
        
        Args:
            entity: Entity dictionary to validate
            
        Returns:
            Tuple of (is_valid, list of issues, quality_score)
        """
        issues = []
        
        # Check required fields
        if not entity.get("name"):
            issues.append("Missing required field: name")
        elif len(entity.get("name", "")) < EntityValidator.MIN_NAME_LENGTH:
            issues.append(f"Name too short (minimum {EntityValidator.MIN_NAME_LENGTH} characters)")
        
        if not entity.get("type"):
            issues.append("Missing required field: type")
        elif entity.get("type") not in ["Person", "Organization", "Topic", "Event", "Policy"]:
            issues.append(f"Invalid entity type: {entity.get('type')}")
        
        # Check description
        description = entity.get("description", "")
        if not description:
            issues.append("Missing description")
        elif len(description) < EntityValidator.MIN_DESCRIPTION_LENGTH:
            issues.append(f"Description too short (minimum {EntityValidator.MIN_DESCRIPTION_LENGTH} characters)")
        
        # Check sources
        sources = entity.get("sources", [])
        if not sources or len(sources) == 0:
            issues.append("No sources provided")
        else:
            valid_source_count = 0
            for i, source in enumerate(sources):
                url = source.get("url", "")
                if not url:
                    issues.append(f"Source {i+1}: Missing URL")
                elif not EntityValidator.is_valid_url(url):
                    issues.append(f"Source {i+1}: Invalid or placeholder URL: {url}")
                else:
                    valid_source_count += 1
            
            if valid_source_count == 0:
                issues.append("No valid sources (all URLs are invalid or placeholders)")
        
        # Check Person-specific fields
        if entity.get("type") == "Person":
            if not entity.get("jobTitle"):
                issues.append("Person entity missing jobTitle (recommended)")
        
        # Check Organization-specific fields
        if entity.get("type") == "Organization":
            url = entity.get("url")
            if url and not EntityValidator.is_valid_url(url):
                issues.append(f"Organization URL is invalid: {url}")
        
        # Check Event-specific fields
        if entity.get("type") == "Event":
            if not entity.get("startDate"):
                issues.append("Event entity missing startDate (recommended)")
            else:
                # Validate temporal field format if present
                start_date = entity.get("startDate")
                if not EntityValidator._is_valid_date_format(start_date):
                    issues.append(f"Event startDate has invalid format: {start_date} (expected ISO 8601)")
            
            # Validate endDate if present
            if entity.get("endDate"):
                end_date = entity.get("endDate")
                if not EntityValidator._is_valid_date_format(end_date):
                    issues.append(f"Event endDate has invalid format: {end_date} (expected ISO 8601)")
        
        # Check Policy-specific fields
        if entity.get("type") == "Policy":
            # Policies should have at least one of: identifier or date
            has_identifier = bool(entity.get("legislationIdentifier"))
            has_date = bool(entity.get("legislationDate") or entity.get("dateCreated"))
            
            if not has_identifier and not has_date:
                issues.append("Policy entity missing both legislationIdentifier and dates (at least one recommended)")
            
            # Validate temporal fields if present
            for date_field in ["legislationDate", "dateCreated", "dateModified", "expirationDate"]:
                if entity.get(date_field):
                    date_value = entity.get(date_field)
                    if not EntityValidator._is_valid_date_format(date_value):
                        issues.append(f"Policy {date_field} has invalid format: {date_value} (expected ISO 8601)")
        
        # Calculate quality score
        quality_score = EntityValidator.calculate_quality_score(entity)
        
        # Determine if entity is valid
        is_valid = len(issues) == 0 or (
            # Allow entities with only "recommended" issues if quality is high enough
            quality_score >= EntityValidator.MIN_QUALITY_SCORE and
            not any("Missing required field" in issue or "Invalid" in issue or "No valid sources" in issue 
                   for issue in issues)
        )
        
        return is_valid, issues, quality_score
    
    @staticmethod
    def filter_low_quality_entities(
        entities: List[Dict[str, Any]], 
        min_score: float = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Filter out low-quality entities and return validation metrics
        
        Args:
            entities: List of entity dictionaries
            min_score: Minimum quality score (default: MIN_QUALITY_SCORE)
            
        Returns:
            Tuple of (filtered entities list, validation metrics dict)
        """
        if min_score is None:
            min_score = EntityValidator.MIN_QUALITY_SCORE
        
        filtered_entities = []
        rejected_entities = []
        validation_metrics = {
            "total_entities": len(entities),
            "valid_entities": 0,
            "rejected_entities": 0,
            "rejection_reasons": {},
            "quality_scores": {
                "high": 0,  # >= 0.7
                "medium": 0,  # 0.4 - 0.7
                "low": 0,  # < 0.4
            },
            "avg_quality_score": 0.0
        }
        
        total_score = 0.0
        
        for entity in entities:
            is_valid, issues, quality_score = EntityValidator.validate_entity(entity)
            total_score += quality_score
            
            # Add quality score to entity
            entity["quality_score"] = quality_score
            
            # Categorize quality
            if quality_score >= 0.7:
                validation_metrics["quality_scores"]["high"] += 1
            elif quality_score >= 0.4:
                validation_metrics["quality_scores"]["medium"] += 1
            else:
                validation_metrics["quality_scores"]["low"] += 1
            
            # Filter based on quality score and validation
            if is_valid and quality_score >= min_score:
                filtered_entities.append(entity)
                validation_metrics["valid_entities"] += 1
                logger.info(f"Entity '{entity.get('name')}' passed validation (score: {quality_score:.2f})")
            else:
                rejected_entities.append({
                    "entity": entity,
                    "issues": issues,
                    "quality_score": quality_score
                })
                validation_metrics["rejected_entities"] += 1
                
                # Track rejection reasons
                for issue in issues:
                    validation_metrics["rejection_reasons"][issue] = \
                        validation_metrics["rejection_reasons"].get(issue, 0) + 1
                
                logger.warning(
                    f"Entity '{entity.get('name')}' rejected (score: {quality_score:.2f}): {', '.join(issues)}"
                )
        
        # Calculate average quality score
        if len(entities) > 0:
            validation_metrics["avg_quality_score"] = total_score / len(entities)
        
        logger.info(
            f"Validation complete: {validation_metrics['valid_entities']}/{validation_metrics['total_entities']} "
            f"entities passed (avg score: {validation_metrics['avg_quality_score']:.2f})"
        )
        
        return filtered_entities, validation_metrics
    
    @staticmethod
    def add_quality_indicators(entity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add quality indicators to entity for UI display
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Entity with quality indicators added
        """
        quality_score = entity.get("quality_score", 0.0)
        
        # Add quality badge
        if quality_score >= 0.7:
            entity["quality_badge"] = "high"
        elif quality_score >= 0.4:
            entity["quality_badge"] = "medium"
        else:
            entity["quality_badge"] = "low"
        
        # Add authoritative source indicator
        sources = entity.get("sources", [])
        has_authoritative = any(
            EntityValidator.is_authoritative_source(s.get("url", ""))
            for s in sources
        )
        entity["has_authoritative_source"] = has_authoritative
        
        # Add Wikipedia indicator
        entity["has_wikipedia"] = bool(entity.get("sameAs") or entity.get("wikidata_id"))
        
        return entity
