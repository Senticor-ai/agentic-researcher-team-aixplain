# Requirements Document

## Introduction

The current OSINT agent team system extracts only Person and Organization entities from search results, missing valuable information about topics, events, policies, and other entity types. Additionally, the system may not be extracting all available entities from search results, particularly from website sources that should at minimum yield an Organization entity. This feature will enhance the entity extraction capabilities to capture a more comprehensive view of the research topic.

## Requirements

### Requirement 1: Extract Additional Entity Types

**User Story:** As a researcher, I want the system to extract multiple entity types beyond just people and organizations, so that I can get a comprehensive understanding of the topic including relevant policies, events, and themes.

#### Acceptance Criteria

1. WHEN the Search Agent processes search results THEN it SHALL extract Topic entities representing themes, subjects, and policy areas mentioned in the sources (e.g., "new guidance on passports and identity cards", "child poverty", "climate policy")
2. WHEN the Search Agent processes search results THEN it SHALL extract Event entities representing conferences, announcements, policy changes, scheduled events, and significant occurrences
3. WHEN an Event entity is extracted THEN it SHALL include temporal information (dates, deadlines, effective dates) when available
4. WHEN a regulation or policy has an effective date THEN the system SHALL extract it as an Event entity with the date and description of what becomes effective
5. WHEN the Search Agent processes search results THEN it SHALL extract Policy entities representing laws, regulations, guidelines, and government programs
6. WHEN a Policy entity is extracted THEN it SHALL include relevant dates (enactment date, effective date, expiration date) when available
7. WHEN entities are extracted THEN each entity SHALL include the same quality metadata (sources, excerpts, descriptions) as Person and Organization entities

### Requirement 2: Ensure Complete Entity Extraction from Search Results

**User Story:** As a researcher, I want every search result to yield at least one entity (particularly the source organization), so that no valuable information is lost during extraction.

#### Acceptance Criteria

1. WHEN a search result comes from a website THEN the system SHALL extract at minimum an Organization entity representing the website owner/publisher
2. WHEN the Search Agent processes top 10 Google search results THEN it SHALL extract entities from each result, not just a subset
3. WHEN a search result contains multiple entities THEN the system SHALL extract all identifiable entities, not just the first one found
4. IF a search result cannot yield any specific entities THEN the system SHALL at minimum extract the source organization as an Organization entity
5. WHEN extraction is complete THEN the system SHALL log statistics showing entities extracted per search result for debugging purposes

### Requirement 3: Update Data Models and Validation

**User Story:** As a developer, I want the data models and validation logic to support the new entity types, so that the system can properly process and validate them.

#### Acceptance Criteria

1. WHEN new entity types are defined THEN the system SHALL create Pydantic models for Topic, Event, and Policy entities following schema.org standards
2. WHEN entities are validated THEN the EntityValidator SHALL apply appropriate quality scoring for all entity types
3. WHEN entities are deduplicated THEN the system SHALL handle deduplication for all entity types using name and type matching
4. WHEN JSON-LD output is generated THEN it SHALL include all entity types in the hasPart array with proper schema.org typing
5. IF an entity type is not recognized THEN the system SHALL log a warning but continue processing other entities

### Requirement 4: Update Agent Instructions

**User Story:** As a system administrator, I want the Search Agent instructions to clearly specify all entity types to extract, so that the agent knows what to look for in search results.

#### Acceptance Criteria

1. WHEN the Search Agent instructions are generated THEN they SHALL include clear definitions and examples for Topic, Event, and Policy entities
2. WHEN the Search Agent instructions are generated THEN they SHALL emphasize extracting entities from every search result
3. WHEN the Search Agent instructions are generated THEN they SHALL include examples showing how to extract organization entities from website sources
4. WHEN the Search Agent processes results THEN it SHALL follow a systematic approach to ensure no search results are skipped
5. WHEN the Search Agent completes extraction THEN it SHALL provide a summary count of entities extracted by type

### Requirement 5: Leverage Wikipedia for Entity Discovery and Validation

**User Story:** As a researcher, I want the system to use Wikipedia to discover additional related entities and validate extracted entities, so that I can get a more complete and accurate picture of the topic.

#### Acceptance Criteria

1. WHEN entities are extracted from search results THEN the Wikipedia Agent SHALL validate each entity by searching Wikipedia
2. WHEN a Wikipedia page is found for an entity THEN the system SHALL extract related entities mentioned on that page, with special emphasis on Topics and Events (people, organizations, topics, events, policies)
3. WHEN a Wikipedia page mentions events with dates THEN the system SHALL extract them as Event entities with temporal information
4. WHEN a Wikipedia page discusses topics or themes THEN the system SHALL extract them as Topic entities with descriptions and relationships
5. WHEN a Wikipedia page contains links to related topics THEN the system SHALL follow those links to discover additional relevant entities, prioritizing topics and events
6. WHEN Wikipedia provides relationship information (e.g., "member of", "part of", "related to", "effective date") THEN the system SHALL use this to discover connected entities
7. WHEN the Wikipedia Agent discovers new entities THEN they SHALL be added to the extraction results with Wikipedia as the source
8. WHEN an entity cannot be validated in Wikipedia THEN the system SHALL retain it but mark it with lower confidence/quality score
9. WHEN Wikipedia provides disambiguation pages THEN the system SHALL select the most relevant option based on the research topic context

### Requirement 6: Maintain Backward Compatibility

**User Story:** As a system user, I want existing functionality for Person and Organization extraction to continue working unchanged, so that current workflows are not disrupted.

#### Acceptance Criteria

1. WHEN Person entities are extracted THEN they SHALL continue to include name, jobTitle, description, and sources as before
2. WHEN Organization entities are extracted THEN they SHALL continue to include name, url, description, and sources as before
3. WHEN existing tests are run THEN they SHALL pass without modification
4. WHEN the UI displays entities THEN it SHALL gracefully handle both old (Person/Organization only) and new (all types) data formats
5. IF the Search Agent returns only Person and Organization entities THEN the system SHALL process them correctly without errors
