"""
Data models for Honeycomb OSINT API
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from uuid import uuid4


class CreateAgentTeamRequest(BaseModel):
    """Request model for creating an agent team"""
    topic: str = Field(..., description="Research topic")
    goals: List[str] = Field(..., description="Research goals")
    interaction_limit: Optional[int] = Field(50, description="Maximum interactions before returning results")
    mece_strategy: Optional[str] = Field("depth_first", description="MECE strategy (depth_first)")


class AgentTeamResponse(BaseModel):
    """Response model for agent team"""
    team_id: str = Field(..., description="Unique team identifier")
    status: str = Field(..., description="Team status (pending, running, completed, aborted)")
    created_at: datetime = Field(..., description="Creation timestamp")


class AgentTeamDetail(BaseModel):
    """Detailed agent team information"""
    model_config = {"arbitrary_types_allowed": True}
    
    team_id: str
    topic: str
    goals: List[str]
    status: str
    interaction_limit: int
    mece_strategy: str
    created_at: datetime
    updated_at: datetime
    execution_log: List = Field(default_factory=list)  # Can contain strings or dicts
    agent_response: Optional[dict] = Field(None, description="Agent execution response with output")
    sachstand: Optional[dict] = Field(None, description="JSON-LD Sachstand output")
    feedback: Optional[str] = Field(None, description="Helpful feedback about extraction results")


class AgentTeamSummary(BaseModel):
    """Summary information for agent team list"""
    team_id: str
    topic: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    entity_count: Optional[int] = Field(None, description="Number of entities extracted")
    sachstand: Optional[dict] = Field(None, description="JSON-LD Sachstand (for entity count)")


# Schema.org Entity Models for JSON-LD Output

class EntitySource(BaseModel):
    """Source information for an entity property"""
    url: str = Field(..., description="Source URL")
    accessed_at: Optional[datetime] = Field(None, description="When the source was accessed")
    excerpt: Optional[str] = Field(None, description="Relevant excerpt from source")


class PersonEntity(BaseModel):
    """Schema.org Person entity"""
    type: Literal["Person"] = Field(default="Person", description="Schema.org type")
    name: str = Field(..., description="Person's name")
    description: Optional[str] = Field(None, description="Description of the person")
    jobTitle: Optional[str] = Field(None, description="Job title")
    url: Optional[str] = Field(None, description="URL to person's page")
    sources: List[EntitySource] = Field(default_factory=list, description="Source URLs")
    sameAs: Optional[List[str]] = Field(None, description="Wikipedia and Wikidata URLs")
    wikidata_id: Optional[str] = Field(None, description="Wikidata identifier")
    wikipedia_links: Optional[List[dict]] = Field(None, description="Wikipedia links in multiple languages")


class OrganizationEntity(BaseModel):
    """Schema.org Organization entity"""
    type: Literal["Organization"] = Field(default="Organization", description="Schema.org type")
    name: str = Field(..., description="Organization's name")
    description: Optional[str] = Field(None, description="Description of the organization")
    url: Optional[str] = Field(None, description="URL to organization's page")
    sources: List[EntitySource] = Field(default_factory=list, description="Source URLs")
    sameAs: Optional[List[str]] = Field(None, description="Wikipedia and Wikidata URLs")
    wikidata_id: Optional[str] = Field(None, description="Wikidata identifier")
    wikipedia_links: Optional[List[dict]] = Field(None, description="Wikipedia links in multiple languages")


class JSONLDSachstand(BaseModel):
    """JSON-LD Sachstand output structure"""
    model_config = {"populate_by_name": True}
    
    context: str = Field("https://schema.org", alias="@context", description="JSON-LD context")
    type: Literal["ResearchReport"] = Field(default="ResearchReport", alias="@type", description="Schema.org type")
    name: str = Field(..., description="Report name")
    dateCreated: datetime = Field(..., description="Creation timestamp")
    about: dict = Field(..., description="Topic information")
    hasPart: List[dict] = Field(default_factory=list, description="Extracted entities")
    completionStatus: Literal["complete", "partial"] = Field(..., description="Completion status (complete or partial)")
