import { Card, Tag, Intent, Collapse, Button, Spinner } from '@blueprintjs/core';
import { useState, useEffect } from 'react';
import { agentTeamsAPI } from '../api/client';
import './TeamConfigInfo.css';

function TeamConfigInfo() {
  const [isExpanded, setIsExpanded] = useState(false);
  const [agentConfig, setAgentConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch agent configuration from API
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const response = await agentTeamsAPI.getAgentConfiguration();
        setAgentConfig(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch agent configuration:', err);
        setError('Failed to load agent configuration');
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  // Map API response to display format
  const getDisplayConfig = () => {
    if (!agentConfig) {
      return null;
    }

    return {
      model: agentConfig.default_model || agentConfig.model || "GPT-4o Mini (Testing Mode)",
      builtInAgents: agentConfig.built_in_agents?.map(agent => ({
        name: agent.name,
        role: agent.role,
        description: agent.description,
        model: agent.model,
        capabilities: agent.capabilities || [],
        icon: getAgentIcon(agent.name),
        color: getAgentColor(agent.name)
      })) || [],
      userDefinedAgents: agentConfig.user_defined_agents?.map(agent => ({
        name: agent.name,
        role: agent.role,
        description: agent.description,
        model: agent.model,
        tools: agent.tools || [],
        capabilities: agent.capabilities || getAgentCapabilities(agent.name),
        searchStrategy: agent.search_strategy,
        languagesSupported: agent.languages_supported,
        icon: getAgentIcon(agent.name),
        color: getAgentColor(agent.name)
      })) || []
    };
  };

  // Helper functions for display
  const getAgentIcon = (name) => {
    const icons = {
      'Mentalist': '🧠',
      'Inspector': '🔍',
      'Orchestrator': '🎯',
      'Feedback Combiner': '📊',
      'Response Generator': '📝',
      'Search Agent': '🔎',
      'Wikipedia Agent': '📚'
    };
    return icons[name] || '🤖';
  };

  const getAgentColor = (name) => {
    const colors = {
      'Mentalist': '#9b59b6',
      'Inspector': '#e74c3c',
      'Orchestrator': '#3498db',
      'Feedback Combiner': '#1abc9c',
      'Response Generator': '#f39c12',
      'Search Agent': '#2ecc71',
      'Wikipedia Agent': '#e67e22'
    };
    return colors[name] || '#95a5a6';
  };

  const getAgentCapabilities = (name) => {
    const capabilities = {
      'Search Agent': [
        "Multi-source web search for comprehensive coverage",
        "Person and Organization entity extraction",
        "Real source URLs and excerpts citation",
        "German and English language search support",
        "Intelligent search strategy optimization",
        "Government and official source prioritization"
      ],
      'Wikipedia Agent': [
        "Wikipedia entity verification and lookup",
        "Multi-language Wikipedia URL retrieval (de, en, fr)",
        "Wikidata ID extraction for authoritative linking",
        "sameAs property generation for deduplication",
        "Entity cross-referencing and validation",
        "Authoritative source attribution"
      ]
    };
    return capabilities[name] || [];
  };

  const displayConfig = getDisplayConfig();

  // Default config structure for fallback
  const teamConfig = {
    model: {
      testing: "GPT-4o Mini",
      production: "GPT-4o",
      current: "GPT-4o Mini (Testing Mode)"
    },
    builtInAgents: [
      {
        name: "Mentalist",
        role: "Strategic Planner",
        description: "Plans research strategy and coordinates the team dynamically",
        icon: "🧠",
        color: "#9b59b6"
      },
      {
        name: "Inspector",
        role: "Quality Monitor",
        description: "Reviews intermediate steps and final output for quality assurance",
        icon: "🔍",
        color: "#e74c3c"
      },
      {
        name: "Orchestrator",
        role: "Agent Spawner",
        description: "Routes tasks to appropriate agents based on Mentalist's plan",
        icon: "🎯",
        color: "#3498db"
      },
      {
        name: "Feedback Combiner",
        role: "Feedback Aggregator",
        description: "Consolidates inspection feedback from multiple reviewers",
        icon: "📊",
        color: "#1abc9c"
      },
      {
        name: "Response Generator",
        role: "Output Synthesizer",
        description: "Creates final structured output from agent results",
        icon: "📝",
        color: "#f39c12"
      }
    ],
    userDefinedAgents: [
      {
        name: "Search Agent",
        description: "OSINT research agent with multiple search tools for comprehensive coverage",
        tools: ["Tavily Search", "Google Search"],
        capabilities: [
          "Multi-source web search for comprehensive coverage",
          "Person and Organization entity extraction",
          "Real source URLs and excerpts citation",
          "German and English language search support",
          "Intelligent search strategy optimization",
          "Government and official source prioritization"
        ],
        icon: "🔎",
        color: "#2ecc71"
      },
      {
        name: "Wikipedia Agent",
        description: "Entity enrichment agent with Wikipedia tool",
        tools: ["Wikipedia API"],
        capabilities: [
          "Search Wikipedia for entity verification",
          "Retrieve Wikipedia URLs in multiple languages (de, en, fr)",
          "Extract Wikidata IDs for entity linking",
          "Add sameAs properties for deduplication"
        ],
        icon: "📚",
        color: "#e67e22"
      }
    ],
    coordination: {
      approach: "Dynamic Planning",
      description: "No predefined workflow - agents coordinate dynamically based on the research needs",
      roles: [
        {
          agent: "Mentalist",
          responsibility: "Analyzes topic and creates dynamic research strategy",
          note: "Plans on-the-fly, not following a fixed workflow"
        },
        {
          agent: "Orchestrator",
          responsibility: "Routes tasks to appropriate agents based on Mentalist's plan",
          note: "Spawns agents as needed, not in a predetermined sequence"
        },
        {
          agent: "Search Agent",
          responsibility: "Executes research tasks when called by Orchestrator",
          note: "May be invoked multiple times for different aspects"
        },
        {
          agent: "Wikipedia Agent",
          responsibility: "Enriches extracted entities with Wikipedia links and Wikidata IDs",
          note: "Called after entity extraction to add authoritative references"
        },
        {
          agent: "Inspector",
          responsibility: "Reviews steps and output for quality",
          note: "Provides feedback throughout execution"
        },
        {
          agent: "Feedback Combiner",
          responsibility: "Aggregates inspection feedback",
          note: "Consolidates reviews from multiple inspection points"
        },
        {
          agent: "Response Generator",
          responsibility: "Synthesizes final output from all agent results",
          note: "Creates structured JSON-LD Sachstand"
        }
      ]
    },
    defaultSettings: {
      interactionLimit: 50,
      meceStrategy: "depth_first",
      inspectorTargets: ["steps", "output"],
      numInspectors: 1
    }
  };

  if (loading) {
    return (
      <Card className="team-config-info">
        <div className="config-header">
          <h3>🤖 Agent Team Configuration</h3>
        </div>
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <Spinner size={40} />
          <p style={{ marginTop: '1rem', color: '#666' }}>Loading agent configuration...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="team-config-info">
        <div className="config-header">
          <h3>🤖 Agent Team Configuration</h3>
        </div>
        <div style={{ textAlign: 'center', padding: '2rem', color: '#e74c3c' }}>
          <p>⚠️ {error}</p>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
            Using fallback configuration
          </p>
        </div>
      </Card>
    );
  }

  const config = displayConfig || teamConfig;

  return (
    <Card className="team-config-info">
      <div className="config-header">
        <div className="config-title-section">
          <h3>🤖 Agent Team Configuration</h3>
          <Tag intent={Intent.SUCCESS} large>
            Live Configuration
          </Tag>
        </div>
        <Button
          minimal
          icon={isExpanded ? 'chevron-up' : 'chevron-down'}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? 'Hide Details' : 'Show Details'}
        </Button>
      </div>

      <div className="config-summary">
        <div className="summary-item">
          <span className="summary-icon">🤖</span>
          <div className="summary-content">
            <div className="summary-label">Model</div>
            <div className="summary-value">{config.model?.current || config.model}</div>
          </div>
        </div>
        <div className="summary-item">
          <span className="summary-icon">👥</span>
          <div className="summary-content">
            <div className="summary-label">Built-in Agents</div>
            <div className="summary-value">{config.builtInAgents?.length || 0} Micro Agents</div>
          </div>
        </div>
        <div className="summary-item">
          <span className="summary-icon">🔧</span>
          <div className="summary-content">
            <div className="summary-label">Custom Agents</div>
            <div className="summary-value">
              {config.userDefinedAgents?.length || 0} Agent{config.userDefinedAgents?.length !== 1 ? 's' : ''}
              {config.userDefinedAgents?.length > 0 && (
                <span style={{ fontSize: '0.85em', color: '#666' }}>
                  {' '}({config.userDefinedAgents.map(a => a.name.replace(' Agent', '')).join(' + ')})
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="summary-item">
          <span className="summary-icon">⚙️</span>
          <div className="summary-content">
            <div className="summary-label">Interaction Limit</div>
            <div className="summary-value">{teamConfig.defaultSettings?.interactionLimit || 50} steps</div>
          </div>
        </div>
      </div>

      <Collapse isOpen={isExpanded}>
        <div className="config-details">
          {/* Built-in Agents */}
          <div className="config-section">
            <h4>Built-in Micro Agents</h4>
            <p className="section-description">
              These agents are automatically included in every team and handle coordination, quality control, and output generation.
            </p>
            <div className="agents-grid">
              {config.builtInAgents?.map((agent, idx) => (
                <div key={idx} className="agent-card" style={{ borderLeftColor: agent.color }}>
                  <div className="agent-header">
                    <span className="agent-icon">{agent.icon}</span>
                    <div className="agent-info">
                      <div className="agent-name">{agent.name}</div>
                      <div className="agent-role" style={{ color: agent.color }}>
                        {agent.role}
                      </div>
                    </div>
                  </div>
                  <div className="agent-description">{agent.description}</div>
                  {agent.model && (
                    <div className="agent-model">
                      <Tag minimal small intent={Intent.PRIMARY}>
                        {agent.model}
                      </Tag>
                    </div>
                  )}
                  {agent.capabilities && agent.capabilities.length > 0 && (
                    <div className="agent-capabilities">
                      <strong>Capabilities:</strong>
                      <ul>
                        {agent.capabilities.map((cap, cidx) => (
                          <li key={cidx}>{cap}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* User-Defined Agents */}
          <div className="config-section">
            <h4>User-Defined Agents</h4>
            <p className="section-description">
              Custom agents with specialized tools for OSINT research and entity extraction.
            </p>
            <div className="agents-grid">
              {config.userDefinedAgents?.map((agent, idx) => (
                <div key={idx} className="agent-card custom-agent" style={{ borderLeftColor: agent.color }}>
                  <div className="agent-header">
                    <span className="agent-icon">{agent.icon}</span>
                    <div className="agent-info">
                      <div className="agent-name">{agent.name}</div>
                      {agent.role && (
                        <div className="agent-role" style={{ color: agent.color }}>
                          {agent.role}
                        </div>
                      )}
                      <div className="agent-tools">
                        {agent.tools.map((tool, tidx) => (
                          <Tag key={tidx} minimal small>
                            {tool}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="agent-description">{agent.description}</div>
                  {agent.model && (
                    <div className="agent-model">
                      <Tag minimal small intent={Intent.PRIMARY}>
                        {agent.model}
                      </Tag>
                    </div>
                  )}
                  {agent.searchStrategy && (
                    <div className="agent-strategy">
                      <strong>Search Strategy:</strong> {agent.searchStrategy}
                    </div>
                  )}
                  {agent.languagesSupported && (
                    <div className="agent-languages">
                      <strong>Languages:</strong> {agent.languagesSupported.join(', ')}
                    </div>
                  )}
                  {agent.capabilities && agent.capabilities.length > 0 && (
                    <div className="agent-capabilities">
                      <strong>Capabilities:</strong>
                      <ul>
                        {agent.capabilities.map((cap, cidx) => (
                          <li key={cidx}>{cap}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Coordination Approach */}
          <div className="config-section">
            <h4>🔄 {teamConfig.coordination.approach}</h4>
            <p className="section-description">
              {teamConfig.coordination.description}
            </p>
            <div className="coordination-info">
              <div className="coordination-note">
                <strong>⚠️ Important:</strong> Unlike traditional workflows, this team does NOT follow a predefined sequence. 
                The Mentalist plans dynamically based on the research topic, and the Orchestrator coordinates agents as needed. 
                This allows for flexible, adaptive research strategies.
              </div>
              <div className="roles-list">
                {teamConfig.coordination.roles.map((role, idx) => (
                  <div key={idx} className="role-item">
                    <div className="role-header">
                      <span className="role-agent">{role.agent}</span>
                      <Tag minimal small intent={Intent.PRIMARY}>
                        Dynamic
                      </Tag>
                    </div>
                    <div className="role-responsibility">{role.responsibility}</div>
                    <div className="role-note">💡 {role.note}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Default Settings */}
          <div className="config-section">
            <h4>Default Settings</h4>
            <div className="settings-grid">
              <div className="setting-item">
                <span className="setting-label">Interaction Limit:</span>
                <span className="setting-value">{teamConfig.defaultSettings.interactionLimit} steps</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">MECE Strategy:</span>
                <span className="setting-value">{teamConfig.defaultSettings.meceStrategy}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Inspector Targets:</span>
                <span className="setting-value">{teamConfig.defaultSettings.inspectorTargets.join(', ')}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Number of Inspectors:</span>
                <span className="setting-value">{teamConfig.defaultSettings.numInspectors}</span>
              </div>
            </div>
          </div>
        </div>
      </Collapse>
    </Card>
  );
}

export default TeamConfigInfo;
