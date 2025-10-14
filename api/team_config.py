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

logger = logging.getLogger(__name__)


class TeamConfig:
    """Configuration for team agent creation"""
    
    @staticmethod
    def get_tools(include_wikipedia: bool = False, include_google_search: bool = True) -> List[Any]:
        """
        Get tool objects for agent configuration
        
        Args:
            include_wikipedia: Whether to include Wikipedia tool
            include_google_search: Whether to include Google Search tool as backup
        
        Returns:
            List of Tool objects
        """
        tools = []
        
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
    def create_wikipedia_agent(model: str = None) -> Any:
        """
        Create Wikipedia Agent for entity linking and enrichment
        
        This agent is responsible for:
        - Checking if extracted entities exist in Wikipedia
        - Retrieving Wikipedia URLs in multiple languages (de, en, fr)
        - Extracting Wikidata IDs for authoritative linking
        - Adding sameAs properties to entities
        
        Args:
            model: Model type ("testing" or "production"), None uses default from Config
            
        Returns:
            Agent object or None if Wikipedia tool not configured
        """
        model_id = Config.get_model_id(model)
        
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
    def create_search_agent(topic: str, model: str = None) -> Any:
        """
        Create Search Agent (user-defined) with Tavily tool
        
        This agent is responsible for:
        - Using Tavily Search to find information
        - Extracting Person and Organization entities
        - Returning structured JSON with entities
        
        NOTE: We do NOT use WorkflowTask here because it would take planning
        responsibility away from the Mentalist. Instead, we let the Mentalist
        decide when and how to use this agent based on the team instructions.
        
        Args:
            topic: Research topic
            model: Model type ("testing" or "production"), None uses default from Config
            
        Returns:
            Agent object
        """
        model_id = Config.get_model_id(model)
        
        # Get instructions from separate file
        system_prompt = get_search_agent_instructions(topic)
        
        # Log a snippet of the instructions to verify format
        if "OUTPUT FORMAT" in system_prompt:
            format_section = system_prompt[system_prompt.index("OUTPUT FORMAT"):system_prompt.index("OUTPUT FORMAT")+200]
            logger.info(f"Search Agent instructions include: {format_section}...")
        
        # Enhance instructions with fallback strategies
        system_prompt = enhance_instructions(topic, system_prompt)
        
        # Get tools (including Google Search as backup)
        tools = TeamConfig.get_tools(include_google_search=True)
        
        # Create agent WITHOUT workflow_tasks
        # This allows the Mentalist to plan when/how to use this agent
        agent = AgentFactory.create(
            name=f"Search Agent",
            description=f"OSINT research agent with Tavily Search. Extracts Person and Organization entities with sources.",
            llm_id=model_id,
            instructions=system_prompt,
            tools=tools
            # NO workflow_tasks - let Mentalist plan!
        )
        
        logger.info(f"Created Search Agent with ID: {agent.id}")
        return agent
    
    @staticmethod
    def create_team(topic: str, goals: Optional[List[str]] = None, model: str = None, 
                   enable_wikipedia: bool = True) -> Any:
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
          - Wikipedia Agent (optional): Enriches entities with Wikipedia links and Wikidata IDs
        
        Args:
            topic: Research topic
            goals: Optional list of research goals
            model: Model type ("testing" or "production"), None uses default from Config
            enable_wikipedia: Whether to include Wikipedia agent for entity enrichment
            
        Returns:
            TeamAgent object
        """
        model_id = Config.get_model_id(model)
        
        # Create Search Agent WITHOUT WorkflowTask
        # This allows Mentalist to plan dynamically
        search_agent = TeamConfig.create_search_agent(topic, model)
        
        # Create Wikipedia Agent if enabled and configured
        user_agents = [search_agent]
        wikipedia_agent = None
        if enable_wikipedia:
            wikipedia_agent = TeamConfig.create_wikipedia_agent(model)
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
            has_wikipedia_agent=(wikipedia_agent is not None)
        )
        
        # Sanitize team name (only alphanumeric, spaces, hyphens, brackets allowed)
        import re
        import uuid
        sanitized_topic = re.sub(r'[^a-zA-Z0-9 \-\(\)]', '', topic[:30])
        
        # Add unique identifier to force new team creation (avoid aixplain caching)
        # Use only alphanumeric characters (no special chars)
        unique_id = str(uuid.uuid4()).replace('-', '')[:8]
        
        # Create team with built-in micro agents
        # NOTE: We do NOT define WorkflowTask - let Mentalist plan dynamically
        team = TeamAgentFactory.create(
            name=f"OSINT Team - {sanitized_topic} ({unique_id})",
            description=f"OSINT research team for topic: {topic}",
            instructions=mentalist_instructions,
            agents=user_agents,  # User-defined agents (no WorkflowTask)
            llm_id=model_id,  # Model for micro agents (Mentalist, Inspector, etc.)
            use_mentalist=True,  # Enable Mentalist for dynamic planning
            use_inspector=True,  # Enable Inspector for quality review
            num_inspectors=1,  # One inspector
            inspector_targets=["steps", "output"]  # Inspect both steps and final output
        )
        
        logger.info(f"Created Team Agent with ID: {team.id}")
        logger.info(f"Team includes: Mentalist, Inspector, Orchestrator, Feedback Combiner, Response Generator (built-in)")
        agent_names = "Search Agent (with Tavily tool)"
        if wikipedia_agent:
            agent_names += ", Wikipedia Agent (with Wikipedia tool)"
        logger.info(f"User-defined agents: {agent_names}")
        logger.info(f"Inspector targets: steps and output")
        
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
        prompt = f"Research the following topic and extract key entities (Person, Organization):\n\n"
        prompt += f"Topic: {topic}\n\n"
        
        if goals:
            prompt += "Research Goals:\n"
            for i, goal in enumerate(goals, 1):
                prompt += f"{i}. {goal}\n"
            prompt += "\n"
        
        prompt += "Please provide a comprehensive report with:\n"
        prompt += "1. Person entities with their roles, descriptions, and source URLs\n"
        prompt += "2. Organization entities with their descriptions and source URLs\n"
        prompt += "3. Real source URLs with relevant excerpts for each entity\n"
        prompt += "\nNote: The Search Agent will handle the formatting. Focus on finding comprehensive, accurate information.\n"
        
        return prompt
