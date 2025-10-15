import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Card, 
  Button, 
  HTMLSelect, 
  HTMLTable, 
  Tag, 
  Intent,
  Callout,
  Spinner,
  NonIdealState,
  Tabs,
  Tab
} from '@blueprintjs/core';
import { agentTeamsAPI } from '../api/client';
import CreateTeamModal from '../components/CreateTeamModal';
import TeamConfigInfo from '../components/TeamConfigInfo';
import '@blueprintjs/core/lib/css/blueprint.css';
import './Dashboard.css';

function Dashboard() {
  const [teams, setTeams] = useState([]);
  const [filteredTeams, setFilteredTeams] = useState([]);
  const [statusFilter, setStatusFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [retryData, setRetryData] = useState(null);
  const [aggregateStats, setAggregateStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [dateRangeFilter, setDateRangeFilter] = useState('all');
  const [selectedTab, setSelectedTab] = useState('teams');
  const navigate = useNavigate();
  const location = useLocation();

  const fetchTeams = async () => {
    try {
      setLoading(true);
      const response = await agentTeamsAPI.getAll();
      // Sort by created_at descending (newest first) - API already does this
      setTeams(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load agent teams: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchAggregateStats = async () => {
    try {
      setStatsLoading(true);
      const params = {};
      
      // Apply status filter
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      // Apply date range filter
      if (dateRangeFilter !== 'all') {
        const now = new Date();
        let startDate;
        
        switch (dateRangeFilter) {
          case 'today':
            startDate = new Date(now.setHours(0, 0, 0, 0));
            break;
          case 'week':
            startDate = new Date(now.setDate(now.getDate() - 7));
            break;
          case 'month':
            startDate = new Date(now.setMonth(now.getMonth() - 1));
            break;
          default:
            startDate = null;
        }
        
        if (startDate) {
          params.start_date = startDate.toISOString();
        }
      }
      
      const response = await agentTeamsAPI.getAggregateStats(params);
      setAggregateStats(response.data);
    } catch (err) {
      console.error('Failed to load aggregate stats:', err);
    } finally {
      setStatsLoading(false);
    }
  };

  useEffect(() => {
    fetchTeams();
    fetchAggregateStats();
    
    // Check if we're retrying a failed team
    if (location.state?.retryTopic) {
      setRetryData({
        topic: location.state.retryTopic,
        goals: location.state.retryGoals
      });
      setShowCreateModal(true);
      // Clear the location state
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, []);

  // Refetch aggregate stats when filters change
  useEffect(() => {
    if (!loading) {
      fetchAggregateStats();
    }
  }, [statusFilter, dateRangeFilter]);

  // Filter teams based on status filter
  useEffect(() => {
    if (statusFilter === 'all') {
      setFilteredTeams(teams);
    } else {
      setFilteredTeams(teams.filter(team => team.status === statusFilter));
    }
  }, [teams, statusFilter]);

  const handleTeamClick = (teamId) => {
    navigate(`/teams/${teamId}`);
  };

  const handleTeamCreated = () => {
    setShowCreateModal(false);
    fetchTeams();
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getEntityCount = (team) => {
    // Try to get entity count from sachstand
    if (team.sachstand && team.sachstand.hasPart) {
      return team.sachstand.hasPart.length;
    }
    return 0;
  };

  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
  };

  // Calculate statistics
  const getStatistics = () => {
    const stats = {
      total: teams.length,
      pending: teams.filter(t => t.status === 'pending').length,
      running: teams.filter(t => t.status === 'running').length,
      completed: teams.filter(t => t.status === 'completed').length,
      failed: teams.filter(t => t.status === 'failed').length,
      recentTeams: teams.slice(0, 5),
      avgCompletionTime: 0
    };

    // Calculate average completion time for completed teams
    const completedTeams = teams.filter(t => t.status === 'completed');
    if (completedTeams.length > 0) {
      const totalTime = completedTeams.reduce((sum, team) => {
        const created = new Date(team.created_at);
        const updated = new Date(team.updated_at || team.created_at);
        return sum + (updated - created);
      }, 0);
      stats.avgCompletionTime = Math.round(totalTime / completedTeams.length / 1000); // in seconds
    }

    return stats;
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const stats = getStatistics();

  const getStatusIntent = (status) => {
    switch (status) {
      case 'completed': return Intent.SUCCESS;
      case 'running': return Intent.PRIMARY;
      case 'failed': return Intent.DANGER;
      case 'pending': return Intent.NONE;
      default: return Intent.NONE;
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <NonIdealState
          icon={<Spinner />}
          title="Loading Agent Teams"
          description="Please wait while we fetch your teams..."
        />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Agent Teams</h2>
        <Button 
          intent={Intent.PRIMARY}
          icon="add"
          text="Create Team"
          onClick={() => setShowCreateModal(true)}
        />
      </div>

      {error && (
        <Callout intent={Intent.DANGER} title="Error" style={{ marginBottom: '1rem' }}>
          {error}
        </Callout>
      )}

      <TeamConfigInfo />

      <Tabs
        id="dashboard-tabs"
        selectedTabId={selectedTab}
        onChange={(newTabId) => setSelectedTab(newTabId)}
        large
      >
        <Tab id="teams" title="Teams" />
        <Tab id="stats" title="Execution Stats" />
      </Tabs>

      {selectedTab === 'teams' && !loading && teams.length > 0 && (
        <div className="dashboard-stats">
          <div className="stats-grid">
            <Card className="stat-card">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Total Teams</div>
            </Card>
            <Card className="stat-card stat-running">
              <div className="stat-value">{stats.running}</div>
              <div className="stat-label">Running</div>
            </Card>
            <Card className="stat-card stat-completed">
              <div className="stat-value">{stats.completed}</div>
              <div className="stat-label">Completed</div>
            </Card>
            <Card className="stat-card stat-failed">
              <div className="stat-value">{stats.failed}</div>
              <div className="stat-label">Failed</div>
            </Card>
            {stats.completed > 0 && (
              <Card className="stat-card">
                <div className="stat-value">{formatDuration(stats.avgCompletionTime)}</div>
                <div className="stat-label">Avg Completion Time</div>
              </Card>
            )}
          </div>

          {stats.recentTeams.length > 0 && (
            <Card className="recent-activity">
              <h3>Recent Activity</h3>
              <div className="recent-teams-list">
                {stats.recentTeams.map((team) => (
                  <Card 
                    key={team.team_id} 
                    interactive
                    className="recent-team-item"
                    onClick={() => handleTeamClick(team.team_id)}
                  >
                    <div className="recent-team-info">
                      <div className="recent-team-topic">{team.topic}</div>
                      <div className="recent-team-meta">
                        <Tag intent={getStatusIntent(team.status)} minimal>
                          {team.status}
                        </Tag>
                        <span className="recent-team-time">{formatDate(team.created_at)}</span>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}

      {selectedTab === 'stats' && (
        <div className="aggregate-stats-panel">
          <Card className="stats-filters">
            <div className="filter-row">
              <div className="filter-group">
                <label htmlFor="date-range-filter">Date Range:</label>
                <HTMLSelect 
                  id="date-range-filter"
                  value={dateRangeFilter} 
                  onChange={(e) => setDateRangeFilter(e.target.value)}
                  options={[
                    { label: 'All Time', value: 'all' },
                    { label: 'Today', value: 'today' },
                    { label: 'Last 7 Days', value: 'week' },
                    { label: 'Last 30 Days', value: 'month' }
                  ]}
                />
              </div>
              <div className="filter-group">
                <label htmlFor="status-filter-stats">Status:</label>
                <HTMLSelect 
                  id="status-filter-stats"
                  value={statusFilter} 
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { label: 'All', value: 'all' },
                    { label: 'Completed', value: 'completed' },
                    { label: 'Running', value: 'running' },
                    { label: 'Failed', value: 'failed' }
                  ]}
                />
              </div>
            </div>
          </Card>

          {statsLoading ? (
            <Card>
              <NonIdealState
                icon={<Spinner />}
                title="Loading Statistics"
                description="Calculating aggregate metrics..."
              />
            </Card>
          ) : aggregateStats ? (
            <>
              <div className="aggregate-stats-grid">
                <Card className="aggregate-stat-card">
                  <div className="aggregate-stat-icon">📊</div>
                  <div className="aggregate-stat-value">{aggregateStats.total_teams}</div>
                  <div className="aggregate-stat-label">Total Teams</div>
                </Card>
                <Card className="aggregate-stat-card">
                  <div className="aggregate-stat-icon">⏱</div>
                  <div className="aggregate-stat-value">{aggregateStats.total_runtime.toFixed(1)}s</div>
                  <div className="aggregate-stat-label">Total Runtime</div>
                  <div className="aggregate-stat-sublabel">Avg: {aggregateStats.avg_runtime.toFixed(1)}s</div>
                </Card>
                <Card className="aggregate-stat-card">
                  <div className="aggregate-stat-icon">💳</div>
                  <div className="aggregate-stat-value">{aggregateStats.total_credits.toFixed(2)}</div>
                  <div className="aggregate-stat-label">Total Credits</div>
                  <div className="aggregate-stat-sublabel">Avg: {aggregateStats.avg_credits.toFixed(2)}</div>
                </Card>
                <Card className="aggregate-stat-card">
                  <div className="aggregate-stat-icon">📡</div>
                  <div className="aggregate-stat-value">{aggregateStats.total_api_calls}</div>
                  <div className="aggregate-stat-label">Total API Calls</div>
                  <div className="aggregate-stat-sublabel">Avg: {aggregateStats.avg_api_calls.toFixed(1)}</div>
                </Card>
                <Card className="aggregate-stat-card">
                  <div className="aggregate-stat-icon">🎯</div>
                  <div className="aggregate-stat-value">{aggregateStats.total_entities}</div>
                  <div className="aggregate-stat-label">Total Entities</div>
                  <div className="aggregate-stat-sublabel">Avg: {aggregateStats.avg_entities.toFixed(1)}</div>
                </Card>
              </div>

              {aggregateStats.cost_trends && aggregateStats.cost_trends.length > 0 && (
                <Card className="cost-trends-card">
                  <h3>Cost Trends Over Time</h3>
                  <div className="cost-trends-chart">
                    <div className="chart-bars">
                      {aggregateStats.cost_trends.map((trend, idx) => {
                        const maxCredits = Math.max(...aggregateStats.cost_trends.map(t => t.credits));
                        const height = maxCredits > 0 ? (trend.credits / maxCredits) * 100 : 0;
                        return (
                          <div key={idx} className="chart-bar-group">
                            <div 
                              className="chart-bar" 
                              style={{ height: `${height}%` }}
                              title={`${trend.date}: ${trend.credits.toFixed(2)} credits`}
                            >
                              <div className="chart-bar-value">{trend.credits.toFixed(1)}</div>
                            </div>
                            <div className="chart-bar-label">{trend.date}</div>
                            <div className="chart-bar-sublabel">{trend.count} teams</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </Card>
              )}

              {aggregateStats.top_consumers && aggregateStats.top_consumers.length > 0 && (
                <Card className="top-consumers-card">
                  <h3>Top Resource-Consuming Teams</h3>
                  <HTMLTable striped className="top-consumers-table">
                    <thead>
                      <tr>
                        <th>Team ID</th>
                        <th>Topic</th>
                        <th>Runtime</th>
                        <th>Credits</th>
                        <th>API Calls</th>
                        <th>Created</th>
                      </tr>
                    </thead>
                    <tbody>
                      {aggregateStats.top_consumers.map((consumer) => (
                        <tr 
                          key={consumer.team_id}
                          onClick={() => handleTeamClick(consumer.team_id)}
                          style={{ cursor: 'pointer' }}
                        >
                          <td><code>{consumer.team_id.substring(0, 8)}...</code></td>
                          <td>{consumer.topic}</td>
                          <td>{consumer.runtime.toFixed(1)}s</td>
                          <td>{consumer.credits.toFixed(2)}</td>
                          <td>{consumer.api_calls}</td>
                          <td>{formatDate(consumer.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </HTMLTable>
                </Card>
              )}
              
              {/* Export Stats Section */}
              <Card className="export-stats-card">
                <h3>Export Statistics</h3>
                <p style={{ marginBottom: '1rem', color: '#5c7080' }}>
                  Export execution statistics for all teams matching the current filters.
                </p>
                <div className="export-buttons">
                  <Button
                    icon="download"
                    intent={Intent.PRIMARY}
                    onClick={async () => {
                      try {
                        const params = {
                          format: 'csv',
                          ...(statusFilter !== 'all' && { status: statusFilter }),
                          ...(dateRangeFilter !== 'all' && (() => {
                            const now = new Date();
                            let startDate;
                            switch (dateRangeFilter) {
                              case 'today':
                                startDate = new Date(now.setHours(0, 0, 0, 0));
                                break;
                              case 'week':
                                startDate = new Date(now.setDate(now.getDate() - 7));
                                break;
                              case 'month':
                                startDate = new Date(now.setMonth(now.getMonth() - 1));
                                break;
                              default:
                                startDate = null;
                            }
                            return startDate ? { start_date: startDate.toISOString() } : {};
                          })())
                        };
                        
                        const response = await agentTeamsAPI.exportStats(params);
                        const blob = new Blob([response.data], { type: 'text/csv' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `team_stats_export_${new Date().toISOString().split('T')[0]}.csv`;
                        a.click();
                        URL.revokeObjectURL(url);
                      } catch (err) {
                        console.error('Failed to export stats:', err);
                      }
                    }}
                  >
                    Export as CSV
                  </Button>
                  <Button
                    icon="download"
                    onClick={async () => {
                      try {
                        const params = {
                          format: 'json',
                          ...(statusFilter !== 'all' && { status: statusFilter }),
                          ...(dateRangeFilter !== 'all' && (() => {
                            const now = new Date();
                            let startDate;
                            switch (dateRangeFilter) {
                              case 'today':
                                startDate = new Date(now.setHours(0, 0, 0, 0));
                                break;
                              case 'week':
                                startDate = new Date(now.setDate(now.getDate() - 7));
                                break;
                              case 'month':
                                startDate = new Date(now.setMonth(now.getMonth() - 1));
                                break;
                              default:
                                startDate = null;
                            }
                            return startDate ? { start_date: startDate.toISOString() } : {};
                          })())
                        };
                        
                        const response = await agentTeamsAPI.exportStats(params);
                        const blob = new Blob([response.data], { type: 'application/json' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `team_stats_export_${new Date().toISOString().split('T')[0]}.json`;
                        a.click();
                        URL.revokeObjectURL(url);
                      } catch (err) {
                        console.error('Failed to export stats:', err);
                      }
                    }}
                  >
                    Export as JSON
                  </Button>
                </div>
              </Card>
            </>
          ) : (
            <Card>
              <NonIdealState
                icon="chart"
                title="No Statistics Available"
                description="No execution statistics available for the selected filters."
              />
            </Card>
          )}
        </div>
      )}

      {selectedTab === 'teams' && (
        <>
          <Card className="dashboard-controls">
            <div className="filter-section">
              <label htmlFor="status-filter">Filter by Status:</label>
              <HTMLSelect 
                id="status-filter"
                value={statusFilter} 
                onChange={handleStatusFilterChange}
                options={[
                  { label: 'All', value: 'all' },
                  { label: 'Pending', value: 'pending' },
                  { label: 'Running', value: 'running' },
                  { label: 'Completed', value: 'completed' },
                  { label: 'Failed', value: 'failed' }
                ]}
              />
            </div>
            <div className="teams-count">
              Showing {filteredTeams.length} of {teams.length} teams
            </div>
          </Card>

          <Card className="teams-list">
            {teams.length === 0 ? (
              <NonIdealState
                icon="inbox"
                title="No Agent Teams"
                description="No agent teams yet. Create one to get started!"
              />
            ) : filteredTeams.length === 0 ? (
              <NonIdealState
                icon="filter"
                title="No Matching Teams"
                description="No teams match the selected filter."
              />
            ) : (
              <HTMLTable interactive striped className="teams-table">
                <thead>
                  <tr>
                    <th>Team ID</th>
                    <th>Topic</th>
                    <th>Status</th>
                    <th>Model</th>
                    <th>Duration</th>
                    <th>Entities</th>
                    <th>Version</th>
                    <th>Created At</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTeams.map((team) => (
                    <tr 
                      key={team.team_id} 
                      onClick={() => handleTeamClick(team.team_id)}
                      className="team-row"
                    >
                      <td className="team-id-cell">
                        <code>{team.team_id.substring(0, 8)}...</code>
                      </td>
                      <td className="topic-cell">{team.topic}</td>
                      <td>
                        <Tag intent={getStatusIntent(team.status)} minimal>
                          {team.status}
                        </Tag>
                      </td>
                      <td className="model-cell">
                        {team.model_name ? (
                          <Tag minimal small>
                            {team.model_name}
                          </Tag>
                        ) : '-'}
                      </td>
                      <td className="duration-cell">
                        {team.duration_seconds ? (
                          <span>{formatDuration(Math.round(team.duration_seconds))}</span>
                        ) : '-'}
                      </td>
                      <td className="entity-count-cell">
                        {team.status === 'completed' ? (
                          <Tag intent={Intent.SUCCESS} minimal round>
                            {getEntityCount(team)}
                          </Tag>
                        ) : '-'}
                      </td>
                      <td className="version-cell">
                        {team.git_sha && team.git_repo_url ? (
                          <a 
                            href={`${team.git_repo_url}/commit/${team.git_sha}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            title={team.git_sha}
                          >
                            <code>{team.git_sha.substring(0, 7)}</code>
                          </a>
                        ) : team.git_sha ? (
                          <code title={team.git_sha}>{team.git_sha.substring(0, 7)}</code>
                        ) : '-'}
                      </td>
                      <td>{formatDate(team.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </HTMLTable>
            )}
          </Card>
        </>
      )}

      {showCreateModal && (
        <CreateTeamModal
          onClose={() => {
            setShowCreateModal(false);
            setRetryData(null);
          }}
          onTeamCreated={handleTeamCreated}
          retryData={retryData}
        />
      )}
    </div>
  );
}

export default Dashboard;
