"""
Team Agent Configuration for Honeycomb OSINT Agent Team System

This module defines team agent configurations using aixplain's TeamAgentFactory.
The team includes built-in micro agents (Mentalist, Inspector, Orchestrator, Response Generator)
and user-defined agents (Search Agent with Tavily tool).
"""
import logging
from typing import Dict, Any, Optional, List
from aixplain.factories import AgentFactory, ToolFactory, TeamAgentFactory

from api.config import Config
from api.search_strategy import enhance_instructions, analyze_topic, generate_alternative_terms
from api.instructions.search_agent import get_search_agent_instructions
from api.instructions.wikipedia_agent import get_wikipedia_agent_instructions
from api.instructions.mentalist import get_mentalist_instructions
from api.instructions.validation_agent import get_validation_agent_instructions
from api.instructions.ontology_agent import get_ontology_agent_instructions

logger = logging.getLogger(__name__)


class TeamConfig:
    """Configuration for team agent creation"""
    
    @staticmethod
    def get_validation_tools() -> List[Any]:
        """
        Get validation tool objects for Validation Agent
        
        Returns:
            List of validation Tool objects (Schema.org Validator, URL Verifier)
        """
        tools = []
        
        try:
            schema_validator_tool = ToolFactory.get(Config.get_tool_id("schema_validator"))
            logger.info(f"Retrieved Schema.org Validator tool: {schema_validator_tool.id}")
            tools.append(schema_validator_tool)
        except Exception as e:
            logger.error(f"Failed to retrieve Schema.org Validator tool: {e}")
            logger.warning("Schema.org validation will not be available")
        
        try:
            url_verifier_tool = ToolFactory.get(Config.get_tool_id("url_verifier"))
            logger.info(f"Retrieved URL Verifier tool: {url_verifier_tool.id}")
            tools.append(url_verifier_tool)
        except Exception as e:
            logger.error(f"Failed to retrieve URL Verifier tool: {e}")
            logger.warning("URL verification will not be available")
        
        return tools
    
    @staticmethod
    def get_tools(include_wikipedia: bool = False, include_google_search: bool = True, include_tavily: bool = True) -> List[Any]:
        """
        Get tool objects for agent configuration
        
        Args:
            include_wikipedia: Whether to include Wikipedia tool
            include_google_search: Whether to include Google Search tool
            include_tavily: Whether to include Tavily Search tool
        
        Returns:
            List of Tool objects
        """
        tools = []
        
        if include_tavily:
            try:
                tavily_tool = ToolFactory.get(Config.get_tool_id("tavily_search"))
                logger.info(f"Retrieved Tavily Search tool: {tavily_tool.id}")
                tools.append(tavily_tool)
            except Exception as e:
                logger.error(f"Failed to retrieve Tavily tool: {e}")
        
        if include_google_search:
            try:
                google_tool = ToolFactory.get(Config.get_tool_id("google_search"))
                logger.info(f"Retrieved Google Search tool: {google_tool.id}")
                tools.append(google_tool)
            except Exception as e:
                logger.error(f"Failed to retrieve Google Search tool: {e}")
                logger.warning("Google Search tool not available - will rely on Tavily only")
        
        if include_wikipedia:
            try:
                wikipedia_tool = ToolFactory.get(Config.get_tool_id("wikipedia"))
                logger.info(f"Retrieved Wikipedia tool: {wikipedia_tool.id}")
                tools.append(wikipedia_tool)
            except Exception as e:
                logger.error(f"Failed to retrieve Wikipedia tool: {e}")
                logger.warning("Wikipedia tool not available - entity linking will be skipped")
        
        return tools
    
    @staticmethod
    def create_wikipedia_agent(model_id: str = None) -> Any:
        """
        Create Wikipedia Agent for entity linking and enrichment
        
        This agent is responsible for:
        - Checking if extracted entities exist in Wikipedia
        - Retrieving Wikipedia URLs in multiple languages (de, en, fr)
        - Extracting Wikidata IDs for authoritative linking
        - Adding sameAs properties to entities
        
        NOTE: Uses GPT-4o by default (configured in Config.WIKIPEDIA_AGENT_MODEL)
        
        Args:
            model_id: Model ID to use, defaults to Config.WIKIPEDIA_AGENT_MODEL (GPT-4o)
            
        Returns:
            Agent object or None if Wikipedia tool not configured
        """
        if model_id is None:
            model_id = Config.WIKIPEDIA_AGENT_MODEL
        
        # Get instructions from separate file
        system_prompt = get_wikipedia_agent_instructions()
        
        # Get Wikipedia tool
        try:
            wikipedia_tool = ToolFactory.get(Config.get_tool_id("wikipedia"))
        except Exception as e:
            logger.error(f"Failed to get Wikipedia tool: {e}")
            return None
        
        # Create agent
        agent = AgentFactory.create(
            name="Wikipedia Agent",
            description="Entity linking agent that enriches entities with Wikipedia URLs and Wikidata IDs",
            llm_id=model_id,
            instructions=system_prompt,
            tools=[wikipedia_tool]
        )
        
        logger.info(f"Created Wikipedia Agent with ID: {agent.id}")
        return agent
    
    @staticmethod
    def create_ontology_agent(model_id: str = None) -> Any:
        """
        Create Ontology Agent for schema.org type and relationship suggestions
        
        This agent is responsible for:
        - Suggesting more specific schema.org types for entities
        - Identifying potential relationships between entities
        - Recommending additional schema.org properties
        - Ensuring semantic consistency across the entity pool
        - Helping the hive mind produce semantically rich data
        
        NOTE: Uses GPT-4o by default (configured in Config.TEAM_AGENT_MODEL)
        
        Args:
            model_id: Model ID to use, defaults to Config.TEAM_AGENT_MODEL (GPT-4o)
            
        Returns:
            Agent object
        """
        if model_id is None:
            model_id = Config.TEAM_AGENT_MODEL
        
        # Get instructions from separate file
        system_prompt = get_ontology_agent_instructions()
        
        # Create agent (no tools needed - uses schema.org knowledge)
        agent = AgentFactory.create(
            name="Ontology Agent",
            description="Schema.org expert that suggests type improvements and relationship properties for entities",
            llm_id=model_id,
            instructions=system_prompt,
            tools=[]  # No tools needed - uses built-in schema.org knowledge
        )
        
        logger.info(f"Created Ontology Agent with ID: {agent.id}")
        logger.info("Ontology Agent provides schema.org expertise for semantic enrichment")
        return agent
    
    @staticmethod
    def create_validation_agent(model_id: str = None) -> Any:
        """
        Create Validation Agent for entity quality checking
        
        This agent is responsible for:
        - Validating entities against schema.org specifications
        - Verifying URLs are valid and accessible
        - Providing validation feedback to other agents
        - Tracking validation metrics
        - Available on-demand and proactively scans entity pool
        
        NOTE: Uses GPT-4o by default (configured in Config.TEAM_AGENT_MODEL)
        
        Args:
            model_id: Model ID to use, defaults to Config.TEAM_AGENT_MODEL (GPT-4o)
            
        Returns:
            Agent object or None if validation tools not configured
        """
        if model_id is None:
            model_id = Config.TEAM_AGENT_MODEL
        
        # Get instructions from separate file
        system_prompt = get_validation_agent_instructions()
        
        # Get validation tools
        validation_tools = TeamConfig.get_validation_tools()
        
        if not validation_tools:
            logger.error("No validation tools available - cannot create Validation Agent")
            return None
        
        # Create agent
        agent = AgentFactory.create(
            name="Validation Agent",
            description="Quality checker agent that validates entities for schema.org compliance and URL accessibility",
            llm_id=model_id,
            instructions=system_prompt,
            tools=validation_tools
        )
        
        logger.info(f"Created Validation Agent with ID: {agent.id}")
        logger.info(f"Validation Agent has {len(validation_tools)} tools: Schema.org Validator, URL Verifier")
        return agent
    
    @staticmethod
    def create_search_agent(topic: str, model_id: str = None) -> Any:
        """
        Create Search Agent (user-defined) with Tavily tool
        
        This agent is responsible for:
        - Using Tavily Search to find information
        - Extracting Person and Organization entities
        - Returning structured JSON with entities
        
        NOTE: Uses GPT-4o by default (configured in Config.SEARCH_AGENT_MODEL)
        Search Agent needs:
        - Larger context window for complex instructions
        - Better reasoning for entity extraction
        - More reliable parsing of search results
        - Less likely to timeout on complex tasks
        
        NOTE: We do NOT use WorkflowTask here because it would take planning
        responsibility away from the Mentalist. Instead, we let the Mentalist
        decide when and how to use this agent based on the team instructions.
        
        Args:
            topic: Research topic
            model_id: Model ID to use, defaults to Config.SEARCH_AGENT_MODEL (GPT-4o)
            
        Returns:
            Agent object
        """
        if model_id is None:
            model_id = Config.SEARCH_AGENT_MODEL
        
        # Get instructions from separate file
        system_prompt = get_search_agent_instructions(topic)
        
        # Log a snippet of the instructions to verify format
        if "OUTPUT FORMAT" in system_prompt:
            format_section = system_prompt[system_prompt.index("OUTPUT FORMAT"):system_prompt.index("OUTPUT FORMAT")+200]
            logger.info(f"Search Agent instructions include: {format_section}...")
        
        # Enhance instructions with fallback strategies
        system_prompt = enhance_instructions(topic, system_prompt)
        
        # Get tools (Google Search only, no Tavily)
        tools = TeamConfig.get_tools(include_google_search=True, include_tavily=False)
        
        # Create agent WITHOUT workflow_tasks
        # This allows the Mentalist to plan when/how to use this agent
        agent = AgentFactory.create(
            name=f"Search Agent",
            description=f"OSINT research agent with Google Search. Extracts Person and Organization entities with sources.",
            llm_id=model_id,
            instructions=system_prompt,
            tools=tools
            # NO workflow_tasks - let Mentalist plan!
        )
        
        logger.info(f"Created Search Agent with ID: {agent.id}")
        logger.info(f"Search Agent model: {model_id} (GPT-4o)")
        logger.info(f"Search Agent tools: {[tool.name if hasattr(tool, 'name') else str(tool) for tool in tools]}")
        logger.info(f"Search Agent instructions length: {len(system_prompt)} characters")
        return agent
    
    @staticmethod
    def create_team(topic: str, goals: Optional[List[str]] = None, team_model_id: str = None,
                   search_model_id: str = None, wikipedia_model_id: str = None,
                   validation_model_id: str = None, ontology_model_id: str = None,
                   enable_wikipedia: bool = True, enable_validation: bool = True,
                   enable_ontology: bool = True) -> Any:
        """
        Create Team Agent with built-in micro agents and user-defined agents
        
        Team structure:
        - Built-in micro agents (automatic):
          - Mentalist: Plans strategy with MECE decomposition for complex topics
          - Inspector: Reviews output for quality
          - Orchestrator: Routes tasks to agents
          - Feedback Combiner: Consolidates inspection feedback
          - Response Generator: Synthesizes final output
        - User-defined agents:
          - Search Agent: Uses Tavily to research and extract entities
          - Ontology Agent (optional): Suggests schema.org type improvements and relationships
          - Wikipedia Agent (optional): Enriches entities with Wikipedia links and Wikidata IDs
          - Validation Agent (optional): Validates entities for schema.org compliance and URL accessibility
        
        NOTE: All agents use GPT-4o by default (configured in Config)
        
        Args:
            topic: Research topic
            goals: Optional list of research goals
            team_model_id: Model ID for team micro agents, defaults to Config.TEAM_AGENT_MODEL (GPT-4o)
            search_model_id: Model ID for Search Agent, defaults to Config.SEARCH_AGENT_MODEL (GPT-4o)
            wikipedia_model_id: Model ID for Wikipedia Agent, defaults to Config.WIKIPEDIA_AGENT_MODEL (GPT-4o)
            validation_model_id: Model ID for Validation Agent, defaults to Config.TEAM_AGENT_MODEL (GPT-4o)
            ontology_model_id: Model ID for Ontology Agent, defaults to Config.TEAM_AGENT_MODEL (GPT-4o)
            enable_wikipedia: Whether to include Wikipedia agent for entity enrichment
            enable_validation: Whether to include Validation agent for entity quality checking
            enable_ontology: Whether to include Ontology agent for schema.org suggestions
            
        Returns:
            TeamAgent object
        """
        # Use configured defaults if not specified
        if team_model_id is None:
            team_model_id = Config.TEAM_AGENT_MODEL
        if search_model_id is None:
            search_model_id = Config.SEARCH_AGENT_MODEL
        if wikipedia_model_id is None:
            wikipedia_model_id = Config.WIKIPEDIA_AGENT_MODEL
        if validation_model_id is None:
            validation_model_id = Config.TEAM_AGENT_MODEL
        if ontology_model_id is None:
            ontology_model_id = Config.TEAM_AGENT_MODEL
        
        # Create Search Agent WITHOUT WorkflowTask
        # This allows Mentalist to plan dynamically
        search_agent = TeamConfig.create_search_agent(topic, search_model_id)
        
        # Create Ontology Agent if enabled and configured
        user_agents = [search_agent]
        ontology_agent = None
        if enable_ontology:
            ontology_agent = TeamConfig.create_ontology_agent(ontology_model_id)
            if ontology_agent:
                user_agents.append(ontology_agent)
                logger.info("Ontology agent added to team for schema.org suggestions")
        
        # Create Validation Agent if enabled and configured
        validation_agent = None
        if enable_validation:
            validation_agent = TeamConfig.create_validation_agent(validation_model_id)
            if validation_agent:
                user_agents.append(validation_agent)
                logger.info("Validation agent added to team for entity quality checking")
        
        # Create Wikipedia Agent if enabled and configured
        wikipedia_agent = None
        if enable_wikipedia:
            wikipedia_agent = TeamConfig.create_wikipedia_agent(wikipedia_model_id)
            if wikipedia_agent:
                user_agents.append(wikipedia_agent)
                logger.info("Wikipedia agent added to team for entity enrichment")
        
        # Analyze topic for strategic planning
        topic_analysis = analyze_topic(topic)
        alternatives = generate_alternative_terms(topic)
        
        # Get Mentalist instructions from separate file
        mentalist_instructions = get_mentalist_instructions(
            topic=topic,
            goals=goals,
            topic_analysis=topic_analysis,
            alternatives=alternatives,
            has_wikipedia_agent=(wikipedia_agent is not None),
            has_validation_agent=(validation_agent is not None),
            has_ontology_agent=(ontology_agent is not None)
        )
        
        # Sanitize team name (only alphanumeric, spaces, hyphens, brackets allowed)
        import re
        import uuid
        sanitized_topic = re.sub(r'[^a-zA-Z0-9 \-\(\)]', '', topic[:30])
        
        # Add unique identifier to force new team creation (avoid aixplain caching)
        # Use only alphanumeric characters (no special chars)
        unique_id = str(uuid.uuid4()).replace('-', '')[:8]
        
        # Create team with built-in micro agents (NO INSPECTORS - simplified)
        # NOTE: We do NOT define WorkflowTask - let Mentalist plan dynamically
        team = TeamAgentFactory.create(
            name=f"OSINT Team - {sanitized_topic} ({unique_id})",
            description=f"OSINT research team for topic: {topic}",
            instructions=mentalist_instructions,
            agents=user_agents,  # User-defined agents (no WorkflowTask)
            llm_id=team_model_id,  # Model for micro agents (Mentalist, etc.)
            use_mentalist=True  # Enable Mentalist for dynamic planning
            # NO inspectors - simplified configuration
        )
        
        logger.info(f"Created Team Agent with ID: {team.id}")
        logger.info(f"Team micro agents model: {team_model_id} (GPT-4o)")
        logger.info(f"Search Agent model: {search_model_id} (GPT-4o)")
        if ontology_agent:
            logger.info(f"Ontology Agent model: {ontology_model_id} (GPT-4o)")
        if validation_agent:
            logger.info(f"Validation Agent model: {validation_model_id} (GPT-4o)")
        if wikipedia_agent:
            logger.info(f"Wikipedia Agent model: {wikipedia_model_id} (GPT-4o)")
        logger.info(f"Team includes: Mentalist, Orchestrator, Response Generator (built-in, no Inspector)")
        agent_names = "Search Agent (with Google Search tool)"
        if ontology_agent:
            agent_names += ", Ontology Agent (schema.org expert)"
        if validation_agent:
            agent_names += ", Validation Agent (with Schema.org Validator and URL Verifier tools)"
        if wikipedia_agent:
            agent_names += ", Wikipedia Agent (with Wikipedia tool)"
        logger.info(f"User-defined agents: {agent_names}")
        logger.info(f"Team configuration: Simplified (no inspectors)")
        
        return team
    
    @staticmethod
    def format_research_prompt(topic: str, goals: Optional[List[str]] = None) -> str:
        """
        Format the input prompt for the team agent
        
        Args:
            topic: Research topic
            goals: Optional list of research goals
            
        Returns:
            Formatted prompt string
        """
        prompt = f"Research the following topic and extract key entities (Person, Organization, Events, Topics):\n\n"
        prompt += f"Topic: {topic}\n\n"
        
        if goals:
            prompt += "Research Goals:\n"
            for i, goal in enumerate(goals, 1):
                prompt += f"{i}. {goal}\n"
            prompt += "\n"
        
        prompt += "Please provide a comprehensive report with:\n"
        prompt += "1. Person entities with their roles, descriptions, and source URLs\n"
        prompt += "2. Organization entities with their descriptions and source URLs\n"
        prompt += "3. Events entities with their descriptions, timeframe and source URLs\n"
        prompt += "3. T opic entities with their descriptions, relationship to People, Organization or Event and their source URLs\n"
        prompt += "4. Real source URLs with relevant excerpts for each entity\n"
        prompt += "\nNote: The Response Generator agent will handle the formatting. Focus on finding comprehensive, accurate information.\n"
        
        return prompt
