"""
aixplain Client Module for Honeycomb OSINT Agent Team System

This module wraps the aixplain SDK to provide agent creation and execution
functionality with error handling and retries.
"""
import logging
import time
from typing import Optional, Dict, Any
from aixplain.factories import AgentFactory
from aixplain.enums import Function

from api.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


class AgentClient:
    """
    Client for interacting with aixplain Agent API
    
    This class wraps the aixplain SDK and provides methods for:
    - Creating agents with specific configurations
    - Running agents with input prompts
    - Error handling with retries
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the aixplain client
        
        Args:
            api_key: aixplain API key (if None, loads from settings)
        """
        if api_key is None:
            settings = get_settings()
            api_key = settings.aixplain_api_key
        
        self.api_key = api_key
        logger.info("Initialized aixplain client")
    
    def create_agent(
        self,
        name: str,
        description: str,
        llm_id: str,
        instructions: str,
        tools: Optional[list] = None,
        max_retries: int = 3
    ) -> Any:
        """
        Create an agent using aixplain SDK
        
        Args:
            name: Agent name
            description: Agent description
            llm_id: LLM model ID (e.g., "gpt-4o-mini")
            instructions: Instructions/system prompt for the agent
            tools: List of tool IDs to attach to the agent
            max_retries: Maximum number of retry attempts
            
        Returns:
            Agent object from aixplain SDK
            
        Raises:
            Exception: If agent creation fails after retries
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Creating agent '{name}' (attempt {attempt + 1}/{max_retries})")
                
                # Create agent using aixplain SDK
                agent = AgentFactory.create(
                    name=name,
                    description=description,
                    llm_id=llm_id,
                    tools=tools or [],
                    instructions=instructions
                )
                
                logger.info(f"Successfully created agent '{name}' with ID: {agent.id}")
                return agent
                
            except Exception as e:
                logger.error(f"Failed to create agent (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to create agent after {max_retries} attempts")
                    raise
    
    def run_agent(
        self,
        agent: Any,
        input_text: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Run an agent with input text
        
        Args:
            agent: Agent object from aixplain SDK
            input_text: Input prompt for the agent
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing agent response with keys:
            - 'output': Agent's text response
            - 'status': Execution status
            - 'agent_id': Agent ID
            
        Raises:
            Exception: If agent execution fails after retries
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Running agent {agent.id} (attempt {attempt + 1}/{max_retries})")
                
                # Run agent using aixplain SDK
                response = agent.run(input_text)
                
                logger.info(f"Agent {agent.id} completed successfully")
                
                # Extract response data
                result = {
                    'output': response.get('data', ''),
                    'status': response.get('status', 'completed'),
                    'agent_id': agent.id
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to run agent (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to run agent after {max_retries} attempts")
                    raise
    
    def get_agent(self, agent_id: str) -> Any:
        """
        Get an existing agent by ID
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent object from aixplain SDK
            
        Raises:
            Exception: If agent retrieval fails
        """
        try:
            logger.info(f"Retrieving agent {agent_id}")
            agent = AgentFactory.get(agent_id)
            logger.info(f"Successfully retrieved agent {agent_id}")
            return agent
        except Exception as e:
            logger.error(f"Failed to retrieve agent {agent_id}: {e}")
            raise
    
    def get_run_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get intermediate status of a running agent/team
        
        This polls the aixplain API to get the current status and any intermediate
        results from a running agent execution.
        
        Args:
            request_id: The request ID returned from agent.run()
            
        Returns:
            Dictionary containing:
            - 'status': Current execution status (running, completed, failed)
            - 'completed': Boolean indicating if execution is complete
            - 'data': Any intermediate or final data available
            - 'intermediate_steps': List of steps completed so far
            - 'error': Error message if failed
            
        Raises:
            Exception: If status retrieval fails
        """
        try:
            import requests
            
            url = f"https://platform-api.aixplain.com/sdk/agents/{request_id}/result"
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            logger.info(f"Polling status for request {request_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Status for {request_id}: {result.get('status', 'unknown')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get run status for {request_id}: {e}")
            raise
