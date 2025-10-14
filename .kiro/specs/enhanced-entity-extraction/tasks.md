# Implementation Plan

- [x] 1. Add new entity type data models
  - Create TopicEntity, EventEntity, and PolicyEntity Pydantic models in api/models.py
  - Follow schema.org standards for field naming
  - Include temporal fields (startDate, endDate, legislationDate, etc.)
  - Add quality_score field to all new models
  - _Requirements: 1.5, 3.1_

- [x] 2. Enhance entity parsing to support new types
  - [x] 2.1 Add parse_topic_entity helper method to EntityProcessor
    - Extract name, description, and sources from TOPIC: sections
    - Handle markdown formatting and field extraction
    - _Requirements: 1.1, 2.3_
  
  - [x] 2.2 Add parse_event_entity helper method to EntityProcessor
    - Extract name, description, dates, location, and sources from EVENT: sections
    - Parse temporal information (startDate, endDate)
    - Handle various date formats
    - _Requirements: 1.2, 1.3, 1.4_
  
  - [x] 2.3 Add parse_policy_entity helper method to EntityProcessor
    - Extract name, description, identifier, dates, jurisdiction, and sources from POLICY: sections
    - Parse temporal information (legislationDate, dateCreated, expirationDate)
    - _Requirements: 1.5, 1.6_
  
  - [x] 2.4 Update parse_text_format method to handle all entity types
    - Add regex patterns for TOPIC:, EVENT:, POLICY: markers
    - Route to appropriate parser based on entity type
    - Log statistics about entity types parsed
    - _Requirements: 1.1, 1.2, 1.5, 2.3_

- [x] 3. Enhance entity validation for new types
  - [x] 3.1 Update validate_entity method in EntityValidator
    - Add validation rules for Topic, Event, Policy types
    - Validate temporal fields when present
    - Check for recommended fields (e.g., Event should have startDate)
    - _Requirements: 3.2, 1.3, 1.6_
  
  - [x] 3.2 Update calculate_quality_score method in EntityValidator
    - Add scoring logic for Event entities (bonus for dates, location)
    - Add scoring logic for Policy entities (bonus for identifier, dates)
    - Add scoring logic for Topic entities
    - _Requirements: 3.2_
  
  - [x] 3.3 Update entity type validation list
    - Add "Topic", "Event", "Policy" to valid entity types
    - Update error messages to include new types
    - _Requirements: 3.1, 3.5_

- [x] 4. Enhance Search Agent instructions for comprehensive extraction
  - [x] 4.1 Add entity type definitions and examples
    - Add TOPIC entity definition with examples
    - Add EVENT entity definition with examples (including temporal info)
    - Add POLICY entity definition with examples (including dates)
    - Provide German and English examples
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 4.1_
  
  - [x] 4.2 Add output format specifications for new types
    - Define TOPIC: output format
    - Define EVENT: output format with Date field
    - Define POLICY: output format with Identifier and Effective Date fields
    - _Requirements: 1.7, 4.2_
  
  - [x] 4.3 Add extraction strategy for complete coverage
    - Emphasize extracting from ALL search results
    - Add minimum entity extraction requirement per result
    - Add guidance for extracting source organization from websites
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.3_
  
  - [x] 4.4 Add feedback mechanism for search effectiveness
    - Instruct agent to report entity counts by type
    - Instruct agent to identify gaps in coverage
    - Provide summary of search effectiveness
    - _Requirements: 4.5_

- [x] 5. Enhance Mentalist instructions for exhaustive research
  - [x] 5.1 Add multi-round search strategy
    - Define Round 1: Direct search strategy
    - Define Round 2: Alternative terms and underrepresented types
    - Define Round 3: Deep dive into specific entities
    - Define Round 4: Wikipedia discovery
    - _Requirements: 2.2, 2.3, 4.2_
  
  - [x] 5.2 Add feedback loop logic
    - Instruct Mentalist to assess coverage after each round
    - Define criteria for identifying underrepresented entity types
    - Provide guidance for selecting next search terms
    - _Requirements: 2.3, 4.4_
  
  - [x] 5.3 Add completion criteria
    - Define when to continue searching (entities < 10, types missing, steps remaining)
    - Define when to stop (steps < 5, comprehensive coverage, duplicates only)
    - Emphasize using full interaction limit
    - _Requirements: 2.2, 2.3, 4.2_
  
  - [x] 5.4 Add search term variation patterns
    - Provide patterns for topic searches
    - Provide patterns for event searches
    - Provide patterns for policy searches
    - Provide patterns for authoritative source searches
    - _Requirements: 2.3, 4.2_

- [ ] 6. Enhance Wikipedia Agent for entity discovery
  - [ ] 6.1 Add entity discovery instructions
    - Instruct agent to scan Wikipedia pages for related entities
    - Emphasize discovering Topics and Events
    - Add guidance for following Wikipedia links (max 2 levels)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 6.2 Add temporal information extraction
    - Instruct agent to extract dates from infoboxes
    - Extract event dates from History/Timeline sections
    - Extract effective dates for policies
    - _Requirements: 5.3, 5.4_
  
  - [ ] 6.3 Add topic discovery instructions
    - Extract topics from category tags
    - Extract topics from "See also" sections
    - Extract topics from section headings
    - _Requirements: 5.2, 5.4, 5.5_
  
  - [ ] 6.4 Update output format for discovered entities
    - Add discovered_entities array to output
    - Include entity_type, name, description, source for each
    - Include discovered_via field to track discovery path
    - _Requirements: 5.5, 5.7_

- [ ] 7. Implement discovered entity merging
  - [ ] 7.1 Add merge_discovered_entities method to EntityProcessor
    - Merge discovered entities from Wikipedia with original entities
    - Check for duplicates by name and type
    - Combine sources when merging duplicates
    - Log statistics about discovered entities
    - _Requirements: 5.5, 5.7_
  
  - [ ] 7.2 Update receive_entities_from_agent to handle discovered entities
    - Extract discovered_entities from Wikipedia Agent output
    - Call merge_discovered_entities to combine with original entities
    - Log counts of original vs discovered entities
    - _Requirements: 5.5, 5.7_

- [ ] 8. Update entity deduplication for new types
  - Update deduplicate_entities method to handle Topic, Event, Policy types
  - Ensure deduplication works with name and type matching for all types
  - Test deduplication with mixed entity types
  - _Requirements: 3.3_

- [ ] 9. Update JSON-LD generation for new types
  - Update generate_jsonld method to include Topic, Event, Policy entities
  - Map new entity types to appropriate schema.org types
  - Include temporal fields in JSON-LD output
  - Test JSON-LD validation with new entity types
  - _Requirements: 3.4_

- [ ] 10. Add progress tracking and monitoring
  - [ ] 10.1 Add progress logging after each search round
    - Log round number, steps used, steps remaining
    - Log entity counts by type
    - Log coverage assessment
    - Log next strategy
    - _Requirements: 2.5_
  
  - [ ] 10.2 Add early warning indicators
    - Log warning if steps < 30 and status = completed
    - Log warning if total entities < 5
    - Log warning if any entity type completely missing
    - Log warning if no new entities in last 2 rounds
    - _Requirements: 2.5_

- [ ] 11. Update UI to display new entity types
  - Update EntitiesDisplay component to handle Topic, Event, Policy
  - Add icons or badges for different entity types
  - Display temporal information for Events and Policies
  - Add filtering by entity type
  - _Requirements: 6.4_

- [ ] 12. Integration testing and validation
  - [ ] 12.1 Test with German government topic
    - Run extraction on Baden-Württemberg policy topic
    - Verify all entity types are extracted
    - Verify temporal information is captured
    - Verify Wikipedia discovery works
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ] 12.2 Test exhaustive research behavior
    - Verify agents use > 45 steps on average
    - Verify multiple search rounds occur
    - Verify feedback loops work
    - Verify agents don't return early
    - _Requirements: 2.2, 2.3, 2.5_
  
  - [ ] 12.3 Test entity extraction completeness
    - Verify average entities per result ≥ 1.5
    - Verify ≥ 90% of results yield entities
    - Verify entity type distribution (≥ 20% Topics, ≥ 10% Events)
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [ ] 12.4 Test backward compatibility
    - Run existing tests to ensure they pass
    - Test with old data format (Person/Organization only)
    - Verify UI handles both old and new formats
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
