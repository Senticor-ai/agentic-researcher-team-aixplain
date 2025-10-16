import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  HTMLSelect,
  Tag,
  Intent,
  Callout,
  Spinner,
  NonIdealState,
  ProgressBar,
  Collapse
} from '@blueprintjs/core';
import { agentTeamsAPI } from '../api/client';
import SachstandDisplay from '../components/SachstandDisplay';
import '@blueprintjs/core/lib/css/blueprint.css';
import './TeamDetail.css';

// Custom hook for auto-refresh polling
function useAutoRefresh(teamId, interval = 3000) {
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const intervalRef = useRef(null);

  const fetchTeam = async (isManual = false) => {
    try {
      if (isManual) {
        setIsRefreshing(true);
      } else if (!team) {
        setLoading(true);
      }
      
      const response = await agentTeamsAPI.getById(teamId);
      setTeam(response.data);
      setError(null);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to load team details: ' + err.message);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchTeam();

    // Set up polling if team is pending or running
    const shouldPoll = team && (team.status === 'pending' || team.status === 'running' || team.status === 'initializing' || team.status === 'researching');
    
    if (shouldPoll) {
      intervalRef.current = setInterval(() => {
        fetchTeam();
      }, interval);
    }

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [teamId, team?.status, interval]);

  const manualRefresh = () => {
    fetchTeam(true);
  };

  return { team, loading, error, lastUpdated, isRefreshing, manualRefresh };
}

function TeamDetail() {
  const { teamId } = useParams();
  const navigate = useNavigate();
  const { team, loading, error, lastUpdated, isRefreshing, manualRefresh } = useAutoRefresh(teamId);
  const [logFilter, setLogFilter] = useState('all');
  const logContainerRef = useRef(null);
  const prevLogLengthRef = useRef(0);
  const [trace, setTrace] = useState(null);
  const [traceLoading, setTraceLoading] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState(new Set());
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [costThreshold, setCostThreshold] = useState(10); // Default threshold: 10 credits
  const [showCostAlert, setShowCostAlert] = useState(false);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatJSON = (obj) => {
    return JSON.stringify(obj, null, 2);
  };

  const getRelativeTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const getTimeSinceUpdate = () => {
    if (!lastUpdated) return '';
    const seconds = Math.floor((new Date() - lastUpdated) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  // Update time display every second
  const [, setTick] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => setTick(t => t + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  // Auto-scroll to latest log entry when new logs arrive
  useEffect(() => {
    if (team?.execution_log && logContainerRef.current) {
      const currentLogLength = team.execution_log.length;
      if (currentLogLength > prevLogLengthRef.current) {
        logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
      }
      prevLogLengthRef.current = currentLogLength;
    }
  }, [team?.execution_log]);

  // Parse log entry to extract timestamp, agent, level, and message
  const parseLogEntry = (entry) => {
    if (typeof entry === 'object') {
      return {
        timestamp: entry.timestamp || null,
        agent: entry.agent || 'system',
        level: entry.level || 'info',
        message: entry.message || formatJSON(entry)
      };
    }
    
    // Parse string format: "timestamp - agent - level - message"
    const str = String(entry);
    const parts = str.split(' - ');
    
    if (parts.length >= 4) {
      return {
        timestamp: parts[0],
        agent: parts[1],
        level: parts[2].toLowerCase(),
        message: parts.slice(3).join(' - ')
      };
    }
    
    // Detect agent name in message
    let agent = 'system';
    let message = str;
    const agentPatterns = [
      { pattern: /\[?mentalist\]?/i, name: 'mentalist' },
      { pattern: /\[?orchestrator\]?/i, name: 'orchestrator' },
      { pattern: /\[?inspector\]?/i, name: 'inspector' },
      { pattern: /\[?search[_ ]agent\]?/i, name: 'search' },
      { pattern: /\[?response[_ ]generator\]?/i, name: 'response' },
    ];
    
    for (const { pattern, name } of agentPatterns) {
      if (pattern.test(str)) {
        agent = name;
        break;
      }
    }
    
    // Detect log level
    let level = 'info';
    if (/error|failed|failure/i.test(str)) level = 'error';
    else if (/warning|warn/i.test(str)) level = 'warning';
    
    return { timestamp: null, agent, level, message };
  };

  // Filter logs based on selected agent
  const getFilteredLogs = () => {
    if (!team?.execution_log) return [];
    if (logFilter === 'all') return team.execution_log;
    
    return team.execution_log.filter(entry => {
      const logData = parseLogEntry(entry);
      return logData.agent === logFilter;
    });
  };

  // Fetch trace data
  useEffect(() => {
    const fetchTrace = async () => {
      if (!team || team.status === 'pending') return;
      
      try {
        setTraceLoading(true);
        const response = await agentTeamsAPI.getTrace(teamId);
        setTrace(response.data);
      } catch (err) {
        console.error('Failed to load trace:', err);
      } finally {
        setTraceLoading(false);
      }
    };

    fetchTrace();
  }, [teamId, team?.status]);

  // Fetch execution stats
  useEffect(() => {
    const fetchStats = async () => {
      if (!team) return;
      
      try {
        setStatsLoading(true);
        const response = await agentTeamsAPI.getExecutionStats(teamId);
        setStats(response.data);
        
        // Check cost threshold
        if (response.data?.execution_data?.credits) {
          const currentCost = response.data.execution_data.credits;
          if (currentCost > costThreshold) {
            setShowCostAlert(true);
          }
        }
      } catch (err) {
        console.error('Failed to load stats:', err);
      } finally {
        setStatsLoading(false);
      }
    };

    fetchStats();
  }, [teamId, team?.status, costThreshold]);

  const toggleStep = (stepNumber) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepNumber)) {
      newExpanded.delete(stepNumber);
    } else {
      newExpanded.add(stepNumber);
    }
    setExpandedSteps(newExpanded);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const getAgentTypeColor = (agentType) => {
    const colors = {
      'mentalist': '#9b59b6',
      'orchestrator': '#3498db',
      'inspector': '#e74c3c',
      'search': '#2ecc71',
      'wikipedia': '#e67e22',
      'response': '#f39c12',
      'unknown': '#95a5a6'
    };
    return colors[agentType?.toLowerCase()] || colors.unknown;
  };

  const getStatusIntent = (status) => {
    switch (status) {
      case 'completed': return Intent.SUCCESS;
      case 'running': case 'researching': return Intent.PRIMARY;
      case 'failed': return Intent.DANGER;
      case 'pending': case 'initializing': return Intent.NONE;
      default: return Intent.NONE;
    }
  };

  // Show error if there's an error and no team data
  if (error && !team) {
    return (
      <div className="team-detail-error">
        <NonIdealState
          icon="error"
          title="Error Loading Team"
          description={error}
          action={<Button onClick={() => navigate('/')} icon="arrow-left">Back to Dashboard</Button>}
        />
      </div>
    );
  }

  // Show loading only if we have no team data at all
  if (loading && !team) {
    return (
      <div className="team-detail-loading">
        <NonIdealState
          icon={<Spinner />}
          title="Loading Team Details"
          description="Please wait while we fetch the team information..."
        />
      </div>
    );
  }

  // If we still don't have team data after loading, show not found
  if (!loading && !team) {
    return (
      <div className="team-detail-error">
        <NonIdealState
          icon="search"
          title="Team Not Found"
          description="The requested team could not be found."
          action={<Button onClick={() => navigate('/')} icon="arrow-left">Back to Dashboard</Button>}
        />
      </div>
    );
  }

  return (
    <div className="team-detail">
      {/* Background refresh indicator */}
      {isRefreshing && (
        <div className="background-refresh-indicator">
          <div className="refresh-spinner"></div>
          <span>Updating...</span>
        </div>
      )}
      
      <div className="team-detail-header">
        <Button 
          onClick={() => navigate('/')} 
          icon="arrow-left"
          minimal
        >
          Back to Dashboard
        </Button>
        <div className="header-title-row">
          <h2>Team: {team.team_id}</h2>
          <div className="refresh-controls">
            {lastUpdated && (
              <span className="last-updated">
                Last updated: {getTimeSinceUpdate()}
              </span>
            )}
            {team.status === 'failed' && (
              <Button 
                onClick={() => navigate('/', { state: { retryTopic: team.topic, retryGoals: team.goals } })} 
                icon="repeat"
                intent={Intent.WARNING}
              >
                Retry with Same Topic
              </Button>
            )}
            <Button 
              onClick={manualRefresh} 
              icon="refresh"
              intent={Intent.PRIMARY}
              loading={isRefreshing}
              disabled={isRefreshing}
            >
              Refresh
            </Button>
          </div>
        </div>
      </div>

      <div className="team-metadata">
        <Card className="metadata-card">
          <h3>Metadata</h3>
          
          {/* Cost Alert */}
          {showCostAlert && stats?.execution_data?.credits && (
            <Callout 
              intent={Intent.WARNING} 
              title="Cost Threshold Exceeded"
              icon="warning-sign"
              onDismiss={() => setShowCostAlert(false)}
              style={{ marginBottom: '1rem' }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <div>
                  This team has exceeded the cost threshold of {costThreshold} credits.
                </div>
                <div style={{ fontSize: '0.875rem' }}>
                  <strong>Current Cost:</strong> {stats.execution_data.credits.toFixed(2)} credits
                  <br />
                  <strong>Threshold:</strong> {costThreshold} credits
                  <br />
                  <strong>Overage:</strong> {(stats.execution_data.credits - costThreshold).toFixed(2)} credits
                </div>
              </div>
            </Callout>
          )}
          
          {/* Live Execution Indicator with Running Cost Estimate */}
          {(team.status === 'pending' || team.status === 'running' || team.status === 'initializing' || team.status === 'researching') && (
            <Callout intent={Intent.PRIMARY} className="progress-indicator">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <Spinner size={20} />
                  <div style={{ flex: 1 }}>
                    <div className="progress-message">
                      Team is executing<span className="dots"></span>
                    </div>
                    <div style={{ fontSize: '0.875rem', color: '#5c7080', marginTop: '0.25rem' }}>
                      {(() => {
                        const elapsed = Math.floor((new Date() - new Date(team.created_at)) / 1000);
                        const minutes = Math.floor(elapsed / 60);
                        const seconds = elapsed % 60;
                        return `Running for ${minutes}m ${seconds}s`;
                      })()}
                    </div>
                    {stats?.execution_data?.credits && (
                      <div style={{ fontSize: '0.875rem', color: '#182026', marginTop: '0.25rem', fontWeight: 600 }}>
                        💳 Running Cost: {stats.execution_data.credits.toFixed(2)} credits
                        {stats.execution_data.credits > costThreshold && (
                          <span style={{ color: '#d9822b', marginLeft: '0.5rem' }}>
                            (⚠ Over threshold)
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  <span className="progress-hint">Auto-refresh: 3s</span>
                </div>
                <div style={{ fontSize: '0.875rem', color: '#182026', lineHeight: '1.5' }}>
                  <strong>Current Phase:</strong> Agents are coordinating research
                  <br />
                  <em>Note: Intermediate steps will appear after execution completes (aixplain SDK limitation)</em>
                </div>
              </div>
            </Callout>
          )}
          
          <div className="metadata-grid">
            <div className="metadata-item">
              <span className="metadata-label">Topic:</span>
              <span className="metadata-value">{team.topic}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">Status:</span>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <Tag intent={getStatusIntent(team.status)} large>
                  {team.status}
                </Tag>
                {/* Show warning if completed but no entities */}
                {team.status === 'completed' && (!team.sachstand?.hasPart || team.sachstand.hasPart.length === 0) && (
                  <Tag intent={Intent.WARNING} large icon="warning-sign">
                    No Entities Found
                  </Tag>
                )}
              </div>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">Created:</span>
              <span className="metadata-value">{getRelativeTime(team.created_at)}</span>
            </div>
            {team.updated_at && (
              <div className="metadata-item">
                <span className="metadata-label">Updated:</span>
                <span className="metadata-value">{getRelativeTime(team.updated_at)}</span>
              </div>
            )}
            {/* Show entity count for completed teams */}
            {(team.status === 'completed' || team.status === 'failed') && (
              <div className="metadata-item" style={{ gridColumn: '1 / -1' }}>
                <span className="metadata-label">Extracted Entities:</span>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  <Tag 
                    large 
                    intent={
                      team.sachstand?.hasPart?.length > 0 ? Intent.SUCCESS : Intent.WARNING
                    }
                    icon={team.sachstand?.hasPart?.length > 0 ? "tick-circle" : "warning-sign"}
                  >
                    {team.sachstand?.hasPart?.length || 0} Total
                  </Tag>
                  {team.sachstand?.hasPart?.length > 0 && (() => {
                    // Count entities by type
                    const typeCounts = {};
                    team.sachstand.hasPart.forEach(entity => {
                      const type = entity['@type'] || 'Unknown';
                      typeCounts[type] = (typeCounts[type] || 0) + 1;
                    });
                    
                    // Define colors for each type
                    const typeColors = {
                      'Person': '#3498db',
                      'Organization': '#e67e22',
                      'GovernmentOrganization': '#e67e22',
                      'Event': '#9b59b6',
                      'ConferenceEvent': '#9b59b6',
                      'Topic': '#16a085',
                      'Thing': '#16a085',
                      'Policy': '#c0392b',
                      'Legislation': '#c0392b'
                    };
                    
                    return Object.entries(typeCounts).map(([type, count]) => (
                      <Tag 
                        key={type}
                        minimal
                        style={{ 
                          backgroundColor: `${typeColors[type] || '#95a5a6'}15`,
                          color: typeColors[type] || '#95a5a6',
                          fontWeight: 600
                        }}
                      >
                        {type}: {count}
                      </Tag>
                    ));
                  })()}
                </div>
              </div>
            )}
          </div>
          
          {/* Interaction Usage Indicator */}
          {team.interaction_limit && stats?.execution_data?.intermediate_steps_count && (
            <div className="progress-bar-container">
              <div className="progress-bar-label">
                <span>Interaction Usage</span>
                <span>{stats.execution_data.intermediate_steps_count} / {team.interaction_limit} interactions used</span>
              </div>
              <ProgressBar 
                value={Math.min((stats.execution_data.intermediate_steps_count / team.interaction_limit), 1)}
                intent={
                  stats.execution_data.intermediate_steps_count / team.interaction_limit > 0.9 
                    ? Intent.WARNING 
                    : Intent.PRIMARY
                }
                stripes={team.status === 'running'}
                animate={team.status === 'running'}
              />
            </div>
          )}
          {team.goals && team.goals.length > 0 && (
            <div className="metadata-section">
              <h4>Goals</h4>
              <ul className="goals-list">
                {team.goals.map((goal, index) => (
                  <li key={index}>{goal}</li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Download Raw Execution Trace */}
          <div className="metadata-section">
            <h4>Debug & Analysis</h4>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <Button
                icon="download"
                intent={Intent.PRIMARY}
                onClick={async () => {
                  try {
                    const response = await agentTeamsAPI.getRawResponse(teamId);
                    const dataStr = JSON.stringify(response.data, null, 2);
                    const dataBlob = new Blob([dataStr], { type: 'application/json' });
                    const url = URL.createObjectURL(dataBlob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `raw_execution_trace_${teamId}.json`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                  } catch (err) {
                    console.error('Failed to download raw trace:', err);
                  }
                }}
              >
                Download Complete Debug Data
              </Button>
            </div>
            <p style={{ fontSize: '0.9em', color: '#666', marginTop: '0.5rem' }}>
              Includes: raw agent response, server logs, execution log, sachstand, and MECE graph
            </p>
          </div>

          {/* Budget Tracking */}
          <div className="metadata-section budget-tracking">
            <h4>Budget Tracking</h4>
            <div className="budget-controls">
              <div className="budget-input-group">
                <label htmlFor="cost-threshold">Cost Threshold (credits):</label>
                <input
                  id="cost-threshold"
                  type="number"
                  min="0"
                  step="0.1"
                  value={costThreshold}
                  onChange={(e) => setCostThreshold(parseFloat(e.target.value) || 0)}
                  className="bp5-input"
                  style={{ width: '120px' }}
                />
              </div>
              {stats?.execution_data?.credits && (
                <div className="budget-status">
                  <div className="budget-bar-container">
                    <div className="budget-bar-label">
                      <span>Budget Usage</span>
                      <span>{stats.execution_data.credits.toFixed(2)} / {costThreshold} credits</span>
                    </div>
                    <ProgressBar 
                      value={Math.min(stats.execution_data.credits / costThreshold, 1)}
                      intent={
                        stats.execution_data.credits / costThreshold > 1 
                          ? Intent.DANGER 
                          : stats.execution_data.credits / costThreshold > 0.8
                          ? Intent.WARNING
                          : Intent.SUCCESS
                      }
                      stripes={stats.execution_data.credits > costThreshold}
                    />
                  </div>
                  <div className="budget-summary">
                    {stats.execution_data.credits <= costThreshold ? (
                      <Tag intent={Intent.SUCCESS} icon="tick-circle">
                        Within Budget
                      </Tag>
                    ) : (
                      <Tag intent={Intent.DANGER} icon="warning-sign">
                        Over Budget by {(stats.execution_data.credits - costThreshold).toFixed(2)} credits
                      </Tag>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>

      <div className="team-content">
        {/* Error Details Section - Show if there's an error */}
        {team.agent_response?.output && team.agent_response.output.includes('Error Code:') && (
          <Card className="content-section error-details-section">
            <Callout intent={Intent.DANGER} title="Agent Execution Error" icon="error">
              <p>The agent encountered an error during execution. See details below:</p>
            </Callout>
            
            <div style={{ marginTop: '1rem' }}>
              <h4>Error Output:</h4>
              <pre className="error-output">
                {team.agent_response.output}
              </pre>
            </div>

            {team.agent_response.data?.input && (
              <div style={{ marginTop: '1rem' }}>
                <h4>Agent Input:</h4>
                <pre className="agent-input">
                  {typeof team.agent_response.data.input === 'string' 
                    ? team.agent_response.data.input 
                    : JSON.stringify(team.agent_response.data.input, null, 2)}
                </pre>
              </div>
            )}

            <div style={{ marginTop: '1rem' }}>
              <Callout intent={Intent.WARNING} title="Debugging Information">
                <p><strong>Team ID (aixplain):</strong> {team.agent_response.data?.session_id || 'N/A'}</p>
                <p><strong>Intermediate Steps:</strong> {team.agent_response.intermediate_steps?.length || 0}</p>
                <p><strong>Status:</strong> {team.agent_response.completed ? 'Completed' : 'In Progress'}</p>
              </Callout>
            </div>
          </Card>
        )}

        {/* Results Section */}
        <SachstandDisplay 
          sachstand={team.sachstand}
          teamStatus={team.status}
          teamId={team.team_id}
        />

        {/* Technical Details Section */}
        <Card className="content-section">
          <div className="section-header">
            <h3>Execution Log</h3>
            <HTMLSelect 
              onChange={(e) => setLogFilter(e.target.value)}
              value={logFilter}
              options={[
                { label: 'All Agents', value: 'all' },
                { label: 'Mentalist', value: 'mentalist' },
                { label: 'Orchestrator', value: 'orchestrator' },
                { label: 'Inspector', value: 'inspector' },
                { label: 'Search Agent', value: 'search' },
                { label: 'Response Generator', value: 'response' }
              ]}
            />
          </div>
          <div className="log-container" ref={logContainerRef}>
            {team.execution_log && team.execution_log.length > 0 ? (
              <ul className="log-list">
                {getFilteredLogs().map((entry, index) => {
                  const logData = parseLogEntry(entry);
                  return (
                    <li 
                      key={index} 
                      className={`log-entry log-level-${logData.level}`}
                    >
                      <div className="log-header">
                        {logData.timestamp && (
                          <span className="log-timestamp">{logData.timestamp}</span>
                        )}
                        {logData.agent && (
                          <span className="log-agent">[{logData.agent}]</span>
                        )}
                        <Tag 
                          minimal 
                          intent={
                            logData.level === 'error' ? Intent.DANGER :
                            logData.level === 'warning' ? Intent.WARNING :
                            Intent.PRIMARY
                          }
                        >
                          {logData.level.toUpperCase()}
                        </Tag>
                      </div>
                      <div className="log-message">{logData.message}</div>
                    </li>
                  );
                })}
              </ul>
            ) : (
              <p className="empty-state">No execution log entries yet</p>
            )}
          </div>
        </Card>

        {/* Server Logs Section */}
        {team.server_logs && team.server_logs.length > 0 && (
          <Card className="content-section">
            <div className="section-header">
              <h3>Server Logs</h3>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <Button
                  small
                  icon="download"
                  onClick={() => {
                    const dataStr = JSON.stringify(team.server_logs, null, 2);
                    const dataBlob = new Blob([dataStr], { type: 'application/json' });
                    const url = URL.createObjectURL(dataBlob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `server_logs_${teamId}.json`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                  }}
                >
                  Download
                </Button>
              </div>
            </div>
            <div className="log-container">
              <ul className="log-list">
                {team.server_logs.map((entry, index) => (
                  <li 
                    key={index} 
                    className={`log-entry log-level-${entry.level?.toLowerCase() || 'info'}`}
                  >
                    <div className="log-header">
                      {entry.timestamp && (
                        <span className="log-timestamp">
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </span>
                      )}
                      {entry.logger && (
                        <span className="log-agent">[{entry.logger}]</span>
                      )}
                      <Tag 
                        minimal 
                        intent={
                          entry.level === 'ERROR' ? Intent.DANGER :
                          entry.level === 'WARNING' ? Intent.WARNING :
                          entry.level === 'INFO' ? Intent.PRIMARY :
                          Intent.NONE
                        }
                      >
                        {entry.level || 'INFO'}
                      </Tag>
                      {entry.module && (
                        <span className="log-module" style={{ fontSize: '0.85em', color: '#888' }}>
                          {entry.module}.{entry.function}:{entry.line}
                        </span>
                      )}
                    </div>
                    <div className="log-message">{entry.message}</div>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        )}

        <Card className="content-section">
          <h3>Agent Configuration & Execution Stats</h3>
          {statsLoading ? (
            <div className="loading-skeleton">
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line short"></div>
            </div>
          ) : stats ? (
            <div className="stats-container">
              {/* Overall Stats */}
              {stats.overall_stats && (
                <div className="stats-section">
                  <h4>Overall Statistics</h4>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <span className="stat-label">Status:</span>
                      <span className={`status-badge status-${stats.overall_stats.status}`}>
                        {stats.overall_stats.status}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Interaction Limit:</span>
                      <span className="stat-value">{stats.overall_stats.interaction_limit}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Strategy:</span>
                      <span className="stat-value">{stats.overall_stats.mece_strategy}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Created:</span>
                      <span className="stat-value">{formatDate(stats.overall_stats.created_at)}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Agent Configuration */}
              {stats.agent_configuration && (
                <div className="stats-section">
                  <h4>Agent Configuration</h4>
                  <div className="config-info">
                    <p><strong>Team Structure:</strong> {stats.agent_configuration.team_structure}</p>
                    <p><strong>Model:</strong> {stats.agent_configuration.model}</p>
                  </div>
                  
                  <div className="agents-grid">
                    <div className="agent-group">
                      <h5>Built-in Micro Agents</h5>
                      {stats.agent_configuration.built_in_agents.map((agent, idx) => (
                        <div key={idx} className="agent-card">
                          <div className="agent-name">{agent.name}</div>
                          <div className="agent-role">{agent.role}</div>
                          <div className="agent-desc">{agent.description}</div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="agent-group">
                      <h5>User-Defined Agents</h5>
                      {stats.agent_configuration.user_defined_agents.map((agent, idx) => (
                        <div key={idx} className="agent-card">
                          <div className="agent-name">{agent.name}</div>
                          <div className="agent-desc">{agent.description}</div>
                          {agent.tools && agent.tools.length > 0 && (
                            <div className="agent-tools">
                              <strong>Tools:</strong> {agent.tools.join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Execution Data */}
              {stats.execution_data && (
                <div className="stats-section">
                  <h4>Execution Statistics</h4>
                  
                  {/* Overall Stats */}
                  <div className="stats-grid">
                    {stats.execution_data.status && (
                      <div className="stat-item">
                        <span className="stat-label">Status:</span>
                        <span className={`stat-value ${stats.execution_data.status === 'SUCCESS' ? 'stat-success' : 'stat-error'}`}>
                          {stats.execution_data.status}
                        </span>
                      </div>
                    )}
                    {stats.execution_data.runtime !== undefined && (
                      <div className="stat-item">
                        <span className="stat-label">⏱ Runtime:</span>
                        <span className="stat-value">{stats.execution_data.runtime}s</span>
                      </div>
                    )}
                    {stats.execution_data.credits !== undefined && (
                      <div className="stat-item">
                        <span className="stat-label">💳 Credits:</span>
                        <span className="stat-value">{stats.execution_data.credits}</span>
                      </div>
                    )}
                    {stats.execution_data.api_calls !== undefined && (
                      <div className="stat-item">
                        <span className="stat-label">📡 API Calls:</span>
                        <span className="stat-value">{stats.execution_data.api_calls}</span>
                      </div>
                    )}
                    <div className="stat-item">
                      <span className="stat-label">Completed:</span>
                      <span className="stat-value">{stats.execution_data.completed ? '✓ Yes' : '✗ No'}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Has Output:</span>
                      <span className="stat-value">{stats.execution_data.has_output ? '✓ Yes' : '✗ No'}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Intermediate Steps:</span>
                      <span className="stat-value">{stats.execution_data.intermediate_steps_count}</span>
                    </div>
                    {stats.execution_data.session_id && (
                      <div className="stat-item">
                        <span className="stat-label">Session ID:</span>
                        <span className="stat-value stat-mono">{stats.execution_data.session_id}</span>
                      </div>
                    )}
                    {stats.execution_data.environment && (
                      <div className="stat-item">
                        <span className="stat-label">Environment:</span>
                        <span className="stat-value">{stats.execution_data.environment}</span>
                      </div>
                    )}
                    {stats.execution_data.timestamp && (
                      <div className="stat-item">
                        <span className="stat-label">Timestamp:</span>
                        <span className="stat-value">{new Date(stats.execution_data.timestamp).toLocaleString()}</span>
                      </div>
                    )}
                  </div>

                  {/* Resource Breakdown with Visualizations */}
                  {(stats.execution_data.runtime_breakdown || stats.execution_data.credit_breakdown || stats.execution_data.api_call_breakdown) && (
                    <div className="breakdown-section">
                      <h5>Resource Breakdown by Asset</h5>
                      
                      {/* Pie Charts for Visual Breakdown */}
                      <div className="pie-charts-container">
                        {stats.execution_data.credit_breakdown && Object.keys(stats.execution_data.credit_breakdown).length > 0 && (
                          <div className="pie-chart-wrapper">
                            <h6>💳 Credit Distribution</h6>
                            <div className="pie-chart">
                              {(() => {
                                const data = Object.entries(stats.execution_data.credit_breakdown);
                                const total = data.reduce((sum, [, val]) => sum + val, 0);
                                let currentAngle = 0;
                                const colors = ['#137cbd', '#0f9960', '#d9822b', '#db3737', '#8f398f', '#00b3a4'];
                                
                                return (
                                  <>
                                    <svg viewBox="0 0 200 200" className="pie-svg">
                                      {data.map(([asset, value], idx) => {
                                        const percentage = (value / total) * 100;
                                        const angle = (percentage / 100) * 360;
                                        const startAngle = currentAngle;
                                        const endAngle = currentAngle + angle;
                                        currentAngle = endAngle;
                                        
                                        const startRad = (startAngle - 90) * Math.PI / 180;
                                        const endRad = (endAngle - 90) * Math.PI / 180;
                                        const x1 = 100 + 80 * Math.cos(startRad);
                                        const y1 = 100 + 80 * Math.sin(startRad);
                                        const x2 = 100 + 80 * Math.cos(endRad);
                                        const y2 = 100 + 80 * Math.sin(endRad);
                                        const largeArc = angle > 180 ? 1 : 0;
                                        
                                        return (
                                          <path
                                            key={asset}
                                            d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`}
                                            fill={colors[idx % colors.length]}
                                            stroke="white"
                                            strokeWidth="2"
                                          >
                                            <title>{`${asset}: ${value.toFixed(2)} (${percentage.toFixed(1)}%)`}</title>
                                          </path>
                                        );
                                      })}
                                    </svg>
                                    <div className="pie-legend">
                                      {data.map(([asset, value], idx) => (
                                        <div key={asset} className="legend-item">
                                          <span 
                                            className="legend-color" 
                                            style={{ backgroundColor: colors[idx % colors.length] }}
                                          ></span>
                                          <span className="legend-label">{asset}</span>
                                          <span className="legend-value">{value.toFixed(2)}</span>
                                        </div>
                                      ))}
                                    </div>
                                  </>
                                );
                              })()}
                            </div>
                          </div>
                        )}
                        
                        {stats.execution_data.runtime_breakdown && Object.keys(stats.execution_data.runtime_breakdown).length > 0 && (
                          <div className="pie-chart-wrapper">
                            <h6>⏱ Runtime Distribution</h6>
                            <div className="pie-chart">
                              {(() => {
                                const data = Object.entries(stats.execution_data.runtime_breakdown);
                                const total = data.reduce((sum, [, val]) => sum + val, 0);
                                let currentAngle = 0;
                                const colors = ['#137cbd', '#0f9960', '#d9822b', '#db3737', '#8f398f', '#00b3a4'];
                                
                                return (
                                  <>
                                    <svg viewBox="0 0 200 200" className="pie-svg">
                                      {data.map(([asset, value], idx) => {
                                        const percentage = (value / total) * 100;
                                        const angle = (percentage / 100) * 360;
                                        const startAngle = currentAngle;
                                        const endAngle = currentAngle + angle;
                                        currentAngle = endAngle;
                                        
                                        const startRad = (startAngle - 90) * Math.PI / 180;
                                        const endRad = (endAngle - 90) * Math.PI / 180;
                                        const x1 = 100 + 80 * Math.cos(startRad);
                                        const y1 = 100 + 80 * Math.sin(startRad);
                                        const x2 = 100 + 80 * Math.cos(endRad);
                                        const y2 = 100 + 80 * Math.sin(endRad);
                                        const largeArc = angle > 180 ? 1 : 0;
                                        
                                        return (
                                          <path
                                            key={asset}
                                            d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`}
                                            fill={colors[idx % colors.length]}
                                            stroke="white"
                                            strokeWidth="2"
                                          >
                                            <title>{`${asset}: ${value.toFixed(2)}s (${percentage.toFixed(1)}%)`}</title>
                                          </path>
                                        );
                                      })}
                                    </svg>
                                    <div className="pie-legend">
                                      {data.map(([asset, value], idx) => (
                                        <div key={asset} className="legend-item">
                                          <span 
                                            className="legend-color" 
                                            style={{ backgroundColor: colors[idx % colors.length] }}
                                          ></span>
                                          <span className="legend-label">{asset}</span>
                                          <span className="legend-value">{value.toFixed(2)}s</span>
                                        </div>
                                      ))}
                                    </div>
                                  </>
                                );
                              })()}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Detailed Breakdown Lists */}
                      <div className="breakdown-grid">
                        {stats.execution_data.runtime_breakdown && Object.keys(stats.execution_data.runtime_breakdown).length > 0 && (
                          <div className="breakdown-card">
                            <strong>⏱ Runtime Breakdown</strong>
                            <ul className="breakdown-list">
                              {Object.entries(stats.execution_data.runtime_breakdown).map(([asset, time]) => (
                                <li key={asset}>
                                  <span className="breakdown-asset">{asset}:</span>
                                  <span className="breakdown-value">{time}s</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {stats.execution_data.credit_breakdown && Object.keys(stats.execution_data.credit_breakdown).length > 0 && (
                          <div className="breakdown-card">
                            <strong>💳 Credit Breakdown</strong>
                            <ul className="breakdown-list">
                              {Object.entries(stats.execution_data.credit_breakdown).map(([asset, credits]) => (
                                <li key={asset}>
                                  <span className="breakdown-asset">{asset}:</span>
                                  <span className="breakdown-value">{credits}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {stats.execution_data.api_call_breakdown && Object.keys(stats.execution_data.api_call_breakdown).length > 0 && (
                          <div className="breakdown-card">
                            <strong>📡 API Call Breakdown</strong>
                            <ul className="breakdown-list">
                              {Object.entries(stats.execution_data.api_call_breakdown).map(([asset, calls]) => (
                                <li key={asset}>
                                  <span className="breakdown-asset">{asset}:</span>
                                  <span className="breakdown-value">{calls}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Cost Per Entity Metric */}
                  {stats.execution_data && stats.execution_data.credits && team.sachstand?.hasPart && (
                    <div className="cost-per-entity-section">
                      <h5>Cost Efficiency</h5>
                      <div className="cost-per-entity-card">
                        <div className="cost-metric">
                          <span className="metric-label">Cost per Entity:</span>
                          <span className="metric-value">
                            {(stats.execution_data.credits / team.sachstand.hasPart.length).toFixed(3)} credits
                          </span>
                        </div>
                        <div className="cost-metric">
                          <span className="metric-label">Total Entities:</span>
                          <span className="metric-value">{team.sachstand.hasPart.length}</span>
                        </div>
                        <div className="cost-metric">
                          <span className="metric-label">Total Credits:</span>
                          <span className="metric-value">{stats.execution_data.credits.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Export Stats Button */}
                  <div className="export-stats-section">
                    <Button
                      icon="download"
                      intent={Intent.PRIMARY}
                      onClick={() => {
                        const statsData = {
                          team_id: team.team_id,
                          topic: team.topic,
                          ...stats
                        };
                        const blob = new Blob([JSON.stringify(statsData, null, 2)], { type: 'application/json' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `stats_${team.team_id}.json`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      Export Stats (JSON)
                    </Button>
                    <Button
                      icon="download"
                      onClick={() => {
                        const csvRows = [
                          ['Metric', 'Value'],
                          ['Team ID', team.team_id],
                          ['Topic', team.topic],
                          ['Status', stats.execution_data?.status || 'N/A'],
                          ['Runtime (s)', stats.execution_data?.runtime || 'N/A'],
                          ['Credits', stats.execution_data?.credits || 'N/A'],
                          ['API Calls', stats.execution_data?.api_calls || 'N/A'],
                          ['Entities', team.sachstand?.hasPart?.length || 0],
                          ['Cost per Entity', stats.execution_data?.credits && team.sachstand?.hasPart ? (stats.execution_data.credits / team.sachstand.hasPart.length).toFixed(3) : 'N/A']
                        ];
                        const csvContent = csvRows.map(row => row.join(',')).join('\n');
                        const blob = new Blob([csvContent], { type: 'text/csv' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `stats_${team.team_id}.csv`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      Export Stats (CSV)
                    </Button>
                  </div>

                  {/* Assets Used */}
                  {stats.execution_data.assets_used && stats.execution_data.assets_used.length > 0 && (
                    <div className="assets-section">
                      <h5>Assets Used</h5>
                      <div className="assets-list">
                        {stats.execution_data.assets_used.map((asset, idx) => (
                          <span key={idx} className="asset-badge">{asset}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Mentalist Plan */}
              {stats.mentalist_plan && stats.mentalist_plan.available && (
                <div className="stats-section">
                  <h4>Mentalist Plan</h4>
                  <div className="plan-entries">
                    {stats.mentalist_plan.entries.map((entry, idx) => (
                      <div key={idx} className="plan-entry">{entry}</div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="empty-state">No stats available yet</p>
          )}
        </Card>

        <Card className="content-section">
          <h3>Agent Execution Trace</h3>
          {traceLoading ? (
            <div className="loading-skeleton">
              <div className="skeleton-line"></div>
              <div className="skeleton-line"></div>
              <div className="skeleton-line short"></div>
            </div>
          ) : trace && trace.trace && trace.trace.length > 0 ? (
            <div className="trace-container">
              {/* Timeline Visualization */}
              <div className="execution-timeline">
                <h4>Execution Timeline</h4>
                <div className="timeline-track">
                  {trace.trace.map((step, index) => {
                    const colors = {
                      'mentalist': '#9b59b6',
                      'orchestrator': '#3498db',
                      'inspector': '#e74c3c',
                      'search': '#2ecc71',
                      'wikipedia': '#e67e22',
                      'response': '#f39c12',
                      'unknown': '#95a5a6'
                    };
                    const color = colors[step.agent_type?.toLowerCase()] || colors.unknown;
                    
                    return (
                      <div 
                        key={step.step_number} 
                        className="timeline-item"
                        onClick={() => toggleStep(step.step_number)}
                      >
                        <div 
                          className="timeline-marker" 
                          style={{ backgroundColor: color }}
                          title={`Step ${step.step_number}: ${step.agent_name}`}
                        >
                          {step.step_number}
                        </div>
                        <div className="timeline-label">
                          <div className="timeline-agent">{step.agent_name || 'Unknown'}</div>
                          {step.runtime && (
                            <div className="timeline-duration">{step.runtime}s</div>
                          )}
                        </div>
                        {index < trace.trace.length - 1 && (
                          <div className="timeline-connector"></div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
              
              <div className="trace-flow">
                {trace.trace.map((step, index) => (
                  <div key={step.step_number} className="trace-step">
                    <div 
                      className="trace-step-header"
                      onClick={() => toggleStep(step.step_number)}
                      style={{ borderLeftColor: getAgentTypeColor(step.agent_type) }}
                    >
                      <div className="trace-step-title">
                        <span className="trace-step-number">Step {step.step_number}</span>
                        {step.agent_name && (
                          <span 
                            className="trace-agent-badge"
                            style={{ backgroundColor: getAgentTypeColor(step.agent_type) }}
                          >
                            {step.agent_name}
                          </span>
                        )}
                        {step.agent_type && step.agent_type !== 'Unknown' && (
                          <span className="trace-agent-type">({step.agent_type})</span>
                        )}
                      </div>
                      <div className="trace-step-controls">
                        {step.runtime !== undefined && step.runtime !== null && (
                          <span className="trace-stat">⏱ {step.runtime}s</span>
                        )}
                        {step.credits !== undefined && step.credits !== null && (
                          <span className="trace-stat">💳 {step.credits}</span>
                        )}
                        {step.api_calls !== undefined && step.api_calls !== null && (
                          <span className="trace-stat">📡 {step.api_calls}</span>
                        )}
                        <button className="trace-expand-btn">
                          {expandedSteps.has(step.step_number) ? '▼' : '▶'}
                        </button>
                      </div>
                    </div>
                    
                    {expandedSteps.has(step.step_number) && (
                      <div className="trace-step-content">
                        {/* Show raw data for debugging if agent is unknown */}
                        {(step.agent_name === 'Unknown Agent' || step.agent_type === 'unknown') && step.raw_data && (
                          <div className="trace-detail trace-debug">
                            <strong>🔍 Debug - Raw Data:</strong>
                            <pre>{typeof step.raw_data === 'string' ? step.raw_data : formatJSON(step.raw_data)}</pre>
                          </div>
                        )}
                        
                        {step.task && (
                          <div className="trace-detail">
                            <strong>Task:</strong>
                            <pre>{typeof step.task === 'string' ? step.task : formatJSON(step.task)}</pre>
                          </div>
                        )}
                        {step.thought && (
                          <div className="trace-detail">
                            <strong>Thought/Reasoning:</strong>
                            <pre>{step.thought}</pre>
                          </div>
                        )}
                        {step.input && (
                          <div className="trace-detail">
                            <strong>Input:</strong>
                            <pre>{typeof step.input === 'string' ? step.input : formatJSON(step.input)}</pre>
                          </div>
                        )}
                        {step.output && (
                          <div className="trace-detail">
                            <strong>Output:</strong>
                            <pre>{typeof step.output === 'string' ? step.output : formatJSON(step.output)}</pre>
                          </div>
                        )}
                        {step.tools && step.tools.length > 0 && (
                          <div className="trace-detail">
                            <strong>Tools Used:</strong>
                            <ul className="trace-tools-list">
                              {step.tools.map((tool, idx) => (
                                <li key={idx}>
                                  {typeof tool === 'string' ? tool : formatJSON(tool)}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {step.api_calls && (
                          <div className="trace-detail">
                            <strong>API Calls:</strong> {step.api_calls}
                          </div>
                        )}
                        {step.message && (
                          <div className="trace-detail">
                            <strong>Message:</strong>
                            <pre>{step.message}</pre>
                          </div>
                        )}
                        <button 
                          className="btn-copy"
                          onClick={() => copyToClipboard(formatJSON(step))}
                        >
                          📋 Copy Step Details
                        </button>
                      </div>
                    )}
                    
                    {index < trace.trace.length - 1 && (
                      <div className="trace-arrow">↓</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="empty-state">No trace data available yet</p>
          )}
        </Card>
      </div>
    </div>
  );
}

export default TeamDetail;
