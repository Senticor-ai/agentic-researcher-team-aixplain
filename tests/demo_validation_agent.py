"""
Demo: Validation Agent with Sample Entities

This script demonstrates the Validation Agent validating sample entities
using the validation tools.
"""
import logging
import json
from api.schema_org_validator_tool import validate_schema_org
from api.url_verifier_tool import verify_urls

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_validation_result(entity_name: str, result: dict):
    """Print validation result in a readable format"""
    print(f"Entity: {entity_name}")
    print(f"Valid: {'✓ YES' if result['valid'] else '✗ NO'}")
    
    if result['issues']:
        print(f"\nIssues found ({len(result['issues'])}):")
        for issue in result['issues']:
            print(f"  - {issue}")
    
    if result['corrections']:
        print(f"\nSuggested corrections:")
        for key, value in result['corrections'].items():
            print(f"  - {key}: {value}")
    
    print()


def print_url_verification_result(urls: list[str], result: dict):
    """Print URL verification result in a readable format"""
    print(f"Total URLs: {result['total_urls']}")
    print(f"Valid format: {result['valid_urls']}/{result['total_urls']}")
    print(f"Accessible: {result['accessible_urls']}/{result['total_urls']}")
    
    if result['invalid_urls'] > 0:
        print(f"\n⚠️  Invalid URLs: {result['invalid_urls']}")
    
    if result['inaccessible_urls'] > 0:
        print(f"⚠️  Inaccessible URLs: {result['inaccessible_urls']}")
    
    print("\nDetailed results:")
    for url_result in result['results']:
        status = "✓" if url_result['accessible'] else "✗"
        print(f"  {status} {url_result['url']}")
        if url_result['issue']:
            print(f"     Issue: {url_result['issue']}")
    
    print()


def demo_validation_agent():
    """Demonstrate Validation Agent capabilities"""
    
    print_section("Validation Agent Demo")
    print("This demo shows how the Validation Agent validates entities")
    print("using Schema.org Validator and URL Verifier tools.")
    
    # Sample entities for validation
    valid_entity = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Dr. Manfred Lucha",
        "jobTitle": "Minister für Soziales, Gesundheit und Integration",
        "description": "Minister in Baden-Württemberg seit 2016",
        "url": "https://sozialministerium.baden-wuerttemberg.de",
        "sameAs": [
            "https://de.wikipedia.org/wiki/Manfred_Lucha",
            "https://www.wikidata.org/wiki/Q1889089"
        ]
    }
    
    invalid_entity = {
        "name": "Test Organization",
        "description": "An organization without proper schema.org structure",
        "url": "https://example.com",
        "sameAs": "https://en.wikipedia.org/wiki/Test"  # Should be array
    }
    
    entity_with_bad_urls = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Test Organization",
        "description": "Organization with invalid URLs",
        "url": "not-a-valid-url",
        "sameAs": [
            "https://example.com",
            "http://localhost:8000",
            "https://placeholder.com"
        ]
    }
    
    # Demo 1: Validate valid entity
    print_section("Demo 1: Validate Valid Entity")
    print("Entity:")
    print(json.dumps(valid_entity, indent=2))
    print("\nValidation Result:")
    result = validate_schema_org(valid_entity)
    print_validation_result(valid_entity['name'], result)
    
    # Demo 2: Validate invalid entity
    print_section("Demo 2: Validate Invalid Entity")
    print("Entity:")
    print(json.dumps(invalid_entity, indent=2))
    print("\nValidation Result:")
    result = validate_schema_org(invalid_entity)
    print_validation_result(invalid_entity['name'], result)
    
    # Demo 3: Verify URLs from valid entity
    print_section("Demo 3: Verify URLs from Valid Entity")
    urls = [valid_entity['url']] + valid_entity['sameAs']
    print("URLs to verify:")
    for url in urls:
        print(f"  - {url}")
    print("\nVerification Result:")
    result = verify_urls(urls)
    print_url_verification_result(urls, result)
    
    # Demo 4: Verify URLs from entity with bad URLs
    print_section("Demo 4: Verify URLs from Entity with Bad URLs")
    urls = [entity_with_bad_urls['url']] + entity_with_bad_urls['sameAs']
    print("URLs to verify:")
    for url in urls:
        print(f"  - {url}")
    print("\nVerification Result:")
    result = verify_urls(urls)
    print_url_verification_result(urls, result)
    
    # Demo 5: Complete validation workflow
    print_section("Demo 5: Complete Validation Workflow")
    print("This simulates what the Validation Agent does:")
    print("1. Validate schema.org compliance")
    print("2. Verify URLs")
    print("3. Calculate quality score")
    print("4. Provide recommendations")
    
    entity = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Bundesagentur für Arbeit",
        "description": "German Federal Employment Agency",
        "url": "https://www.arbeitsagentur.de",
        "sameAs": [
            "https://de.wikipedia.org/wiki/Bundesagentur_f%C3%BCr_Arbeit",
            "https://www.wikidata.org/wiki/Q518155"
        ]
    }
    
    print("\nEntity:")
    print(json.dumps(entity, indent=2))
    
    # Step 1: Schema.org validation
    print("\n--- Step 1: Schema.org Validation ---")
    schema_result = validate_schema_org(entity)
    print(f"Schema.org valid: {'✓ YES' if schema_result['valid'] else '✗ NO'}")
    if schema_result['issues']:
        print(f"Issues: {', '.join(schema_result['issues'])}")
    
    # Step 2: URL verification
    print("\n--- Step 2: URL Verification ---")
    urls = [entity['url']] + entity.get('sameAs', [])
    url_result = verify_urls(urls)
    print(f"URLs accessible: {url_result['accessible_urls']}/{url_result['total_urls']}")
    
    # Step 3: Calculate quality score
    print("\n--- Step 3: Quality Score Calculation ---")
    quality_score = 0.0
    
    # Has valid @context and @type: +0.3
    if schema_result['valid']:
        quality_score += 0.3
        print("✓ Valid schema.org structure: +0.3")
    
    # All properties valid: +0.2
    if not schema_result['issues']:
        quality_score += 0.2
        print("✓ All properties valid: +0.2")
    
    # Has accessible URLs: +0.2
    if url_result['accessible_urls'] > 0:
        quality_score += 0.2
        print(f"✓ Has accessible URLs: +0.2")
    
    # Has Wikipedia/Wikidata links: +0.2
    if entity.get('sameAs'):
        quality_score += 0.2
        print("✓ Has Wikipedia/Wikidata links: +0.2")
    
    # Has detailed description: +0.1
    if entity.get('description') and len(entity['description']) > 20:
        quality_score += 0.1
        print("✓ Has detailed description: +0.1")
    
    print(f"\nFinal Quality Score: {quality_score:.2f}")
    
    # Step 4: Recommendations
    print("\n--- Step 4: Recommendations ---")
    recommendations = []
    
    if not schema_result['valid']:
        recommendations.append("Fix schema.org compliance issues")
    
    if url_result['inaccessible_urls'] > 0:
        recommendations.append(f"Fix {url_result['inaccessible_urls']} inaccessible URLs")
    
    if not entity.get('sameAs'):
        recommendations.append("Add Wikipedia/Wikidata links for better authority")
    
    if quality_score < 0.8:
        recommendations.append("Improve entity quality to reach 0.8+ score")
    
    if recommendations:
        print("Recommendations:")
        for rec in recommendations:
            print(f"  - {rec}")
    else:
        print("✓ Entity meets all quality standards!")
    
    # Summary
    print_section("Summary")
    print("The Validation Agent provides:")
    print("  ✓ Schema.org compliance validation")
    print("  ✓ URL format and accessibility verification")
    print("  ✓ Quality score calculation")
    print("  ✓ Actionable recommendations")
    print("\nThe agent can be called on-demand by other agents or")
    print("proactively scan the entity pool for quality issues.")


if __name__ == "__main__":
    demo_validation_agent()
