# Validation Tools

This directory contains Python validation tools for schema.org validation and URL verification. These tools can be registered with the aixplain SDK and used by agents in the team system.

## Overview

The validation tools provide two key capabilities:

1. **Schema.org Validator**: Validates entities against schema.org specifications
2. **URL Verifier**: Verifies URLs are valid and accessible

## Files

- `schema_org_validator_tool.py` - Schema.org validation tool
- `url_verifier_tool.py` - URL verification tool
- `register_validation_tools.py` - Tool registration with aixplain SDK

## Schema.org Validator

### Features

- Validates `@context` field points to "https://schema.org"
- Validates `@type` is a recognized schema.org type
- Validates properties are valid for the entity type
- Validates `sameAs` property format (should be array of URLs)
- Provides suggested corrections for common issues

### Supported Types

- Person
- Organization
- GovernmentOrganization
- Topic
- Thing
- Event
- ConferenceEvent
- Policy
- Legislation
- CreativeWork
- Place
- Action
- Intangible
- Product
- Service

### Usage

```python
from api.schema_org_validator_tool import validate_schema_org

entity = {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Angela Merkel",
    "description": "Former Chancellor of Germany"
}

result = validate_schema_org(entity)
# Returns:
# {
#     "valid": True,
#     "issues": [],
#     "corrections": {},
#     "entity_type": "Person",
#     "schema_url": "https://schema.org"
# }
```

### Applying Corrections

```python
from api.schema_org_validator_tool import SchemaOrgValidator

entity = {
    "type": "Person",  # Missing @context
    "name": "Test Person"
}

result = validate_schema_org(entity)
corrected = SchemaOrgValidator.apply_corrections(entity, result['corrections'])
# Corrected entity now has @context and @type fields
```

## URL Verifier

### Features

- Validates URL format (scheme, domain, path)
- Checks for invalid patterns (example.com, localhost, etc.)
- Verifies URL accessibility via HTTP HEAD request
- Returns status codes and detailed error messages
- Handles timeouts and network errors gracefully

### Usage

```python
from api.url_verifier_tool import verify_urls

urls = [
    "https://www.wikipedia.org",
    "https://www.wikidata.org",
    "https://example.com/invalid"  # Invalid pattern
]

result = verify_urls(urls)
# Returns:
# {
#     "total_urls": 3,
#     "valid_urls": 2,
#     "accessible_urls": 2,
#     "invalid_urls": 1,
#     "inaccessible_urls": 0,
#     "results": [
#         {
#             "url": "https://www.wikipedia.org",
#             "valid": True,
#             "accessible": True,
#             "status_code": 200,
#             "issue": ""
#         },
#         ...
#     ]
# }
```

### Invalid URL Patterns

The URL verifier detects and rejects:

- example.com domains
- placeholder URLs
- test.com domains
- localhost URLs
- 127.0.0.1 addresses
- dummy/fake URLs

### Timeout Configuration

- Default timeout: 5 seconds per URL
- Configurable via `URLVerifier.REQUEST_TIMEOUT`

## Tool Registration

### Registering with aixplain SDK

```python
from api.register_validation_tools import register_validation_tools

# Register both tools
schema_validator_id, url_verifier_id = register_validation_tools()

print(f"Schema Validator Tool ID: {schema_validator_id}")
print(f"URL Verifier Tool ID: {url_verifier_id}")
```

### Using Registered Tools with Agents

```python
from aixplain.factories import AgentFactory
from api.register_validation_tools import ValidationToolRegistry

# Register tools first
ValidationToolRegistry.register_all_tools()

# Get tool IDs
schema_tool_id = ValidationToolRegistry.SCHEMA_VALIDATOR_TOOL_ID
url_tool_id = ValidationToolRegistry.URL_VERIFIER_TOOL_ID

# Create agent with validation tools
agent = AgentFactory.create(
    name="Validation Agent",
    role="Quality Checker",
    tools=[schema_tool_id, url_tool_id],
    instructions="Validate entities for schema.org compliance and URL accessibility"
)
```

## Testing

### Run Unit Tests

```bash
python -m pytest tests/test_validation_tools.py -v
```

### Run Demo

```bash
PYTHONPATH=. python tests/demo_validation_tools.py
```

The demo script demonstrates:
1. Schema.org validation with valid and invalid entities
2. URL verification with various URL formats
3. Integration of both tools for complete entity validation

## Integration with Agent Team System

These tools are designed to be used by agents in the team system:

1. **Validation Agent**: Uses both tools to validate entities on-demand and proactively
2. **Search Agent**: Calls URL Verifier to validate sources immediately after discovery
3. **Wikipedia Agent**: Calls Schema.org Validator to ensure enrichment is compliant
4. **Orchestrator**: Uses tools to validate entity pool and broadcast issues

See the design document at `.kiro/specs/schema-org-validation-and-enrichment/design.md` for details on the hive mind architecture.

## Error Handling

Both tools handle errors gracefully:

- **Schema.org Validator**: Returns validation issues and suggested corrections
- **URL Verifier**: Returns detailed error messages for format and accessibility issues
- **Network Errors**: Caught and reported with descriptive messages
- **Timeouts**: Handled with configurable timeout settings

## Performance Considerations

- **URL Verification**: Uses HTTP HEAD requests to minimize data transfer
- **Timeout**: 5 second timeout per URL prevents blocking
- **Parallel Verification**: Can verify multiple URLs in a single call
- **Caching**: Schema.org type definitions can be cached (future enhancement)

## Future Enhancements

- [ ] Cache schema.org type definitions
- [ ] Batch URL verification with parallel requests
- [ ] Support for custom schema.org types
- [ ] Validation metrics tracking
- [ ] Integration with entity processor for automatic validation
