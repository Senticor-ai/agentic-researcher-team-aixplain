# Requirements Document

## Introduction

This document outlines the requirements for an OSINT (Open Source Intelligence) Agent Team System (codenamed "Honeycomb") designed for the Ministerium für Soziales, Gesundheit und Integration. The system enables policy makers and policy managers to conduct automated web research on specific topics, extract structured information using schema.org entities, and return results in JSON-LD format for backend persistence. The system uses agentic teams (via aixplain.com team agents) that employ MECE (Mutually Exclusive, Collectively Exhaustive) methodology with depth-first search strategy to ensure manageable scope and timely results.

## Requirements

### Requirement 1: Agent Team Management API

**User Story:** As a policy manager, I want to spawn and manage multiple agent teams through an API interface, so that I can run parallel research tasks on different topics.

#### Acceptance Criteria

1. WHEN a user sends a POST request to the API with a topic and research goals THEN the system SHALL create a new agent team instance with a unique identifier
2. WHEN a user requests the list of active agent teams THEN the system SHALL return all running and completed agent teams with their current status
3. WHEN a user sends a request to abort an agent team THEN the system SHALL terminate execution and mark the team as aborted
4. WHEN an agent team completes or reaches interaction limits THEN the system SHALL return the JSON-LD Sachstand with completion status
5. IF the system receives partial results THEN it SHALL be able to issue a new query specifying what is done and what remains

### Requirement 2: Web-Based Monitoring UI

**User Story:** As a policy maker, I want to monitor agent team progress through a web interface, so that I can track research activities and review results in real-time.

#### Acceptance Criteria

1. WHEN a user accesses the monitoring UI THEN the system SHALL display all agent teams with their current status, progress, and metadata
2. WHEN an agent team updates its status THEN the UI SHALL reflect the changes in real-time
3. WHEN a user selects an agent team THEN the system SHALL display detailed information including topic, subtopics covered, entities extracted, and execution logs
4. WHEN a user views the MECE topic graph THEN the system SHALL display nodes showing covered and uncovered research areas
5. WHEN a user clicks on a completed agent team THEN the system SHALL provide access to the generated JSON-LD Sachstand and extracted data

### Requirement 3: OSINT Web Research Capability

**User Story:** As an agent team, I want to conduct comprehensive web research on assigned topics, so that I can gather all publicly available information relevant to the policy domain.

#### Acceptance Criteria

1. WHEN an agent team receives a research topic with goals THEN the system SHALL perform web searches across multiple search engines and sources
2. WHEN the agent team discovers relevant content THEN the system SHALL extract text, metadata, and source references
3. WHEN the agent team encounters large topics THEN the system SHALL apply MECE methodology to divide the topic by people, subject, time, and subtopics
4. WHEN the agent team completes a subtopic THEN the system SHALL update the MECE graph showing coverage status
5. WHEN the agent team finds duplicate information THEN the system SHALL deduplicate and consolidate facts with multiple source references

### Requirement 4: Schema.org Entity Extraction

**User Story:** As an agent team, I want to extract structured entities from gathered information using schema.org vocabulary, so that the data can be integrated into a standardized knowledge graph.

#### Acceptance Criteria

1. WHEN the agent team processes web content THEN the system SHALL identify entities matching schema.org types (Person, Organization, Event, Place, etc.)
2. WHEN an entity is identified THEN the system SHALL extract relevant properties according to schema.org specifications
3. WHEN entity extraction is complete THEN the system SHALL output data in JSON-LD format
4. WHEN multiple sources describe the same entity THEN the system SHALL merge properties and maintain provenance for each fact
5. IF an entity has relationships to other entities THEN the system SHALL represent these relationships using schema.org properties

### Requirement 5: Depth-First MECE Strategy with Interaction Limits

**User Story:** As an agent team, I want to follow a depth-first MECE strategy with interaction limits, so that I can return timely results and allow the system to decide on continuation.

#### Acceptance Criteria

1. WHEN an agent team begins research THEN the system SHALL set a maximum interaction limit before returning results
2. WHEN the interaction limit is reached THEN the system SHALL return current findings with a status indicating remaining work
3. WHEN returning partial results THEN the system SHALL include the MECE graph showing what is completed and what remains uncovered
4. WHEN the system receives partial results THEN it SHALL be able to issue a new query specifying what is done and what is still missing
5. IF a topic is too deep THEN the agent team SHALL prioritize depth-first exploration of one MECE branch before breadth

### Requirement 6: JSON-LD Sachstand Output

**User Story:** As a backend system, I want to receive research results in JSON-LD format, so that I can persist the Sachstand in the knowledge graph store.

#### Acceptance Criteria

1. WHEN an agent team completes research or reaches interaction limit THEN the system SHALL generate a Sachstand in JSON-LD format
2. WHEN generating the JSON-LD THEN the system SHALL include all extracted entities with schema.org types and properties
3. WHEN generating the JSON-LD THEN the system SHALL include facts, relationships, and deep links to all source web resources used
4. WHEN generating the JSON-LD THEN the system SHALL include the MECE coverage graph showing researched and unresearched nodes
5. IF the research is partial THEN the JSON-LD SHALL include metadata indicating completion status and remaining work

### Requirement 7: MECE Topic Decomposition

**User Story:** As an agent team, I want to decompose large topics using MECE methodology, so that I can ensure comprehensive and non-overlapping coverage.

#### Acceptance Criteria

1. WHEN an agent team receives a large topic THEN the system SHALL analyze the topic and propose a MECE decomposition
2. WHEN decomposing a topic THEN the system SHALL create dimensions for people, subjects, time periods, and subtopics
3. WHEN the MECE structure is created THEN the system SHALL generate a graph representation with nodes for each area
4. WHEN the agent team completes research on a node THEN the system SHALL mark it as covered in the graph
5. WHEN returning results THEN the system SHALL include the MECE graph showing which nodes are researched and which remain uncovered

### Requirement 8: Wikipedia Entity Linking

**User Story:** As an agent team, I want to check if extracted entities exist in Wikipedia, so that I can link to authoritative sources and enable deduplication.

#### Acceptance Criteria

1. WHEN an agent team extracts an entity THEN the system SHALL check if the entity has a representation in Wikipedia (any language)
2. WHEN a Wikipedia article is found for an entity THEN the system SHALL capture the Wikipedia URL and language
3. WHEN linking Wikipedia articles THEN the system SHALL include the relationship in the JSON-LD output
4. WHEN multiple language versions exist THEN the system SHALL link all versions to enable cross-language deduplication
5. IF Wikipedia provides Wikidata identifiers THEN the system SHALL include them in the JSON-LD for authoritative graph linking

### Requirement 9: System Evaluation Framework

**User Story:** As a system developer, I want a defined evaluation framework with test examples, so that I can build and validate the agent team system effectively.

#### Acceptance Criteria

1. WHEN building the system THEN we SHALL define a set of representative test topics from the ministry domain (health, social services, integration)
2. WHEN evaluating the system THEN we SHALL measure coverage completeness, entity extraction accuracy, source quality, and Wikipedia linking success
3. WHEN creating test cases THEN we SHALL include topics of varying complexity (simple single-entity, medium multi-entity, complex requiring MECE decomposition)
4. WHEN running evaluations THEN we SHALL compare extracted entities and facts against ground truth datasets
5. IF evaluation metrics fall below thresholds THEN the system SHALL flag the need for agent team prompt or strategy adjustments

