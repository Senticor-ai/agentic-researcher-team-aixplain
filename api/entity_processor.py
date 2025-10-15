"""
Entity processing and JSON-LD generation

This module receives entities extracted by agents and generates
JSON-LD Sachstand output in schema.org format.

Architecture principle: API invokes, monitors, stores - agents do the extraction work.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple

from api.models import PersonEntity, OrganizationEntity, TopicEntity, EventEntity, PolicyEntity, EntitySource
from api.entity_validator import EntityValidator

logger = logging.getLogger(__name__)


class EntityProcessor:
    """
    Process agent-extracted entities and generate JSON-LD output
    
    Note: This class does NOT extract entities - that's the agent's job.
    It only validates and formats what the agent already extracted.
    """
    
    @staticmethod
    def merge_wikipedia_data(entities_data: Dict[str, Any], wikipedia_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge Wikipedia enrichment data into entities
        
        Args:
            entities_data: Dictionary with entities from Search Agent
            wikipedia_data: Dictionary mapping entity names to Wikipedia data
            
        Returns:
            Entities data with Wikipedia enrichment merged in
        """
        if not wikipedia_data:
            return entities_data
        
        # Merge Wikipedia data into each entity
        for entity in entities_data.get("entities", []):
            entity_name = entity.get("name")
            if entity_name and entity_name in wikipedia_data:
                wiki_info = wikipedia_data[entity_name]
                
                # Add Wikipedia links
                if wiki_info.get("wikipedia_links"):
                    entity["wikipedia_links"] = wiki_info["wikipedia_links"]
                
                # Add Wikidata ID
                if wiki_info.get("wikidata_id"):
                    entity["wikidata_id"] = wiki_info["wikidata_id"]
                
                # Add sameAs property
                if wiki_info.get("sameAs"):
                    entity["sameAs"] = wiki_info["sameAs"]
                
                logger.info(f"Enriched entity '{entity_name}' with Wikipedia data")
        
        return entities_data
    
    @staticmethod
    def extract_mece_graph(agent_response: dict) -> Optional[Dict[str, Any]]:
        """
        Extract MECE decomposition graph from Mentalist output
        
        Args:
            agent_response: Response from aixplain agent
            
        Returns:
            MECE graph dictionary or None if not found
        """
        mece_graph = None
        
        try:
            # Check intermediate steps for Mentalist output
            if "data" in agent_response and "intermediate_steps" in agent_response["data"]:
                intermediate_steps = agent_response["data"]["intermediate_steps"]
                
                # Look for Mentalist output with MECE decomposition
                for step in intermediate_steps:
                    agent_name = step.get("agent", "").lower()
                    if "mentalist" in agent_name:
                        output = step.get("output", "")
                        logger.info(f"Found Mentalist output, checking for MECE graph")
                        
                        # Try to extract MECE graph from output
                        if isinstance(output, dict) and "mece_decomposition" in output:
                            mece_graph = output["mece_decomposition"]
                            logger.info("Found MECE decomposition in Mentalist dict output")
                        elif isinstance(output, str):
                            # Try to find JSON with mece_decomposition
                            import re
                            # Look for mece_decomposition JSON object
                            mece_match = re.search(
                                r'"mece_decomposition"\s*:\s*(\{[^}]*(?:\{[^}]*\}[^}]*)*\})',
                                output,
                                re.DOTALL
                            )
                            if mece_match:
                                try:
                                    # Extract the full JSON object containing mece_decomposition
                                    json_match = re.search(
                                        r'\{[^{}]*"mece_decomposition"[^{}]*\{.*?\}[^{}]*\}',
                                        output,
                                        re.DOTALL
                                    )
                                    if json_match:
                                        parsed = json.loads(json_match.group(0))
                                        mece_graph = parsed.get("mece_decomposition")
                                        logger.info("Extracted MECE graph from Mentalist string output")
                                except json.JSONDecodeError as e:
                                    logger.info(f"Failed to parse MECE graph JSON: {e}")
            
            # Also check the main output for MECE information
            if not mece_graph:
                output_data = agent_response.get("output", "")
                if isinstance(output_data, dict) and "mece_decomposition" in output_data:
                    mece_graph = output_data["mece_decomposition"]
                    logger.info("Found MECE decomposition in main output")
                elif isinstance(output_data, str) and "mece_decomposition" in output_data:
                    # Try to extract from string
                    import re
                    json_match = re.search(
                        r'\{[^{}]*"mece_decomposition"[^{}]*\{.*?\}[^{}]*\}',
                        output_data,
                        re.DOTALL
                    )
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group(0))
                            mece_graph = parsed.get("mece_decomposition")
                            logger.info("Extracted MECE graph from main output string")
                        except json.JSONDecodeError:
                            pass
            
            if mece_graph:
                logger.info(f"MECE graph extracted: {mece_graph.get('applied', False)} applied, "
                          f"{len(mece_graph.get('nodes', []))} nodes")
            else:
                logger.info("No MECE decomposition found in agent response")
        
        except Exception as e:
            logger.error(f"Error extracting MECE graph: {e}")
        
        return mece_graph
    
    @staticmethod
    def extract_wikipedia_enrichment(agent_response: dict) -> Dict[str, Any]:
        """
        Extract Wikipedia enrichment data from Wikipedia Agent output
        
        Args:
            agent_response: Response from aixplain agent
            
        Returns:
            Dictionary mapping entity names to Wikipedia enrichment data
        """
        wikipedia_data = {}
        
        try:
            if "data" in agent_response and "intermediate_steps" in agent_response["data"]:
                intermediate_steps = agent_response["data"]["intermediate_steps"]
                
                # Look for Wikipedia Agent output
                for step in intermediate_steps:
                    if step.get("agent") == "Wikipedia Agent":
                        wiki_output = step.get("output")
                        logger.info(f"Found Wikipedia Agent output: {type(wiki_output)}")
                        
                        # Parse Wikipedia output
                        enrichment = None
                        if isinstance(wiki_output, dict):
                            enrichment = wiki_output
                        elif isinstance(wiki_output, str):
                            # Try to parse as JSON
                            try:
                                enrichment = json.loads(wiki_output)
                            except json.JSONDecodeError:
                                # Try Python literal eval
                                try:
                                    import ast
                                    enrichment = ast.literal_eval(wiki_output)
                                except (ValueError, SyntaxError):
                                    logger.warning("Could not parse Wikipedia Agent output")
                        
                        # Extract enriched entities
                        if enrichment and "enriched_entities" in enrichment:
                            for entity in enrichment["enriched_entities"]:
                                entity_name = entity.get("entity_name")
                                if entity_name:
                                    wikipedia_data[entity_name] = {
                                        "wikipedia_links": entity.get("wikipedia_links", []),
                                        "wikidata_id": entity.get("wikidata_id"),
                                        "sameAs": entity.get("sameAs", [])
                                    }
                            logger.info(f"Extracted Wikipedia data for {len(wikipedia_data)} entities")
        
        except Exception as e:
            logger.error(f"Error extracting Wikipedia enrichment: {e}")
        
        return wikipedia_data
    
    @staticmethod
    def receive_entities_from_agent(agent_response: dict) -> Dict[str, Any]:
        """
        Receive entities that the agent already extracted
        
        The agent (using tools like Docling) has already done the extraction work.
        We just receive and validate the structured output.
        
        Args:
            agent_response: Response from aixplain agent containing extracted entities
            
        Returns:
            Dictionary with entities extracted by the agent and Wikipedia enrichment
        """
        try:
            # Extract Wikipedia enrichment data first
            wikipedia_data = EntityProcessor.extract_wikipedia_enrichment(agent_response)
            
            # For team agents, check intermediate_steps for Search Agent output
            # The Response Generator reformats the output as markdown, so we need
            # to get the raw output from the Search Agent
            # Check both locations: root level and under "data"
            intermediate_steps = None
            if "intermediate_steps" in agent_response:
                intermediate_steps = agent_response["intermediate_steps"]
            elif "data" in agent_response and "intermediate_steps" in agent_response["data"]:
                intermediate_steps = agent_response["data"]["intermediate_steps"]
            
            if intermediate_steps:
                logger.info(f"Found {len(intermediate_steps)} intermediate steps")
                
                # Log all agent names to help debug
                agent_names = [step.get("agent", "unknown") for step in intermediate_steps]
                logger.info(f"Agent names in steps: {agent_names}")
                
                # Look for Search Agent output (try multiple possible names)
                search_agent_names = ["Search Agent", "search_agent", "SearchAgent", "search"]
                for step in intermediate_steps:
                    agent_name = step.get("agent", "")
                    if any(name.lower() in agent_name.lower() for name in search_agent_names):
                        search_output = step.get("output")
                        logger.info(f"Found Search Agent output from '{agent_name}': {type(search_output)}")
                        
                        if isinstance(search_output, dict) and "entities" in search_output:
                            logger.info(f"Search Agent returned {len(search_output['entities'])} entities")
                            # Merge Wikipedia data into entities
                            entities_with_wiki = EntityProcessor.merge_wikipedia_data(
                                search_output, wikipedia_data
                            )
                            return entities_with_wiki
                        elif isinstance(search_output, str):
                            # Try to parse as JSON first
                            try:
                                parsed = json.loads(search_output)
                                
                                # Check if entities are in standard format
                                if isinstance(parsed, dict) and "entities" in parsed:
                                    logger.info(f"Parsed Search Agent output as JSON: {len(parsed['entities'])} entities")
                                    # Merge Wikipedia data
                                    entities_with_wiki = EntityProcessor.merge_wikipedia_data(
                                        parsed, wikipedia_data
                                    )
                                    return entities_with_wiki
                                
                                # Check if entities are grouped by type (e.g., "Person Entities", "Organization Entities")
                                elif isinstance(parsed, dict) and any(key.endswith(" Entities") for key in parsed.keys()):
                                    logger.info("Found grouped entity format, converting to standard format")
                                    converted = EntityProcessor.convert_grouped_entities(parsed)
                                    logger.info(f"Converted {len(converted['entities'])} entities from grouped format")
                                    # Merge Wikipedia data
                                    entities_with_wiki = EntityProcessor.merge_wikipedia_data(
                                        converted, wikipedia_data
                                    )
                                    return entities_with_wiki
                                    
                            except json.JSONDecodeError:
                                logger.info("Search Agent output is not valid JSON, trying ast.literal_eval")
                            
                            # Try Python literal eval (handles dict strings with single quotes)
                            try:
                                import ast
                                parsed = ast.literal_eval(search_output)
                                if isinstance(parsed, dict) and "entities" in parsed:
                                    logger.info(f"Parsed Search Agent output as Python dict: {len(parsed['entities'])} entities")
                                    # Merge Wikipedia data
                                    entities_with_wiki = EntityProcessor.merge_wikipedia_data(
                                        parsed, wikipedia_data
                                    )
                                    return entities_with_wiki
                            except (ValueError, SyntaxError) as e:
                                logger.info(f"Could not parse Search Agent output: {e}")
                            
                            # Try text format parser (new format)
                            logger.info("Attempting to parse Search Agent output as text format")
                            parsed = EntityProcessor.parse_text_format(search_output)
                            if parsed and parsed.get("entities"):
                                logger.info(f"Parsed Search Agent output as text format: {len(parsed['entities'])} entities")
                                # Merge Wikipedia data
                                entities_with_wiki = EntityProcessor.merge_wikipedia_data(
                                    parsed, wikipedia_data
                                )
                                return entities_with_wiki
            
            # Fallback to original logic
            # The agent should return structured entities in its output
            # For walking skeleton: agent returns data in "output" field
            # For full system: Inspector aggregates from shared memory
            output_data = agent_response.get("output", "")
            
            logger.info(f"Received agent output type: {type(output_data)}")
            
            if not output_data:
                logger.warning("No output from agent")
                return {"entities": []}
            
            # Check if output is already a dict (parsed data from agent)
            if isinstance(output_data, dict):
                logger.info("Agent returned structured dict")
                logger.info(f"Dict keys: {list(output_data.keys())}")
                entities_data = output_data
            elif isinstance(output_data, str):
                # Output is a string, need to parse it
                output_text = output_data.strip()
                logger.info(f"Agent output (first 300 chars): {output_text[:300]}")
                
                # Check if output is an error message
                if "error occurred" in output_text.lower() or "contact your administrator" in output_text.lower():
                    logger.error(f"Agent returned error: {output_text}")
                    logger.error("This might be due to:")
                    logger.error("  - Tool configuration issues (Tavily Search not accessible)")
                    logger.error("  - API key permissions")
                    logger.error("  - Team agent configuration conflicts")
                    return {"entities": []}
                
                # Try multiple parsing strategies
                entities_data = None
                
                # Strategy 1: Direct JSON parse
                try:
                    entities_data = json.loads(output_text)
                    logger.info("Successfully parsed as direct JSON")
                except json.JSONDecodeError as e:
                    logger.info(f"Direct JSON parse failed: {e}")
                
                # Strategy 2: Extract from markdown code blocks
                if entities_data is None:
                    import re
                    # Try ```json blocks
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', output_text, re.DOTALL)
                    if json_match:
                        try:
                            entities_data = json.loads(json_match.group(1))
                            logger.info("Successfully parsed JSON from markdown code block")
                        except json.JSONDecodeError:
                            logger.info("Failed to parse JSON from markdown code block")
                
                # Strategy 3: Find JSON object anywhere in text
                if entities_data is None:
                    import re
                    # Look for { ... } with "entities" key
                    json_match = re.search(r'\{[^{}]*"entities"[^{}]*\[[^\]]*\][^{}]*\}', output_text, re.DOTALL)
                    if not json_match:
                        # Try more permissive pattern
                        json_match = re.search(r'\{.*?"entities".*?\}', output_text, re.DOTALL)
                    
                    if json_match:
                        try:
                            entities_data = json.loads(json_match.group(0))
                            logger.info("Successfully extracted JSON object from text")
                        except json.JSONDecodeError:
                            logger.info("Failed to parse extracted JSON object")
                
                # Strategy 4: Try Python literal eval (handles single quotes)
                if entities_data is None:
                    try:
                        import ast
                        entities_data = ast.literal_eval(output_text)
                        if isinstance(entities_data, dict):
                            logger.info("Successfully parsed as Python dict literal")
                        else:
                            logger.info("Python literal eval returned non-dict")
                            entities_data = None
                    except (ValueError, SyntaxError) as e:
                        logger.info(f"Python literal eval failed: {e}")
                
                # Strategy 5: Parse structured text format (new format)
                if entities_data is None:
                    logger.info("Attempting to parse structured text format")
                    entities_data = EntityProcessor.parse_text_format(output_text)
                    if entities_data and entities_data.get("entities"):
                        logger.info(f"Successfully parsed text format: {len(entities_data['entities'])} entities")
                
                # If all strategies failed
                if entities_data is None:
                    logger.warning("All parsing strategies failed")
                    logger.warning(f"Output was: {output_text[:1000]}...")
                    logger.warning("Trying one more fallback: look for any entity-like patterns in markdown")
                    
                    # Last resort: try to extract entities from markdown headings/lists
                    fallback_entities = EntityProcessor.parse_markdown_entities(output_text)
                    if fallback_entities and fallback_entities.get("entities"):
                        logger.info(f"Fallback markdown parser found {len(fallback_entities['entities'])} entities")
                        return fallback_entities
                    
                    return {"entities": []}
                    
            else:
                logger.warning(f"Unexpected output type: {type(output_data)}")
                return {"entities": []}
            
            # Validate that we have a dict
            if not isinstance(entities_data, dict):
                logger.warning(f"Parsed data is not a dict: {type(entities_data)}")
                return {"entities": []}
            
            # Check for entities field
            if "entities" not in entities_data:
                logger.warning("Agent output missing 'entities' field")
                logger.warning(f"Available fields: {list(entities_data.keys())}")
                
                # Check if entities are grouped by type (e.g., "Person Entities", "Organization Entities")
                if any(key.endswith(" Entities") for key in entities_data.keys()):
                    logger.info("Found grouped entity format in output, converting to standard format")
                    entities_data = EntityProcessor.convert_grouped_entities(entities_data)
                    logger.info(f"Converted {len(entities_data['entities'])} entities from grouped format")
                # Try to be flexible - maybe entities are at root level
                # or in a different structure
                elif isinstance(entities_data, list):
                    # Maybe the whole thing is a list of entities
                    logger.info("Treating root list as entities")
                    entities_data = {"entities": entities_data}
                else:
                    return {"entities": []}
            
            entities_list = entities_data.get("entities", [])
            logger.info(f"Received {len(entities_list)} entities from agent")
            
            # Log first entity for debugging
            if entities_list:
                logger.info(f"First entity: {entities_list[0]}")
            
            return entities_data
            
        except Exception as e:
            logger.error(f"Error receiving entities from agent: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {"entities": []}
    
    @staticmethod
    def _extract_field(section: str, field_name: str) -> Optional[str]:
        """
        Extract a field value from a text section
        
        Args:
            section: Text section containing entity data
            field_name: Name of the field to extract
            
        Returns:
            Field value or None if not found
        """
        import re
        # Match field name followed by colon and value until next field or end
        pattern = rf'{field_name}:\s*(.+?)(?=\n[A-Z][a-z]+:|\nSources:|\n(?:PERSON|ORGANIZATION|TOPIC|EVENT|POLICY):|$)'
        match = re.search(pattern, section, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    @staticmethod
    def _extract_sources(section: str) -> List[Dict[str, str]]:
        """
        Extract sources from a text section
        
        Args:
            section: Text section containing entity data
            
        Returns:
            List of source dictionaries with url and excerpt
        """
        import re
        sources = []
        sources_section = re.search(
            r'Sources:\s*(.+?)(?=\n(?:PERSON|ORGANIZATION|TOPIC|EVENT|POLICY):|$)', 
            section, 
            re.DOTALL
        )
        if sources_section:
            sources_text = sources_section.group(1)
            # Parse each source line: - [URL]: "[Excerpt]"
            source_lines = re.findall(r'-\s*(.+?):\s*"(.+?)"', sources_text, re.DOTALL)
            for url, excerpt in source_lines:
                sources.append({
                    "url": url.strip(),
                    "excerpt": excerpt.strip()
                })
        return sources
    
    @staticmethod
    def parse_topic_entity(section: str) -> Optional[Dict[str, Any]]:
        """
        Parse TOPIC entity from text section
        
        Expected format:
        TOPIC: [Name]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        Args:
            section: Text section containing TOPIC entity
            
        Returns:
            Entity dictionary or None if parsing fails
        """
        import re
        
        # Extract name from TOPIC: line (handle markdown bold markers **)
        name_match = re.match(r'\*{0,2}TOPIC:\s*(.+?)(\*{0,2})?$', section, re.MULTILINE)
        if not name_match:
            return None
        
        name = name_match.group(1).strip().strip('*')
        
        # Extract fields
        description = EntityProcessor._extract_field(section, 'Description')
        sources = EntityProcessor._extract_sources(section)
        
        entity = {
            "type": "Topic",
            "name": name,
            "description": description or "",
            "sources": sources
        }
        
        return entity
    
    @staticmethod
    def parse_event_entity(section: str) -> Optional[Dict[str, Any]]:
        """
        Parse EVENT entity from text section
        
        Expected format:
        EVENT: [Name]
        Date: [ISO 8601 date or date range]
        Location: [Location]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        Args:
            section: Text section containing EVENT entity
            
        Returns:
            Entity dictionary or None if parsing fails
        """
        import re
        
        # Extract name from EVENT: line (handle markdown bold markers **)
        name_match = re.match(r'\*{0,2}EVENT:\s*(.+?)(\*{0,2})?$', section, re.MULTILINE)
        if not name_match:
            return None
        
        name = name_match.group(1).strip().strip('*')
        
        # Extract fields
        description = EntityProcessor._extract_field(section, 'Description')
        date = EntityProcessor._extract_field(section, 'Date')
        location = EntityProcessor._extract_field(section, 'Location')
        organizer = EntityProcessor._extract_field(section, 'Organizer')
        sources = EntityProcessor._extract_sources(section)
        
        entity = {
            "type": "Event",
            "name": name,
            "description": description or "",
            "sources": sources
        }
        
        # Add optional temporal and location fields
        if date:
            # Check if it's a date range (contains " to " or " - ")
            if " to " in date or " - " in date:
                # Split into start and end dates
                parts = re.split(r'\s+(?:to|-)\s+', date)
                if len(parts) == 2:
                    entity["startDate"] = parts[0].strip()
                    entity["endDate"] = parts[1].strip()
                else:
                    entity["startDate"] = date
            else:
                entity["startDate"] = date
        
        if location:
            entity["location"] = location
        
        if organizer:
            entity["organizer"] = organizer
        
        return entity
    
    @staticmethod
    def parse_policy_entity(section: str) -> Optional[Dict[str, Any]]:
        """
        Parse POLICY entity from text section
        
        Expected format:
        POLICY: [Name]
        Identifier: [Official ID]
        Effective Date: [ISO 8601 date]
        Jurisdiction: [Jurisdiction]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        Args:
            section: Text section containing POLICY entity
            
        Returns:
            Entity dictionary or None if parsing fails
        """
        import re
        
        # Extract name from POLICY: line (handle markdown bold markers **)
        name_match = re.match(r'\*{0,2}POLICY:\s*(.+?)(\*{0,2})?$', section, re.MULTILINE)
        if not name_match:
            return None
        
        name = name_match.group(1).strip().strip('*')
        
        # Extract fields
        description = EntityProcessor._extract_field(section, 'Description')
        identifier = EntityProcessor._extract_field(section, 'Identifier')
        effective_date = EntityProcessor._extract_field(section, 'Effective Date')
        jurisdiction = EntityProcessor._extract_field(section, 'Jurisdiction')
        enactment_date = EntityProcessor._extract_field(section, 'Enactment Date')
        expiration_date = EntityProcessor._extract_field(section, 'Expiration Date')
        sources = EntityProcessor._extract_sources(section)
        
        entity = {
            "type": "Policy",
            "name": name,
            "description": description or "",
            "sources": sources
        }
        
        # Add optional fields
        if identifier:
            entity["legislationIdentifier"] = identifier
        
        if effective_date:
            entity["legislationDate"] = effective_date
        
        if enactment_date:
            entity["dateCreated"] = enactment_date
        
        if expiration_date:
            entity["expirationDate"] = expiration_date
        
        if jurisdiction:
            entity["legislationJurisdiction"] = jurisdiction
        
        return entity
    
    @staticmethod
    def convert_grouped_entities(grouped_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert grouped entity format to standard format
        
        Input format:
        {
            "Person Entities": [{name, job_title, description, sources}, ...],
            "Organization Entities": [{name, description, sources}, ...],
            "Event Entities": [{name, date, location, description, sources}, ...],
            "Topic Entities": [{name, description, relationship, sources}, ...]
        }
        
        Output format:
        {
            "entities": [
                {type: "Person", name, jobTitle, description, sources},
                {type: "Organization", name, description, sources},
                ...
            ]
        }
        
        Args:
            grouped_data: Dictionary with entities grouped by type
            
        Returns:
            Dictionary with flat entities array
        """
        entities = []
        
        # Map group names to entity types
        type_mapping = {
            "Person Entities": "Person",
            "Organization Entities": "Organization",
            "Event Entities": "Event",
            "Topic Entities": "Topic",
            "Policy Entities": "Policy"
        }
        
        for group_name, entity_list in grouped_data.items():
            if not isinstance(entity_list, list):
                continue
            
            # Determine entity type
            entity_type = type_mapping.get(group_name)
            if not entity_type:
                # Try to infer from group name
                if "person" in group_name.lower() or "people" in group_name.lower():
                    entity_type = "Person"
                elif "organization" in group_name.lower():
                    entity_type = "Organization"
                elif "event" in group_name.lower():
                    entity_type = "Event"
                elif "topic" in group_name.lower():
                    entity_type = "Topic"
                elif "polic" in group_name.lower():
                    entity_type = "Policy"
                else:
                    logger.warning(f"Unknown entity group: {group_name}")
                    continue
            
            # Convert each entity in the group
            for entity_data in entity_list:
                if not isinstance(entity_data, dict):
                    continue
                
                entity = {
                    "type": entity_type,
                    "name": entity_data.get("name", ""),
                    "description": entity_data.get("description", ""),
                }
                
                # Parse sources (handle both string and list formats)
                sources = []
                raw_sources = entity_data.get("sources", [])
                if isinstance(raw_sources, list):
                    for source in raw_sources:
                        if isinstance(source, str):
                            # Parse "URL: excerpt" format
                            if ": " in source:
                                url_part, excerpt_part = source.split(": ", 1)
                                url = url_part.strip()
                                excerpt = excerpt_part.strip().strip('"')
                                sources.append({"url": url, "excerpt": excerpt})
                            else:
                                sources.append({"url": source.strip(), "excerpt": None})
                        elif isinstance(source, dict):
                            sources.append(source)
                
                entity["sources"] = sources
                
                # Add type-specific fields
                if entity_type == "Person":
                    if "job_title" in entity_data:
                        entity["jobTitle"] = entity_data["job_title"]
                    if "url" in entity_data:
                        entity["url"] = entity_data["url"]
                
                elif entity_type == "Organization":
                    if "url" in entity_data:
                        entity["url"] = entity_data["url"]
                    if "website" in entity_data:
                        entity["url"] = entity_data["website"]
                
                elif entity_type == "Event":
                    if "date" in entity_data:
                        entity["startDate"] = entity_data["date"]
                    if "location" in entity_data:
                        entity["location"] = entity_data["location"]
                    if "organizer" in entity_data:
                        entity["organizer"] = entity_data["organizer"]
                
                elif entity_type == "Topic":
                    if "about" in entity_data:
                        entity["about"] = entity_data["about"]
                    if "relationship" in entity_data:
                        entity["about"] = entity_data["relationship"]
                
                elif entity_type == "Policy":
                    if "identifier" in entity_data:
                        entity["legislationIdentifier"] = entity_data["identifier"]
                    if "effective_date" in entity_data:
                        entity["legislationDate"] = entity_data["effective_date"]
                    if "jurisdiction" in entity_data:
                        entity["legislationJurisdiction"] = entity_data["jurisdiction"]
                
                entities.append(entity)
        
        logger.info(f"Converted {len(entities)} entities from grouped format")
        return {"entities": entities}
    
    @staticmethod
    def parse_markdown_entities(text: str) -> Dict[str, Any]:
        """
        Fallback parser for markdown-formatted entity lists
        
        Handles formats like:
        ## People
        - **Name**: Description
        
        ### Organizations  
        1. **Name** - Description
        
        Args:
            text: Markdown text
            
        Returns:
            Dictionary with entities array
        """
        import re
        entities = []
        
        # Look for sections with entity type headers
        # Pattern: ## People, ### Organizations, etc.
        sections = re.split(r'\n#{1,3}\s+(People|Persons|Organizations|Topics|Events|Policies)', text, flags=re.IGNORECASE)
        
        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break
                
            entity_type_raw = sections[i].strip()
            content = sections[i + 1]
            
            # Normalize entity type
            entity_type = "Person" if "person" in entity_type_raw.lower() or "people" in entity_type_raw.lower() else \
                         "Organization" if "organization" in entity_type_raw.lower() else \
                         "Topic" if "topic" in entity_type_raw.lower() else \
                         "Event" if "event" in entity_type_raw.lower() else \
                         "Policy" if "polic" in entity_type_raw.lower() else None
            
            if not entity_type:
                continue
            
            # Extract entities from lists (- or 1. format)
            # Pattern: - **Name**: Description or 1. **Name** - Description
            entity_patterns = [
                r'[-*]\s+\*\*([^*]+)\*\*[:\-]\s*([^\n]+)',  # - **Name**: Description
                r'\d+\.\s+\*\*([^*]+)\*\*[:\-]\s*([^\n]+)',  # 1. **Name**: Description
                r'[-*]\s+([^:\n]+):\s*([^\n]+)',  # - Name: Description
            ]
            
            for pattern in entity_patterns:
                matches = re.findall(pattern, content)
                for name, description in matches:
                    name = name.strip()
                    description = description.strip()
                    
                    if name and len(name) > 1:  # Basic validation
                        entity = {
                            "type": entity_type,
                            "name": name,
                            "description": description,
                            "sources": []
                        }
                        entities.append(entity)
        
        if entities:
            logger.info(f"Markdown fallback parser extracted {len(entities)} entities")
        
        return {"entities": entities}
    
    @staticmethod
    def parse_text_format(text: str) -> Dict[str, Any]:
        """
        Parse structured text format from Search Agent
        
        Expected format:
        PERSON: [Name]
        Job Title: [Title]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        ORGANIZATION: [Name]
        Website: [URL]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        TOPIC: [Name]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        EVENT: [Name]
        Date: [ISO 8601 date]
        Location: [Location]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        POLICY: [Name]
        Identifier: [Official ID]
        Effective Date: [ISO 8601 date]
        Jurisdiction: [Jurisdiction]
        Description: [Description]
        Sources:
        - [URL]: "[Excerpt]"
        
        Args:
            text: Text output from Search Agent
            
        Returns:
            Dictionary with entities array
        """
        import re
        
        entities = []
        entity_type_stats = {
            "Person": 0,
            "Organization": 0,
            "Topic": 0,
            "Event": 0,
            "Policy": 0
        }
        
        # Split by entity type markers (with optional markdown **)
        sections = re.split(r'\n(?=\*{0,2}(?:PERSON|ORGANIZATION|TOPIC|EVENT|POLICY):)', text)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            entity = None
            
            # Route to appropriate parser based on entity type
            if section.startswith('TOPIC:') or section.startswith('**TOPIC:'):
                entity = EntityProcessor.parse_topic_entity(section)
                if entity:
                    entity_type_stats["Topic"] += 1
            elif section.startswith('EVENT:') or section.startswith('**EVENT:'):
                entity = EntityProcessor.parse_event_entity(section)
                if entity:
                    entity_type_stats["Event"] += 1
            elif section.startswith('POLICY:') or section.startswith('**POLICY:'):
                entity = EntityProcessor.parse_policy_entity(section)
                if entity:
                    entity_type_stats["Policy"] += 1
            elif section.startswith('PERSON:') or section.startswith('**PERSON:'):
                # Parse Person entity (existing logic)
                name_match = re.match(r'\*{0,2}PERSON:\s*(.+?)(\*{0,2})?$', section, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip().strip('*')
                    
                    # Extract fields
                    job_title = EntityProcessor._extract_field(section, 'Job Title')
                    description = EntityProcessor._extract_field(section, 'Description')
                    sources = EntityProcessor._extract_sources(section)
                    
                    entity = {
                        "type": "Person",
                        "name": name,
                        "description": description or "",
                        "sources": sources
                    }
                    
                    if job_title:
                        entity["jobTitle"] = job_title
                    
                    entity_type_stats["Person"] += 1
            elif section.startswith('ORGANIZATION:') or section.startswith('**ORGANIZATION:'):
                # Parse Organization entity (existing logic)
                name_match = re.match(r'\*{0,2}ORGANIZATION:\s*(.+?)(\*{0,2})?$', section, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip().strip('*')
                    
                    # Extract fields
                    website = EntityProcessor._extract_field(section, 'Website')
                    description = EntityProcessor._extract_field(section, 'Description')
                    sources = EntityProcessor._extract_sources(section)
                    
                    entity = {
                        "type": "Organization",
                        "name": name,
                        "description": description or "",
                        "sources": sources
                    }
                    
                    if website:
                        entity["url"] = website
                    
                    entity_type_stats["Organization"] += 1
            
            if entity:
                entities.append(entity)
        
        # Log statistics about entity types parsed
        total_entities = len(entities)
        logger.info(f"Parsed {total_entities} entities from text format")
        if total_entities > 0:
            logger.info(f"Entity type breakdown: {entity_type_stats}")
        
        return {"entities": entities}
    
    @staticmethod
    def deduplicate_entities(entities: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Deduplicate entities based on name, type, and Wikipedia/Wikidata IDs
        
        Deduplication strategy:
        1. Authoritative deduplication: Use Wikidata IDs if available
        2. Name-based deduplication: Merge entities with same name and type
        3. Combine sources from duplicate entities
        4. Keep highest quality description and properties
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Tuple of (deduplicated entities list, deduplication stats dict)
        """
        if not entities:
            return entities, {"duplicates_found": 0, "entities_merged": 0}
        
        dedup_stats = {
            "original_count": len(entities),
            "duplicates_found": 0,
            "entities_merged": 0,
            "wikidata_dedup": 0,
            "name_dedup": 0
        }
        
        # Group entities by deduplication key
        # Use a two-pass approach: first by Wikidata ID, then by name
        entity_groups = {}
        wikidata_to_key = {}  # Map Wikidata IDs to group keys
        
        for entity in entities:
            name = entity.get("name", "").lower().strip()
            entity_type = entity.get("type", "")
            wikidata_id = entity.get("wikidata_id")
            
            # Determine the group key
            key = None
            dedup_method = None
            
            # Check if this entity has a Wikidata ID that's already been seen
            if wikidata_id and wikidata_id in wikidata_to_key:
                key = wikidata_to_key[wikidata_id]
                dedup_method = "wikidata"
            # Check if there's already a group for this name+type
            elif f"{entity_type}:{name}" in entity_groups:
                key = f"{entity_type}:{name}"
                dedup_method = "name"
                # If this entity has a Wikidata ID, register it
                if wikidata_id:
                    wikidata_to_key[wikidata_id] = key
                    entity_groups[key]["dedup_method"] = "wikidata"
            # Create new group
            else:
                key = f"{entity_type}:{name}"
                dedup_method = "wikidata" if wikidata_id else "name"
                if wikidata_id:
                    wikidata_to_key[wikidata_id] = key
            
            if key not in entity_groups:
                entity_groups[key] = {
                    "entities": [],
                    "dedup_method": dedup_method
                }
            
            entity_groups[key]["entities"].append(entity)
        
        # Merge duplicate groups
        deduplicated = []
        
        for key, group in entity_groups.items():
            group_entities = group["entities"]
            dedup_method = group["dedup_method"]
            
            if len(group_entities) == 1:
                # No duplicates
                deduplicated.append(group_entities[0])
            else:
                # Merge duplicates
                dedup_stats["duplicates_found"] += len(group_entities) - 1
                dedup_stats["entities_merged"] += len(group_entities)
                
                if dedup_method == "wikidata":
                    dedup_stats["wikidata_dedup"] += 1
                else:
                    dedup_stats["name_dedup"] += 1
                
                merged = EntityProcessor._merge_duplicate_entities(group_entities)
                deduplicated.append(merged)
                
                logger.info(
                    f"Merged {len(group_entities)} duplicate entities: '{merged.get('name')}' "
                    f"(method: {dedup_method})"
                )
        
        dedup_stats["final_count"] = len(deduplicated)
        
        logger.info(
            f"Deduplication complete: {dedup_stats['original_count']} → {dedup_stats['final_count']} entities "
            f"({dedup_stats['duplicates_found']} duplicates removed)"
        )
        
        return deduplicated, dedup_stats
    
    @staticmethod
    def _merge_duplicate_entities(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple duplicate entities into one
        
        Strategy:
        - Use entity with highest quality score as base
        - Combine all sources
        - Keep longest/most detailed description
        - Preserve all Wikipedia links
        - Combine all properties
        
        Args:
            entities: List of duplicate entity dictionaries
            
        Returns:
            Merged entity dictionary
        """
        if not entities:
            return {}
        
        # Sort by quality score (highest first)
        sorted_entities = sorted(
            entities,
            key=lambda e: e.get("quality_score", 0.0),
            reverse=True
        )
        
        # Use highest quality entity as base
        merged = sorted_entities[0].copy()
        
        # Combine sources from all entities
        all_sources = []
        seen_urls = set()
        
        for entity in entities:
            for source in entity.get("sources", []):
                url = source.get("url", "")
                if url and url not in seen_urls:
                    all_sources.append(source)
                    seen_urls.add(url)
        
        merged["sources"] = all_sources
        
        # Use longest description
        longest_desc = ""
        for entity in entities:
            desc = entity.get("description", "")
            if len(desc) > len(longest_desc):
                longest_desc = desc
        
        if longest_desc:
            merged["description"] = longest_desc
        
        # Combine Wikipedia links
        all_sameAs = set()
        all_wiki_links = []
        
        for entity in entities:
            if entity.get("sameAs"):
                if isinstance(entity["sameAs"], list):
                    all_sameAs.update(entity["sameAs"])
                else:
                    all_sameAs.add(entity["sameAs"])
            
            if entity.get("wikipedia_links"):
                for link in entity["wikipedia_links"]:
                    if link not in all_wiki_links:
                        all_wiki_links.append(link)
        
        if all_sameAs:
            merged["sameAs"] = list(all_sameAs)
        
        if all_wiki_links:
            merged["wikipedia_links"] = all_wiki_links
        
        # Prefer Wikidata ID from any entity
        for entity in entities:
            if entity.get("wikidata_id"):
                merged["wikidata_id"] = entity["wikidata_id"]
                break
        
        # For Person entities, prefer entity with jobTitle
        if merged.get("type") == "Person":
            for entity in entities:
                if entity.get("jobTitle") and not merged.get("jobTitle"):
                    merged["jobTitle"] = entity["jobTitle"]
                    break
        
        # For Organization entities, prefer entity with URL
        if merged.get("type") == "Organization":
            for entity in entities:
                if entity.get("url") and not merged.get("url"):
                    merged["url"] = entity["url"]
                    break
        
        # Recalculate quality score based on merged data
        merged["quality_score"] = EntityValidator.calculate_quality_score(merged)
        
        return merged
    
    @staticmethod
    def validate_and_convert_entities(
        entities_data: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Validate and convert entities to proper format with quality checks and deduplication
        
        Args:
            entities_data: Raw entities data from agent
            
        Returns:
            Tuple of (validated entities list, validation metrics dict)
        """
        raw_entities = entities_data.get("entities", [])
        
        # First pass: Filter low-quality entities using EntityValidator
        filtered_entities, validation_metrics = EntityValidator.filter_low_quality_entities(raw_entities)
        
        logger.info(f"Quality filtering: {len(filtered_entities)}/{len(raw_entities)} entities passed")
        
        # Second pass: Convert to proper format and add quality indicators
        validated_entities = []
        
        for entity in filtered_entities:
            try:
                entity_type = entity.get("type")
                
                # Convert sources to EntitySource objects
                sources = []
                for source in entity.get("sources", []):
                    sources.append(EntitySource(
                        url=source.get("url", ""),
                        excerpt=source.get("excerpt")
                    ))
                
                # Validate based on entity type
                if entity_type == "Person":
                    person = PersonEntity(
                        name=entity.get("name", ""),
                        description=entity.get("description"),
                        jobTitle=entity.get("jobTitle"),
                        url=entity.get("url"),
                        sources=sources
                    )
                    entity_dict = person.model_dump(by_alias=True)
                    
                elif entity_type == "Organization":
                    org = OrganizationEntity(
                        name=entity.get("name", ""),
                        description=entity.get("description"),
                        url=entity.get("url"),
                        sources=sources
                    )
                    entity_dict = org.model_dump(by_alias=True)
                    
                elif entity_type == "Topic":
                    topic = TopicEntity(
                        name=entity.get("name", ""),
                        description=entity.get("description"),
                        about=entity.get("about"),
                        sources=sources
                    )
                    entity_dict = topic.model_dump(by_alias=True)
                    
                elif entity_type == "Event":
                    event = EventEntity(
                        name=entity.get("name", ""),
                        description=entity.get("description"),
                        startDate=entity.get("startDate"),
                        endDate=entity.get("endDate"),
                        location=entity.get("location"),
                        organizer=entity.get("organizer"),
                        sources=sources
                    )
                    entity_dict = event.model_dump(by_alias=True)
                    
                elif entity_type == "Policy":
                    policy = PolicyEntity(
                        name=entity.get("name", ""),
                        description=entity.get("description"),
                        legislationIdentifier=entity.get("legislationIdentifier"),
                        dateCreated=entity.get("dateCreated"),
                        dateModified=entity.get("dateModified"),
                        legislationDate=entity.get("legislationDate"),
                        expirationDate=entity.get("expirationDate"),
                        legislationJurisdiction=entity.get("legislationJurisdiction"),
                        sources=sources
                    )
                    entity_dict = policy.model_dump(by_alias=True)
                    
                else:
                    logger.warning(f"Unknown entity type: {entity_type}")
                    continue
                
                # Add quality indicators
                entity_dict["quality_score"] = entity.get("quality_score", 0.0)
                entity_dict = EntityValidator.add_quality_indicators(entity_dict)
                
                # Preserve Wikipedia enrichment data
                if entity.get("sameAs"):
                    entity_dict["sameAs"] = entity["sameAs"]
                if entity.get("wikidata_id"):
                    entity_dict["wikidata_id"] = entity["wikidata_id"]
                if entity.get("wikipedia_links"):
                    entity_dict["wikipedia_links"] = entity["wikipedia_links"]
                
                validated_entities.append(entity_dict)
                    
            except Exception as e:
                logger.error(f"Failed to validate entity: {e}")
                continue
        
        # Third pass: Deduplicate entities
        deduplicated_entities, dedup_stats = EntityProcessor.deduplicate_entities(validated_entities)
        
        # Add deduplication stats to validation metrics
        validation_metrics["deduplication"] = dedup_stats
        
        logger.info(f"Final entity count: {len(deduplicated_entities)} (after validation and deduplication)")
        return deduplicated_entities, validation_metrics
    
    @staticmethod
    def generate_jsonld_sachstand(
        topic: str,
        entities: List[Dict[str, Any]],
        completion_status: str = "complete",
        mece_graph: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON-LD Sachstand from entities
        
        Args:
            topic: Research topic
            entities: List of validated entities
            completion_status: "complete" or "partial"
            mece_graph: Optional MECE decomposition graph
            
        Returns:
            JSON-LD Sachstand dictionary
        """
        now = datetime.now(timezone.utc)
        
        # Convert entities to JSON-LD format with @type
        jsonld_entities = []
        for entity in entities:
            jsonld_entity = {
                "@type": entity.get("type"),
                "name": entity.get("name"),
            }
            
            # Add optional fields (common to all types)
            if entity.get("description"):
                jsonld_entity["description"] = entity["description"]
            if entity.get("url"):
                jsonld_entity["url"] = entity["url"]
            
            # Person-specific fields
            if entity.get("jobTitle"):
                jsonld_entity["jobTitle"] = entity["jobTitle"]
            
            # Topic-specific fields
            if entity.get("about"):
                jsonld_entity["about"] = entity["about"]
            
            # Event-specific fields
            if entity.get("startDate"):
                jsonld_entity["startDate"] = entity["startDate"]
            if entity.get("endDate"):
                jsonld_entity["endDate"] = entity["endDate"]
            if entity.get("location"):
                jsonld_entity["location"] = entity["location"]
            if entity.get("organizer"):
                jsonld_entity["organizer"] = entity["organizer"]
            
            # Policy-specific fields
            if entity.get("legislationIdentifier"):
                jsonld_entity["legislationIdentifier"] = entity["legislationIdentifier"]
            if entity.get("dateCreated"):
                jsonld_entity["dateCreated"] = entity["dateCreated"]
            if entity.get("dateModified"):
                jsonld_entity["dateModified"] = entity["dateModified"]
            if entity.get("legislationDate"):
                jsonld_entity["legislationDate"] = entity["legislationDate"]
            if entity.get("expirationDate"):
                jsonld_entity["expirationDate"] = entity["expirationDate"]
            if entity.get("legislationJurisdiction"):
                jsonld_entity["legislationJurisdiction"] = entity["legislationJurisdiction"]
            
            # Add Wikipedia enrichment data
            if entity.get("sameAs"):
                jsonld_entity["sameAs"] = entity["sameAs"]
            
            if entity.get("wikidata_id"):
                # Add Wikidata ID as identifier
                jsonld_entity["identifier"] = {
                    "@type": "PropertyValue",
                    "propertyID": "Wikidata",
                    "value": entity["wikidata_id"]
                }
            
            # Add citations from sources
            if entity.get("sources"):
                citations = []
                for source in entity["sources"]:
                    citation = {
                        "@type": "WebPage",
                        "url": source.get("url")
                    }
                    if source.get("accessed_at"):
                        citation["dateAccessed"] = source["accessed_at"]
                    citations.append(citation)
                jsonld_entity["citation"] = citations
            
            jsonld_entities.append(jsonld_entity)
        
        # Create Sachstand structure
        sachstand = {
            "@context": "https://schema.org",
            "@type": "ResearchReport",
            "name": f"Sachstand: {topic}",
            "dateCreated": now.isoformat(),
            "author": {
                "@type": "SoftwareApplication",
                "name": "Honeycomb OSINT Agent Team",
                "version": "0.1.0"
            },
            "about": {
                "@type": "Thing",
                "name": topic
            },
            "hasPart": jsonld_entities,
            "completionStatus": completion_status
        }
        
        # Add MECE coverage graph if available
        if mece_graph:
            sachstand["coverage"] = {
                "@type": "PropertyValue",
                "name": "MECE Coverage Graph",
                "value": mece_graph
            }
            logger.info(f"Added MECE coverage graph to Sachstand")
        
        logger.info(f"Generated JSON-LD Sachstand with {len(jsonld_entities)} entities")
        return sachstand
    
    @staticmethod
    def process_agent_response(
        agent_response: dict,
        topic: str,
        completion_status: str = "complete"
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Process agent response: receive entities and generate JSON-LD with validation metrics
        
        Architecture: The team agent (via Response Generator) has created output.
        We receive, validate, and format into JSON-LD.
        
        Team Agent Flow:
        1. Mentalist plans research strategy (may include MECE decomposition)
        2. Orchestrator routes to Search Agent
        3. Search Agent uses Tavily to find info and extract entities
        4. Inspector reviews steps and output
        5. Feedback Combiner consolidates feedback
        6. Response Generator creates final output
        7. API receives response and formats to JSON-LD
        
        Args:
            agent_response: Response from aixplain team agent with extracted entities
            topic: Research topic
            completion_status: "complete" or "partial"
            
        Returns:
            Tuple of (JSON-LD Sachstand dictionary, MECE graph dictionary or None, validation metrics dict)
        """
        validation_metrics = {
            "total_entities": 0,
            "valid_entities": 0,
            "rejected_entities": 0,
            "avg_quality_score": 0.0
        }
        
        try:
            # Extract MECE graph from Mentalist output
            mece_graph = EntityProcessor.extract_mece_graph(agent_response)
            
            # Receive entities that the agent already extracted
            entities_data = EntityProcessor.receive_entities_from_agent(agent_response)
            
            # Check if we got any entities
            if not entities_data.get("entities"):
                logger.warning("No entities extracted from agent response")
                logger.warning("This could be due to:")
                logger.warning("  - Agent execution failed or returned empty results")
                logger.warning("  - Tool (Tavily Search) not accessible or returned no results")
                logger.warning("  - Agent prompt needs refinement")
                logger.warning("  - Topic too specific or no information available")
                
                # Return empty Sachstand with error note
                return (
                    EntityProcessor.generate_jsonld_sachstand(
                        topic=topic,
                        entities=[],
                        completion_status="failed",
                        mece_graph=mece_graph
                    ),
                    mece_graph,
                    validation_metrics
                )
            
            # Validate the entities the agent provided with quality checks
            validated_entities, validation_metrics = EntityProcessor.validate_and_convert_entities(entities_data)
            
            if not validated_entities:
                logger.warning("No entities passed validation")
                logger.warning("Check entity structure and required fields")
                logger.warning(f"Validation metrics: {validation_metrics}")
            else:
                logger.info(f"Validation summary: {validation_metrics['valid_entities']}/{validation_metrics['total_entities']} "
                          f"entities passed (avg score: {validation_metrics['avg_quality_score']:.2f})")
            
            # Generate JSON-LD Sachstand from agent's entities
            sachstand = EntityProcessor.generate_jsonld_sachstand(
                topic=topic,
                entities=validated_entities,
                completion_status=completion_status,
                mece_graph=mece_graph
            )
            
            # Add validation metrics to Sachstand
            sachstand["validationMetrics"] = validation_metrics
            
            logger.info(f"Successfully processed agent response: {len(validated_entities)} entities")
            return sachstand, mece_graph, validation_metrics
            
        except Exception as e:
            logger.error(f"Failed to process agent response: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Return error Sachstand
            return (
                EntityProcessor.generate_jsonld_sachstand(
                    topic=topic,
                    entities=[],
                    completion_status="error"
                ),
                None,
                validation_metrics
            )
