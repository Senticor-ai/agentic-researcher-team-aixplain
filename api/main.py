"""
Honeycomb OSINT Agent Team System - Main API Application
"""
import os
import json
import logging
import subprocess
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# Load environment variables FIRST
load_dotenv()

# Configure aixplain SDK before importing modules that use it
# The SDK expects TEAM_API_KEY environment variable
if os.getenv("AIXPLAIN_API_KEY") and not os.getenv("TEAM_API_KEY"):
    os.environ["TEAM_API_KEY"] = os.getenv("AIXPLAIN_API_KEY")

from api.models import (
    CreateAgentTeamRequest,
    AgentTeamResponse,
    AgentTeamSummary,
    AgentTeamDetail
)
from api.persistent_storage import get_store  # Changed from api.storage
from api.team_config import TeamConfig
from api.entity_processor import EntityProcessor
from api.search_strategy import generate_feedback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_git_info():
    """Get current git SHA and repo URL"""
    try:
        # Get current commit SHA
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], 
                                     stderr=subprocess.DEVNULL).decode('utf-8').strip()
        
        # Get remote URL
        remote_url = subprocess.check_output(['git', 'config', '--get', 'remote.origin.url'],
                                            stderr=subprocess.DEVNULL).decode('utf-8').strip()
        
        # Convert SSH URL to HTTPS if needed
        if remote_url.startswith('git@'):
            remote_url = remote_url.replace(':', '/').replace('git@', 'https://')
        if remote_url.endswith('.git'):
            remote_url = remote_url[:-4]
        
        return sha, remote_url
    except Exception as e:
        logger.warning(f"Failed to get git info: {e}")
        return None, None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Honeycomb OSINT API...")
    git_sha, git_repo = get_git_info()
    if git_sha:
        print(f"Running version: {git_sha[:8]}")
        if git_repo:
            print(f"Repository: {git_repo}")
    yield
    # Shutdown
    print("Shutting down Honeycomb OSINT API...")


# Create FastAPI application
app = FastAPI(
    title="Honeycomb OSINT Agent Team System",
    description="API for managing OSINT research agent teams",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",  # Vite alternate port
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "honeycomb-osint-api",
        "version": "0.1.0"
    }


async def run_team_task(team_id: str, topic: str, goals: list):
    """
    Background task to create and run the aixplain team agent
    
    Architecture:
    - Creates team with built-in micro agents (Mentalist, Inspector, Orchestrator, Response Generator)
    - Includes user-defined Search Agent with Tavily tool
    - Team coordinates research and entity extraction
    - API receives response and formats to JSON-LD
    
    Args:
        team_id: Team ID
        topic: Research topic
        goals: Research goals
    """
    store = get_store()
    
    try:
        # Update status to running
        store.update_team_status(team_id, "running")
        
        # Get interaction limit from team data
        team_data = store.get_team(team_id)
        interaction_limit = team_data.get("interaction_limit", 50)
        
        store.add_log_entry(team_id, f"Starting team creation for topic: {topic}")
        store.add_log_entry(team_id, f"Interaction limit: {interaction_limit} steps")
        logger.info(f"Team {team_id}: Creating team agent for topic: {topic}")
        logger.info(f"Team {team_id}: Interaction limit set to {interaction_limit}")
        
        # Create team agent with built-in micro agents and Search Agent
        # Uses default GPT-4o for all agents (configured in Config)
        team = TeamConfig.create_team(topic, goals)
        
        # Store team ID
        store.set_aixplain_agent_id(team_id, team.id)
        store.add_log_entry(team_id, f"Team created with ID: {team.id}")
        store.add_log_entry(team_id, "Team includes: Mentalist, Inspector, Orchestrator, Response Generator (built-in)")
        store.add_log_entry(team_id, "User-defined agents: Search Agent (Tavily)")
        logger.info(f"Team {team_id}: Team created with ID: {team.id}")
        
        # Format research prompt
        prompt = TeamConfig.format_research_prompt(topic, goals)
        store.add_log_entry(team_id, "Running team with research prompt")
        logger.info(f"Team {team_id}: Running team")
        
        # Run team in thread pool to avoid blocking the event loop
        # Mentalist will plan, Orchestrator will route to Search Agent,
        # Inspector will review, Response Generator will create final output
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, team.run, prompt)
        
        # Try to extract request_id for polling intermediate status
        request_id = None
        if hasattr(response, 'request_id'):
            request_id = response.request_id
        elif hasattr(response, 'id'):
            request_id = response.id
        elif hasattr(response, 'data') and hasattr(response.data, 'session_id'):
            request_id = response.data.session_id
        elif hasattr(response, 'data') and hasattr(response.data, 'sessionId'):
            request_id = response.data.sessionId
        
        if request_id:
            store.set_aixplain_agent_id(team_id, team.id, request_id)
            store.add_log_entry(team_id, f"Request ID: {request_id} (can be used for polling status)")
            logger.info(f"Team {team_id}: Request ID: {request_id}")
        else:
            logger.warning(f"Team {team_id}: Could not extract request_id from response")
        
        # Store response - convert aixplain objects to serializable format
        # Note: response.data is an AgentResponseData object with .output field
        output_data = None
        data_dict = None
        execution_stats = None
        
        if hasattr(response, 'data'):
            # Convert AgentResponseData to dict
            if hasattr(response.data, '__dict__'):
                data_dict = {
                    k: v for k, v in response.data.__dict__.items()
                    if not k.startswith('_') and not callable(v)
                }
            elif isinstance(response.data, str):
                data_dict = {"output": response.data}
            else:
                data_dict = {"raw": str(response.data)}
            
            # Extract output
            if hasattr(response.data, 'output'):
                output_data = response.data.output
            elif isinstance(response.data, str):
                output_data = response.data
            
            # Extract executionStats
            if hasattr(response.data, 'executionStats'):
                stats = response.data.executionStats
                if hasattr(stats, '__dict__'):
                    execution_stats = {
                        k: v for k, v in stats.__dict__.items()
                        if not k.startswith('_') and not callable(v)
                    }
                    logger.info(f"Team {team_id}: Extracted executionStats: {list(execution_stats.keys())}")
                    store.add_log_entry(team_id, f"Execution stats: {execution_stats.get('runtime', 'N/A')}s runtime, {execution_stats.get('credits', 'N/A')} credits, {execution_stats.get('apiCalls', 'N/A')} API calls")
                elif isinstance(stats, dict):
                    execution_stats = stats
                    logger.info(f"Team {team_id}: executionStats is dict: {list(execution_stats.keys())}")
        
        # Log intermediate steps for debugging
        intermediate_steps = []
        if hasattr(response, 'data') and hasattr(response.data, 'intermediate_steps'):
            # Convert intermediate steps to serializable format
            steps = response.data.intermediate_steps
            logger.info(f"Team {team_id}: Raw intermediate_steps type: {type(steps)}")
            if isinstance(steps, list):
                logger.info(f"Team {team_id}: Processing {len(steps)} steps")
                for idx, step in enumerate(steps):
                    logger.info(f"Team {team_id}: Step {idx+1} type: {type(step)}")
                    if isinstance(step, (str, dict, list, int, float, bool, type(None))):
                        intermediate_steps.append(step)
                    else:
                        # Try to extract useful info from complex objects
                        step_dict = {}
                        if hasattr(step, '__dict__'):
                            logger.info(f"Team {team_id}: Step {idx+1} attributes: {list(step.__dict__.keys())}")
                            for key, value in step.__dict__.items():
                                if not key.startswith('_') and not callable(value):
                                    # Serialize nested objects
                                    if isinstance(value, (str, int, float, bool, type(None))):
                                        step_dict[key] = value
                                    elif isinstance(value, (list, dict)):
                                        step_dict[key] = value
                                    else:
                                        step_dict[key] = str(value)
                        else:
                            step_dict = {"raw": str(step)}
                        logger.info(f"Team {team_id}: Step {idx+1} serialized keys: {list(step_dict.keys())}")
                        intermediate_steps.append(step_dict)
            store.add_log_entry(team_id, f"Team execution had {len(intermediate_steps)} intermediate steps")
            logger.info(f"Team {team_id}: {len(intermediate_steps)} intermediate steps")
        
        response_data = {
            "data": data_dict,
            "output": output_data,
            "completed": response.completed if hasattr(response, 'completed') else False,
            "intermediate_steps": intermediate_steps,
            "executionStats": execution_stats
        }
        store.set_agent_response(team_id, response_data)
        
        # Check if we got valid output
        if output_data is None:
            store.add_log_entry(team_id, "WARNING: Team returned None output")
            logger.warning(f"Team {team_id}: Team returned None output")
        else:
            store.add_log_entry(team_id, f"Team completed successfully")
            logger.info(f"Team {team_id}: Team completed successfully")
        
        # Receive entities from team response and generate JSON-LD Sachstand
        # Architecture: Team (via Response Generator) has created output, API formats to JSON-LD
        store.add_log_entry(team_id, "Receiving entities from team and generating JSON-LD Sachstand")
        logger.info(f"Team {team_id}: Formatting team response to JSON-LD")
        
        sachstand, mece_graph, validation_metrics = EntityProcessor.process_agent_response(
            agent_response=response_data,
            topic=topic,
            completion_status="complete"
        )
        
        # Log validation metrics
        if validation_metrics:
            store.add_log_entry(
                team_id, 
                f"Entity validation: {validation_metrics['valid_entities']}/{validation_metrics['total_entities']} "
                f"entities passed (avg quality: {validation_metrics['avg_quality_score']:.2f})"
            )
            if validation_metrics['rejected_entities'] > 0:
                store.add_log_entry(
                    team_id,
                    f"Rejected {validation_metrics['rejected_entities']} low-quality entities"
                )
            
            # Log deduplication stats
            if 'deduplication' in validation_metrics:
                dedup = validation_metrics['deduplication']
                if dedup['duplicates_found'] > 0:
                    store.add_log_entry(
                        team_id,
                        f"Entity deduplication: Removed {dedup['duplicates_found']} duplicates "
                        f"({dedup['original_count']} → {dedup['final_count']} entities)"
                    )
                    if dedup['wikidata_dedup'] > 0:
                        store.add_log_entry(
                            team_id,
                            f"Used Wikidata IDs for {dedup['wikidata_dedup']} authoritative deduplication(s)"
                        )
            
            logger.info(f"Team {team_id}: Validation metrics: {validation_metrics}")
        
        # Store MECE graph if available
        if mece_graph:
            store.set_mece_graph(team_id, mece_graph)
            store.add_log_entry(team_id, f"MECE decomposition applied: {mece_graph.get('applied', False)}")
            if mece_graph.get("applied"):
                store.add_log_entry(team_id, f"MECE dimensions: {', '.join(mece_graph.get('dimensions', []))}")
                store.add_log_entry(team_id, f"MECE completion: {mece_graph.get('completion_percentage', 0)}%")
            logger.info(f"Team {team_id}: Stored MECE graph")
        
        # Write JSON-LD to file
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"sachstand_{team_id}.jsonld"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sachstand, f, indent=2, ensure_ascii=False)
        
        store.add_log_entry(team_id, f"JSON-LD Sachstand written to {output_file}")
        logger.info(f"Team {team_id}: JSON-LD written to {output_file}")
        
        # Store sachstand in team data
        store.set_sachstand(team_id, sachstand)
        
        # Update status to completed
        store.update_team_status(team_id, "completed")
        
    except Exception as e:
        logger.error(f"Team {team_id}: Team execution failed: {e}")
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Team {team_id}: Error trace:\n{error_trace}")
        
        store.add_log_entry(team_id, f"Error: {str(e)}")
        store.add_log_entry(team_id, "Possible causes:")
        store.add_log_entry(team_id, "  - API key permissions issue")
        store.add_log_entry(team_id, "  - Tool (Tavily Search) not accessible")
        store.add_log_entry(team_id, "  - Agent configuration error")
        store.add_log_entry(team_id, "  - Network or timeout issue")
        store.update_team_status(team_id, "failed")


@app.post("/api/v1/agent-teams", response_model=AgentTeamResponse)
async def create_agent_team(request: CreateAgentTeamRequest, background_tasks: BackgroundTasks):
    """Create a new agent team for research"""
    from api.config import Config
    
    store = get_store()
    
    # Get git info
    git_sha, git_repo_url = get_git_info()
    
    # Get model info
    model_id = Config.TEAM_AGENT_MODEL
    model_name = Config.get_model_name(model_id)
    
    # Create team in storage
    team = store.create_team(
        topic=request.topic,
        goals=request.goals,
        interaction_limit=request.interaction_limit or 50,
        mece_strategy=request.mece_strategy or "depth_first",
        model_id=model_id,
        model_name=model_name,
        git_sha=git_sha,
        git_repo_url=git_repo_url
    )
    
    # Schedule team creation and execution in background
    background_tasks.add_task(
        run_team_task,
        team["team_id"],
        request.topic,
        request.goals
    )
    
    logger.info(f"Created team {team['team_id']} for topic: {request.topic}")
    
    return AgentTeamResponse(
        team_id=team["team_id"],
        status=team["status"],
        created_at=team["created_at"]
    )


@app.get("/api/v1/agent-teams", response_model=list[AgentTeamSummary])
async def list_agent_teams():
    """List all agent teams (sorted by created_at descending - newest first)"""
    store = get_store()
    teams = store.get_all_teams()  # Already sorted by created_at DESC
    
    return [
        AgentTeamSummary(
            team_id=team["team_id"],
            topic=team["topic"],
            status=team["status"],
            created_at=team["created_at"],
            updated_at=team.get("updated_at"),
            entity_count=len(team["sachstand"]["hasPart"]) if team.get("sachstand") and team["sachstand"].get("hasPart") else None,
            sachstand=team.get("sachstand")
        )
        for team in teams
    ]


@app.get("/api/v1/agent-teams/{team_id}", response_model=AgentTeamDetail)
async def get_agent_team(team_id: str):
    """Get detailed information about a specific agent team"""
    store = get_store()
    team = store.get_team(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail=f"Agent team {team_id} not found")
    
    # Generate helpful feedback based on results
    feedback = None
    if team["status"] == "completed":
        sachstand = team.get("sachstand", {})
        entities = sachstand.get("hasPart", [])
        entity_count = len(entities)
        feedback = generate_feedback(team["topic"], entity_count)
    
    return AgentTeamDetail(
        team_id=team["team_id"],
        topic=team["topic"],
        goals=team["goals"],
        status=team["status"],
        interaction_limit=team["interaction_limit"],
        mece_strategy=team["mece_strategy"],
        created_at=team["created_at"],
        updated_at=team["updated_at"],
        execution_log=team["execution_log"],
        agent_response=team.get("agent_response"),
        sachstand=team.get("sachstand"),
        feedback=feedback
    )


@app.get("/api/v1/sachstand/{team_id}")
async def get_sachstand(team_id: str):
    """Get JSON-LD Sachstand for a specific agent team"""
    store = get_store()
    team = store.get_team(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail=f"Agent team {team_id} not found")
    
    sachstand = team.get("sachstand")
    if not sachstand:
        raise HTTPException(status_code=404, detail=f"Sachstand not yet available for team {team_id}")
    
    # Also provide file path
    output_file = f"./output/sachstand_{team_id}.jsonld"
    
    return {
        "file_path": output_file,
        "content": sachstand
    }


@app.get("/api/v1/agent-teams/{team_id}/trace")
async def get_agent_trace(team_id: str):
    """Get detailed execution trace with intermediate steps for a specific agent team"""
    store = get_store()
    team = store.get_team(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail=f"Agent team {team_id} not found")
    
    agent_response = team.get("agent_response")
    if not agent_response:
        return {
            "team_id": team_id,
            "trace": [],
            "message": "No trace data available yet"
        }
    
    # Extract intermediate steps from agent response
    intermediate_steps = agent_response.get("intermediate_steps", [])
    
    # Format trace data for UI
    trace = []
    for idx, step in enumerate(intermediate_steps):
        step_data = {
            "step_number": idx + 1,
            "raw_data": step if isinstance(step, (str, dict)) else str(step)
        }
        
        # Try to parse structured data if available
        if isinstance(step, dict):
            # Extract agent information - try multiple field names
            agent_name = (
                step.get("agent_name") or 
                step.get("agent") or 
                step.get("name") or
                "Unknown Agent"
            )
            
            # Determine agent type from name
            agent_type = "unknown"
            agent_name_lower = agent_name.lower()
            if "mentalist" in agent_name_lower:
                agent_type = "mentalist"
            elif "orchestrator" in agent_name_lower:
                agent_type = "orchestrator"
            elif "inspector" in agent_name_lower:
                agent_type = "inspector"
            elif "search" in agent_name_lower:
                agent_type = "search"
            elif "response" in agent_name_lower or "generator" in agent_name_lower:
                agent_type = "response"
            
            step_data.update({
                "agent_name": agent_name,
                "agent_type": agent_type,
                "input": step.get("input") or step.get("task") or step.get("query"),
                "output": step.get("output") or step.get("result") or step.get("response"),
                "thought": step.get("thought") or step.get("reasoning"),
                "task": step.get("task") or step.get("assignment"),
                "tools": step.get("tools", []) or step.get("tool_calls", []),
                "runtime": step.get("runtime") or step.get("duration") or step.get("time"),
                "credits": step.get("credits") or step.get("cost"),
                "api_calls": step.get("api_calls") or step.get("calls")
            })
        elif isinstance(step, str):
            # Try to extract agent info from string representation
            step_str = step
            agent_name = "Unknown Agent"
            agent_type = "unknown"
            
            # Look for agent name patterns in string
            if "agent=" in step_str.lower() or "agent:" in step_str.lower():
                # Try to extract agent name
                import re
                match = re.search(r"agent[=:]\s*['\"]?([^'\">,\s]+)", step_str, re.IGNORECASE)
                if match:
                    agent_name = match.group(1)
            
            # Check for agent type keywords
            step_lower = step_str.lower()
            if "mentalist" in step_lower:
                agent_name = "Mentalist"
                agent_type = "mentalist"
            elif "orchestrator" in step_lower:
                agent_name = "Orchestrator"
                agent_type = "orchestrator"
            elif "inspector" in step_lower:
                agent_name = "Inspector"
                agent_type = "inspector"
            elif "search" in step_lower:
                agent_name = "Search Agent"
                agent_type = "search"
            elif "response" in step_lower or "generator" in step_lower:
                agent_name = "Response Generator"
                agent_type = "response"
            
            step_data.update({
                "agent_name": agent_name,
                "agent_type": agent_type,
                "message": step_str
            })
            
        trace.append(step_data)
    
    return {
        "team_id": team_id,
        "trace": trace,
        "total_steps": len(trace)
    }


def get_agent_configuration():
    """
    Get agent configuration from team_config
    
    This dynamically reads the configured agents and tools from Config.
    """
    from api.config import Config
    
    # Get configured tools
    configured_tools = {}
    tool_names = {
        "tavily_search": "Tavily Search",
        "google_search": "Google Search",
        "wikipedia": "Wikipedia"
    }
    
    for tool_key, tool_name in tool_names.items():
        if tool_key in Config.TOOL_IDS:
            configured_tools[tool_key] = {
                "name": tool_name,
                "id": Config.TOOL_IDS[tool_key]
            }
    
    # Get model configuration
    model_id = Config.TEAM_AGENT_MODEL
    model_name = Config.get_model_name(model_id)
    
    # Built-in agents (always present)
    built_in_agents = [
        {
            "name": "Mentalist",
            "role": "Strategic Planner",
            "description": "Analyzes the research topic and creates a dynamic research strategy using MECE decomposition for complex topics. Plans on-the-fly without following a fixed workflow, adapting to the specific needs of each research request.",
            "model": model_name,
            "capabilities": [
                "Topic analysis and complexity assessment",
                "MECE (Mutually Exclusive, Collectively Exhaustive) decomposition",
                "Dynamic research strategy planning",
                "Agent task coordination",
                "Adaptive workflow generation"
            ]
        },
        {
            "name": "Inspector",
            "role": "Quality Monitor",
            "description": "Reviews intermediate steps and final output to ensure quality, accuracy, and completeness. Provides feedback throughout execution to maintain high standards and catch issues early.",
            "model": model_name,
            "capabilities": [
                "Intermediate step quality review",
                "Final output validation",
                "Accuracy and completeness checking",
                "Entity quality assessment",
                "Source verification"
            ]
        },
        {
            "name": "Orchestrator",
            "role": "Agent Spawner & Task Router",
            "description": "Routes tasks to appropriate agents based on the Mentalist's dynamic plan. Spawns Search Agents, Wikipedia Agents, and other specialized agents as needed, managing their execution and collecting results.",
            "model": model_name,
            "capabilities": [
                "Dynamic agent spawning",
                "Task routing and distribution",
                "Agent execution management",
                "Result collection and aggregation",
                "Parallel task coordination"
            ]
        },
        {
            "name": "Feedback Combiner",
            "role": "Feedback Aggregator",
            "description": "Consolidates inspection feedback from multiple reviewers and inspection points. Synthesizes feedback into actionable insights for improving output quality and addressing identified issues.",
            "model": model_name,
            "capabilities": [
                "Multi-source feedback aggregation",
                "Feedback prioritization",
                "Actionable insight generation",
                "Quality improvement recommendations",
                "Issue tracking and resolution"
            ]
        },
        {
            "name": "Response Generator",
            "role": "Output Synthesizer",
            "description": "Creates the final structured JSON-LD Sachstand output from all agent results. Synthesizes information from Search Agents, Wikipedia Agents, and other sources into a cohesive, well-formatted report.",
            "model": model_name,
            "capabilities": [
                "Multi-agent result synthesis",
                "JSON-LD Sachstand generation",
                "Entity deduplication and merging",
                "Source attribution and citation",
                "Structured output formatting"
            ]
        }
    ]
    
    # User-defined agents (dynamically configured based on available tools)
    # Each tool gets its own card
    user_defined_agents = []
    
    # Tavily Search Tool
    if "tavily_search" in configured_tools:
        user_defined_agents.append({
            "name": "Tavily Search",
            "role": "AI-Optimized Web Search",
            "tool_id": configured_tools["tavily_search"]["id"],
            "description": "AI-optimized web search tool designed for research agents. Provides high-quality, curated search results with focus on relevance and accuracy. Primary search tool for OSINT research and entity extraction.",
            "model": model_name,
            "capabilities": [
                "AI-optimized web search with curated results",
                "High relevance and accuracy filtering",
                "Person and Organization entity discovery",
                "Real source URLs and excerpts",
                "German and English language support",
                "Government and official source prioritization"
            ],
            "used_by": "Search Agent"
        })
    
    # Google Search Tool
    if "google_search" in configured_tools:
        user_defined_agents.append({
            "name": "Google Search",
            "role": "Comprehensive Web Search",
            "tool_id": configured_tools["google_search"]["id"],
            "description": "Comprehensive web search powered by Google via Scale SERP. Provides broad coverage across the entire web with deep indexing of government sites, official sources, and regional content. Excellent for German regional topics.",
            "model": model_name,
            "capabilities": [
                "Comprehensive web coverage and deep indexing",
                "Excellent German regional content coverage",
                "Government and official website indexing",
                "Historical and archived content access",
                "Broad source diversity",
                "Regional and local organization discovery"
            ],
            "used_by": "Search Agent",
            "cost_per_request": "$0.0008"
        })
    
    # Wikipedia Tool
    if "wikipedia" in configured_tools:
        user_defined_agents.append({
            "name": "Wikipedia",
            "role": "Entity Enrichment & Verification",
            "tool_id": configured_tools["wikipedia"]["id"],
            "description": "Wikipedia API for entity verification, enrichment, and authoritative linking. Retrieves Wikipedia articles in multiple languages and extracts Wikidata IDs for entity deduplication and cross-referencing.",
            "model": model_name,
            "capabilities": [
                "Wikipedia entity verification and lookup",
                "Multi-language Wikipedia URL retrieval (de, en, fr)",
                "Wikidata ID extraction for authoritative linking",
                "sameAs property generation for deduplication",
                "Entity cross-referencing and validation",
                "Authoritative source attribution"
            ],
            "languages_supported": ["de", "en", "fr"],
            "used_by": "Wikipedia Agent"
        })
    
    return {
        "team_structure": "Built-in micro agents + User-defined agents",
        "built_in_agents": built_in_agents,
        "user_defined_agents": user_defined_agents,
        "configured_tools": configured_tools,
        "default_model": model_name,
        "model_id": model_id,
        "coordination": {
            "approach": "Dynamic Planning",
            "description": "No predefined workflow - agents coordinate dynamically based on the research needs",
            "roles": [
                {
                    "agent": "Mentalist",
                    "responsibility": "Analyzes topic and creates dynamic research strategy",
                    "note": "Plans on-the-fly, not following a fixed workflow"
                },
                {
                    "agent": "Orchestrator",
                    "responsibility": "Routes tasks to appropriate agents based on Mentalist's plan",
                    "note": "Spawns agents as needed, not in a predetermined sequence"
                },
                {
                    "agent": "Search Agent",
                    "responsibility": "Executes research tasks when called by Orchestrator",
                    "note": "May be invoked multiple times for different aspects"
                },
                {
                    "agent": "Wikipedia Agent",
                    "responsibility": "Enriches extracted entities with Wikipedia links and Wikidata IDs",
                    "note": "Called after entity extraction to add authoritative references"
                },
                {
                    "agent": "Inspector",
                    "responsibility": "Reviews steps and output for quality",
                    "note": "Provides feedback throughout execution"
                },
                {
                    "agent": "Feedback Combiner",
                    "responsibility": "Aggregates inspection feedback",
                    "note": "Consolidates reviews from multiple inspection points"
                },
                {
                    "agent": "Response Generator",
                    "responsibility": "Synthesizes final output from all agent results",
                    "note": "Creates structured JSON-LD Sachstand"
                }
            ]
        },
        "default_settings": {
            "interaction_limit": 50,
            "mece_strategy": "depth_first",
            "inspector_targets": ["steps", "output"],
            "num_inspectors": 1
        }
    }


@app.get("/api/v1/agent-configuration")
async def get_agent_configuration_endpoint():
    """
    Get current agent configuration
    
    Returns the dynamically configured agents based on team_config.py
    """
    return get_agent_configuration()


@app.get("/api/v1/debug/search-agent-instructions")
async def get_search_agent_instructions_debug(topic: str = "Test Topic"):
    """
    Debug endpoint to see the exact instructions being sent to Search Agent
    
    Query Parameters:
        - topic: Topic to use for generating instructions (default: "Test Topic")
    
    Returns:
        Full instructions that would be sent to the Search Agent
    """
    from api.instructions.search_agent import get_search_agent_instructions
    from api.search_strategy import enhance_instructions
    
    # Get base instructions
    base_instructions = get_search_agent_instructions(topic)
    
    # Enhance with fallback strategies
    enhanced_instructions = enhance_instructions(topic, base_instructions)
    
    return {
        "topic": topic,
        "instructions_length": len(enhanced_instructions),
        "has_text_format": "PERSON: [Name]" in enhanced_instructions,
        "has_json_format": '"type": "Person"' in enhanced_instructions,
        "output_format_section": enhanced_instructions[enhanced_instructions.index("OUTPUT FORMAT"):enhanced_instructions.index("OUTPUT FORMAT")+500] if "OUTPUT FORMAT" in enhanced_instructions else "NOT FOUND",
        "full_instructions": enhanced_instructions
    }


@app.get("/api/v1/debug/team-config")
async def get_team_config_debug(topic: str = "Test Topic"):
    """
    Debug endpoint to see how a team would be configured
    
    Query Parameters:
        - topic: Topic to use for team configuration (default: "Test Topic")
    
    Returns:
        Team configuration details including agents and tools
    """
    from api.config import Config
    
    return {
        "topic": topic,
        "configured_tools": {
            "tavily_search": Config.TOOL_IDS.get("tavily_search"),
            "google_search": Config.TOOL_IDS.get("google_search"),
            "wikipedia": Config.TOOL_IDS.get("wikipedia")
        },
        "default_model": Config.get_model_id(),
        "model_options": Config.MODELS,
        "note": "This shows what tools and models are configured. Use /debug/search-agent-instructions to see agent instructions."
    }


@app.get("/api/v1/agent-teams/{team_id}/mece-graph")
async def get_mece_graph(team_id: str):
    """Get MECE decomposition graph for a specific agent team"""
    store = get_store()
    team = store.get_team(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail=f"Agent team {team_id} not found")
    
    mece_graph = team.get("mece_graph")
    
    if not mece_graph:
        return {
            "team_id": team_id,
            "mece_applied": False,
            "message": "No MECE decomposition was applied for this topic"
        }
    
    return {
        "team_id": team_id,
        "mece_applied": mece_graph.get("applied", False),
        "mece_graph": mece_graph
    }


@app.get("/api/v1/agent-teams/{team_id}/status")
async def get_team_status(team_id: str):
    """
    Get real-time status of a running agent team
    
    This endpoint polls the aixplain API to get intermediate status updates
    while the team is running. Useful for monitoring progress in real-time.
    
    Returns:
        - status: Current execution status (pending, running, completed, failed)
        - completed: Boolean indicating if execution is complete
        - intermediate_data: Any intermediate results available
        - message: Status message
    """
    store = get_store()
    team = store.get_team(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail=f"Agent team {team_id} not found")
    
    # Get current status from database
    current_status = team.get("status")
    
    # If already completed or failed, return stored data
    if current_status in ["completed", "failed", "aborted"]:
        return {
            "team_id": team_id,
            "status": current_status,
            "completed": True,
            "message": f"Team execution {current_status}",
            "agent_response": team.get("agent_response"),
            "sachstand": team.get("sachstand"),
            "mece_graph": team.get("mece_graph")
        }
    
    # Try to get request_id for polling
    request_id = store.get_request_id(team_id)
    
    if not request_id:
        # No request_id available yet, return current status
        return {
            "team_id": team_id,
            "status": current_status,
            "completed": False,
            "message": "Team is being initialized, no request ID available yet"
        }
    
    # Poll aixplain API for intermediate status
    try:
        from api.aixplain_client import AgentClient
        client = AgentClient()
        
        run_status = client.get_run_status(request_id)
        
        return {
            "team_id": team_id,
            "status": run_status.get("status", current_status),
            "completed": run_status.get("completed", False),
            "intermediate_data": run_status.get("data"),
            "intermediate_steps": run_status.get("intermediate_steps", []),
            "message": "Retrieved intermediate status from aixplain API"
        }
        
    except Exception as e:
        logger.error(f"Failed to poll aixplain API for team {team_id}: {e}")
        # Fallback to database status
        return {
            "team_id": team_id,
            "status": current_status,
            "completed": False,
            "message": f"Could not retrieve intermediate status: {str(e)}",
            "error": str(e)
        }


@app.get("/api/v1/agent-teams/{team_id}/execution-stats")
async def get_execution_stats(team_id: str):
    """Get execution statistics and agent configuration for a specific agent team"""
    store = get_store()
    team = store.get_team(team_id)
    
    if not team:
        raise HTTPException(status_code=404, detail=f"Agent team {team_id} not found")
    
    agent_response = team.get("agent_response")
    
    # Build stats from available data
    stats = {
        "team_id": team_id,
        "overall_stats": {
            "status": team.get("status"),
            "created_at": team.get("created_at"),
            "updated_at": team.get("updated_at"),
            "interaction_limit": team.get("interaction_limit"),
            "mece_strategy": team.get("mece_strategy")
        },
        "agent_configuration": get_agent_configuration(),
        "execution_data": None
    }
    
    # Add execution data if available
    if agent_response:
        execution_data = {
            "completed": agent_response.get("completed", False),
            "has_output": agent_response.get("output") is not None,
            "intermediate_steps_count": len(agent_response.get("intermediate_steps", []))
        }
        
        # Extract executionStats if available
        execution_stats = agent_response.get("executionStats")
        if execution_stats:
            execution_data.update({
                "status": execution_stats.get("status"),
                "runtime": execution_stats.get("runtime"),
                "credits": execution_stats.get("credits"),
                "api_calls": execution_stats.get("apiCalls"),
                "session_id": execution_stats.get("sessionId"),
                "environment": execution_stats.get("environment"),
                "timestamp": execution_stats.get("timeStamp"),
                "assets_used": execution_stats.get("assetsUsed", []),
                "api_call_breakdown": execution_stats.get("apiCallBreakdown", {}),
                "runtime_breakdown": execution_stats.get("runtimeBreakdown", {}),
                "credit_breakdown": execution_stats.get("creditBreakdown", {}),
                "params": execution_stats.get("params", {})
            })
        
        # Fallback: Try to extract from response data
        if isinstance(agent_response.get("data"), dict):
            data = agent_response["data"]
            if not execution_data.get("session_id"):
                execution_data["session_id"] = data.get("session_id") or data.get("sessionId")
            if not execution_data.get("environment"):
                execution_data["environment"] = data.get("environment", "production")
        
        stats["execution_data"] = execution_data
    
    # Add plan from Mentalist if available in logs
    execution_log = team.get("execution_log", [])
    plan_entries = [log for log in execution_log if isinstance(log, str) and 'plan' in log.lower()]
    if plan_entries:
        stats["mentalist_plan"] = {
            "available": True,
            "entries": plan_entries[:5]  # First 5 plan-related entries
        }
    
    return stats


@app.get("/api/v1/stats/export")
async def export_stats(
    format: str = "csv",
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Export execution statistics for multiple teams
    
    Query Parameters:
        - format: Export format (csv or json)
        - status: Filter by team status (pending, running, completed, failed)
        - start_date: Filter teams created after this date (ISO format)
        - end_date: Filter teams created before this date (ISO format)
    """
    from fastapi.responses import Response
    
    store = get_store()
    teams = store.get_all_teams()
    
    # Apply filters
    filtered_teams = teams
    
    if status:
        filtered_teams = [t for t in filtered_teams if t.get("status") == status]
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            filtered_teams = [t for t in filtered_teams if t.get("created_at") >= start_dt]
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            filtered_teams = [t for t in filtered_teams if t.get("created_at") <= end_dt]
        except ValueError:
            pass
    
    # Collect stats for each team
    export_data = []
    for team in filtered_teams:
        agent_response = team.get("agent_response")
        execution_stats = agent_response.get("executionStats") if agent_response else None
        sachstand = team.get("sachstand")
        entity_count = len(sachstand.get("hasPart", [])) if sachstand else 0
        
        team_stats = {
            "team_id": team["team_id"],
            "topic": team["topic"],
            "status": team["status"],
            "created_at": team["created_at"].isoformat() if isinstance(team["created_at"], datetime) else team["created_at"],
            "updated_at": team["updated_at"].isoformat() if isinstance(team["updated_at"], datetime) else team["updated_at"],
            "runtime": execution_stats.get("runtime") if execution_stats else None,
            "credits": execution_stats.get("credits") if execution_stats else None,
            "api_calls": execution_stats.get("apiCalls") if execution_stats else None,
            "entity_count": entity_count,
            "cost_per_entity": (execution_stats.get("credits") / entity_count) if execution_stats and entity_count > 0 else None
        }
        export_data.append(team_stats)
    
    if format.lower() == "csv":
        # Generate CSV
        import csv
        from io import StringIO
        
        output = StringIO()
        if export_data:
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
            writer.writeheader()
            writer.writerows(export_data)
        
        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=team_stats_export.csv"}
        )
    else:
        # Return JSON
        return Response(
            content=json.dumps(export_data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=team_stats_export.json"}
        )


@app.get("/api/v1/stats/aggregate")
async def get_aggregate_stats(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get aggregate execution statistics across all teams
    
    Query Parameters:
        - status: Filter by team status (pending, running, completed, failed)
        - start_date: Filter teams created after this date (ISO format)
        - end_date: Filter teams created before this date (ISO format)
    """
    store = get_store()
    teams = store.get_all_teams()
    
    # Apply filters
    filtered_teams = teams
    
    if status:
        filtered_teams = [t for t in filtered_teams if t.get("status") == status]
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            filtered_teams = [t for t in filtered_teams if t.get("created_at") >= start_dt]
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            filtered_teams = [t for t in filtered_teams if t.get("created_at") <= end_dt]
        except ValueError:
            pass
    
    # Calculate aggregate statistics
    total_teams = len(filtered_teams)
    total_runtime = 0
    total_credits = 0
    total_api_calls = 0
    total_entities = 0
    completed_teams = []
    top_consumers = []
    
    for team in filtered_teams:
        # Extract execution stats
        agent_response = team.get("agent_response")
        if agent_response:
            execution_stats = agent_response.get("executionStats")
            if execution_stats:
                runtime = execution_stats.get("runtime", 0)
                credits = execution_stats.get("credits", 0)
                api_calls = execution_stats.get("apiCalls", 0)
                
                total_runtime += runtime or 0
                total_credits += credits or 0
                total_api_calls += api_calls or 0
                
                # Track for top consumers
                if runtime or credits or api_calls:
                    top_consumers.append({
                        "team_id": team["team_id"],
                        "topic": team["topic"],
                        "runtime": runtime or 0,
                        "credits": credits or 0,
                        "api_calls": api_calls or 0,
                        "created_at": team["created_at"]
                    })
        
        # Count entities
        sachstand = team.get("sachstand")
        if sachstand and sachstand.get("hasPart"):
            total_entities += len(sachstand["hasPart"])
        
        # Track completed teams for trends
        if team.get("status") == "completed":
            # Safely get execution stats
            exec_stats = {}
            if agent_response and isinstance(agent_response, dict):
                exec_stats = agent_response.get("executionStats", {})
            
            completed_teams.append({
                "team_id": team["team_id"],
                "created_at": team["created_at"],
                "runtime": exec_stats.get("runtime", 0) if exec_stats else 0,
                "credits": exec_stats.get("credits", 0) if exec_stats else 0
            })
    
    # Sort top consumers by credits (descending)
    top_consumers.sort(key=lambda x: x["credits"], reverse=True)
    top_consumers = top_consumers[:10]  # Top 10
    
    # Calculate averages
    avg_runtime = total_runtime / total_teams if total_teams > 0 else 0
    avg_credits = total_credits / total_teams if total_teams > 0 else 0
    avg_api_calls = total_api_calls / total_teams if total_teams > 0 else 0
    avg_entities = total_entities / total_teams if total_teams > 0 else 0
    
    # Cost trends over time (group by date)
    cost_trends = {}
    for team in completed_teams:
        date_key = team["created_at"].strftime("%Y-%m-%d")
        if date_key not in cost_trends:
            cost_trends[date_key] = {"runtime": 0, "credits": 0, "count": 0}
        cost_trends[date_key]["runtime"] += team["runtime"]
        cost_trends[date_key]["credits"] += team["credits"]
        cost_trends[date_key]["count"] += 1
    
    # Convert to list and sort by date
    cost_trends_list = [
        {
            "date": date,
            "runtime": data["runtime"],
            "credits": data["credits"],
            "count": data["count"],
            "avg_runtime": data["runtime"] / data["count"] if data["count"] > 0 else 0,
            "avg_credits": data["credits"] / data["count"] if data["count"] > 0 else 0
        }
        for date, data in sorted(cost_trends.items())
    ]
    
    return {
        "total_teams": total_teams,
        "total_runtime": round(total_runtime, 2),
        "total_credits": round(total_credits, 2),
        "total_api_calls": total_api_calls,
        "total_entities": total_entities,
        "avg_runtime": round(avg_runtime, 2),
        "avg_credits": round(avg_credits, 2),
        "avg_api_calls": round(avg_api_calls, 2),
        "avg_entities": round(avg_entities, 2),
        "top_consumers": top_consumers,
        "cost_trends": cost_trends_list,
        "filters_applied": {
            "status": status,
            "start_date": start_date,
            "end_date": end_date
        }
    }


if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=True
    )
