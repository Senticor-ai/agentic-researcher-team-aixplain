"""
Demo script for validation tools

This script demonstrates the validation tools working independently with sample entities.
"""
import json
from api.schema_org_validator_tool import validate_schema_org, SchemaOrgValidator
from api.url_verifier_tool import verify_urls


def demo_schema_validator():
    """Demonstrate schema.org validator"""
    print("\n" + "="*80)
    print("SCHEMA.ORG VALIDATOR DEMO")
    print("="*80)
    
    # Test 1: Valid entity
    print("\n1. Testing valid Person entity:")
    valid_entity = {
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
    print(f"Entity: {json.dumps(valid_entity, indent=2)}")
    result = validate_schema_org(valid_entity)
    print(f"\nValidation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Entity Type: {result['entity_type']}")
    
    # Test 2: Entity with issues
    print("\n2. Testing entity with issues:")
    invalid_entity = {
        "type": "Person",  # Missing @context, using 'type' instead of '@type'
        "name": "Test Person",
        "sameAs": "https://www.wikipedia.org"  # Should be array
    }
    print(f"Entity: {json.dumps(invalid_entity, indent=2)}")
    result = validate_schema_org(invalid_entity)
    print(f"\nValidation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Issues: {result['issues']}")
    print(f"  Corrections: {json.dumps(result['corrections'], indent=2)}")
    
    # Test 3: Apply corrections
    print("\n3. Applying corrections:")
    corrected_entity = SchemaOrgValidator.apply_corrections(invalid_entity, result['corrections'])
    print(f"Corrected Entity: {json.dumps(corrected_entity, indent=2)}")
    result2 = validate_schema_org(corrected_entity)
    print(f"\nValidation Result After Corrections:")
    print(f"  Valid: {result2['valid']}")
    print(f"  Issues: {result2['issues']}")


def demo_url_verifier():
    """Demonstrate URL verifier"""
    print("\n" + "="*80)
    print("URL VERIFIER DEMO")
    print("="*80)
    
    # Test URLs
    test_urls = [
        "https://www.wikipedia.org",
        "https://www.wikidata.org",
        "https://www.bundestag.de",
        "https://example.com/invalid",  # Invalid pattern
        "not-a-url",  # Invalid format
        "ftp://invalid-scheme.com",  # Invalid scheme
    ]
    
    print(f"\nTesting {len(test_urls)} URLs:")
    for url in test_urls:
        print(f"  - {url}")
    
    result = verify_urls(test_urls)
    
    print(f"\nVerification Summary:")
    print(f"  Total URLs: {result['total_urls']}")
    print(f"  Valid Format: {result['valid_urls']}")
    print(f"  Accessible: {result['accessible_urls']}")
    print(f"  Invalid Format: {result['invalid_urls']}")
    print(f"  Inaccessible: {result['inaccessible_urls']}")
    
    print(f"\nDetailed Results:")
    for r in result['results']:
        status = "✓" if r['valid'] and r['accessible'] else "✗"
        print(f"  {status} {r['url']}")
        if not r['valid']:
            print(f"      Format Issue: {r['issue']}")
        elif not r['accessible']:
            print(f"      Accessibility Issue: {r['issue']}")
        else:
            print(f"      Status Code: {r['status_code']}")


def demo_integration():
    """Demonstrate integration of both tools"""
    print("\n" + "="*80)
    print("INTEGRATION DEMO")
    print("="*80)
    
    # Entity with URLs to validate
    entity = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Bundesministerium für Umwelt",
        "description": "German Federal Ministry for the Environment",
        "url": "https://www.bmuv.de",
        "sameAs": [
            "https://de.wikipedia.org/wiki/Bundesministerium_für_Umwelt",
            "https://www.wikidata.org/wiki/Q679500"
        ]
    }
    
    print("\nEntity to validate:")
    print(json.dumps(entity, indent=2))
    
    # Step 1: Validate schema.org compliance
    print("\nStep 1: Validating schema.org compliance...")
    schema_result = validate_schema_org(entity)
    print(f"  Schema.org Valid: {schema_result['valid']}")
    if schema_result['issues']:
        print(f"  Issues: {schema_result['issues']}")
    
    # Step 2: Verify URLs
    print("\nStep 2: Verifying URLs...")
    urls = [entity['url']] + entity['sameAs']
    url_result = verify_urls(urls)
    print(f"  Total URLs: {url_result['total_urls']}")
    print(f"  Valid Format: {url_result['valid_urls']}")
    print(f"  Accessible: {url_result['accessible_urls']}")
    
    # Step 3: Overall assessment
    print("\nOverall Assessment:")
    schema_valid = schema_result['valid']
    urls_valid = url_result['valid_urls'] == url_result['total_urls']
    urls_accessible = url_result['accessible_urls'] >= url_result['total_urls'] * 0.9  # 90% threshold
    
    print(f"  Schema.org Compliant: {'✓' if schema_valid else '✗'}")
    print(f"  URLs Valid Format: {'✓' if urls_valid else '✗'}")
    print(f"  URLs Accessible: {'✓' if urls_accessible else '✗'}")
    
    overall_valid = schema_valid and urls_valid and urls_accessible
    print(f"\n  Overall Entity Quality: {'HIGH ✓' if overall_valid else 'NEEDS IMPROVEMENT ✗'}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("VALIDATION TOOLS DEMONSTRATION")
    print("="*80)
    print("\nThis demo shows the schema.org validator and URL verifier tools")
    print("working independently with sample entities.")
    
    demo_schema_validator()
    demo_url_verifier()
    demo_integration()
    
    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print("\nThe validation tools are ready to be registered with aixplain SDK")
    print("and used by agents in the team system.")
    print()
