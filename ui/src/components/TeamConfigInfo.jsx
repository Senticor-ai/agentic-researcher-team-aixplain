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
      model: agentConfig.default_model,
      builtInAgents: agentConfig.built_in_agents?.map(agent => ({
        name: agent.name,
        role: agent.role,
        description: agent.description,
        model: agent.model,
        capabilities: agent.capabilities,
        icon: getAgentIcon(agent.name),
        color: getAgentColor(agent.name)
      })),
      userDefinedAgents: agentConfig.user_defined_agents?.map(agent => ({
        name: agent.name,
        role: agent.role,
        description: agent.description,
        model: agent.model,
        tools: agent.tools,
        capabilities: agent.capabilities,
        searchStrategy: agent.search_strategy,
        languagesSupported: agent.languages_supported,
        toolId: agent.tool_id,
        usedBy: agent.used_by,
        costPerRequest: agent.cost_per_request,
        icon: getAgentIcon(agent.name),
        color: getAgentColor(agent.name)
      })),
      coordination: agentConfig.coordination,
      defaultSettings: {
        interactionLimit: agentConfig.default_settings?.interaction_limit,
        meceStrategy: agentConfig.default_settings?.mece_strategy,
        inspectorTargets: agentConfig.default_settings?.inspector_targets,
        numInspectors: agentConfig.default_settings?.num_inspectors
      }
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

  const config = getDisplayConfig();

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

  if (error || !config) {
    return (
      <Card className="team-config-info">
        <div className="config-header">
          <h3>🤖 Agent Team Configuration</h3>
        </div>
        <div style={{ textAlign: 'center', padding: '2rem', color: '#e74c3c' }}>
          <p>⚠️ {error || 'Failed to load configuration'}</p>
          <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
            Please check your API connection
          </p>
        </div>
      </Card>
    );
  }

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
            <div className="summary-value">{config.model}</div>
          </div>
        </div>
        <div className="summary-item">
          <span className="summary-icon">👥</span>
          <div className="summary-content">
            <div className="summary-label">Built-in Agents</div>
            <div className="summary-value">{config.builtInAgents.length} Micro Agents</div>
          </div>
        </div>
        <div className="summary-item">
          <span className="summary-icon">🔧</span>
          <div className="summary-content">
            <div className="summary-label">Custom Agents</div>
            <div className="summary-value">
              {config.userDefinedAgents.length} Agent{config.userDefinedAgents.length !== 1 ? 's' : ''}
              {config.userDefinedAgents.length > 0 && (
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
            <div className="summary-value">{config.defaultSettings.interactionLimit} steps</div>
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
              {config.builtInAgents.map((agent, idx) => (
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
              {config.userDefinedAgents.map((agent, idx) => (
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
                      {agent.tools && agent.tools.length > 0 && (
                        <div className="agent-tools">
                          {agent.tools.map((tool, tidx) => (
                            <Tag key={tidx} minimal small>
                              {tool}
                            </Tag>
                          ))}
                        </div>
                      )}
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
            <h4>🔄 {config.coordination.approach}</h4>
            <p className="section-description">
              {config.coordination.description}
            </p>
            <div className="coordination-info">
              <div className="coordination-note">
                <strong>⚠️ Important:</strong> Unlike traditional workflows, this team does NOT follow a predefined sequence. 
                The Mentalist plans dynamically based on the research topic, and the Orchestrator coordinates agents as needed. 
                This allows for flexible, adaptive research strategies.
              </div>
              <div className="roles-list">
                {config.coordination.roles.map((role, idx) => (
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
                <span className="setting-value">{config.defaultSettings.interactionLimit} steps</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">MECE Strategy:</span>
                <span className="setting-value">{config.defaultSettings.meceStrategy}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Inspector Targets:</span>
                <span className="setting-value">{config.defaultSettings.inspectorTargets.join(', ')}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Number of Inspectors:</span>
                <span className="setting-value">{config.defaultSettings.numInspectors}</span>
              </div>
            </div>
          </div>
        </div>
      </Collapse>
    </Card>
  );
}

export default TeamConfigInfo;
