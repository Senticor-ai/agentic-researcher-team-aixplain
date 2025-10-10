import { useState } from 'react';
import { Card, HTMLSelect, InputGroup, Button, Tag, Callout, NonIdealState, Intent } from '@blueprintjs/core';
import EntityCard from './EntityCard';
import './EntitiesDisplay.css';

function EntitiesDisplay({ entities, isLoading = false, teamStatus, onRetry }) {
  const [filterType, setFilterType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Group entities by type
  const groupedEntities = entities.reduce((acc, entity) => {
    const type = entity['@type'] || entity.type || 'Unknown';
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(entity);
    return acc;
  }, {});

  // Get unique entity types for filter
  const entityTypes = ['all', ...Object.keys(groupedEntities).sort()];

  // Filter entities
  const getFilteredEntities = () => {
    let filtered = entities;

    // Filter by type
    if (filterType !== 'all') {
      filtered = filtered.filter(entity => 
        (entity['@type'] || entity.type) === filterType
      );
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(entity =>
        entity.name?.toLowerCase().includes(query) ||
        entity.description?.toLowerCase().includes(query) ||
        entity.jobTitle?.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredEntities = getFilteredEntities();

  // Group filtered entities by type
  const filteredGrouped = filteredEntities.reduce((acc, entity) => {
    const type = entity['@type'] || entity.type || 'Unknown';
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(entity);
    return acc;
  }, {});

  const hasFilters = filterType !== 'all' || searchQuery.trim() !== '';

  const clearFilters = () => {
    setFilterType('all');
    setSearchQuery('');
  };

  const highlightMatch = (text, query) => {
    if (!query.trim() || !text) return text;
    
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <mark key={i} className="search-highlight">{part}</mark> : 
        part
    );
  };

  if (isLoading) {
    return (
      <Card className="entities-display">
        <div className="loading-skeleton">
          <div className="skeleton-line"></div>
          <div className="skeleton-line"></div>
          <div className="skeleton-line short"></div>
        </div>
      </Card>
    );
  }

  // Handle failed team execution
  if (teamStatus === 'failed') {
    return (
      <Card className="entities-display">
        <NonIdealState
          icon="error"
          title="Entity Extraction Failed"
          description={
            <div className="error-description">
              <p>The team was unable to extract entities from the research.</p>
              <Callout intent={Intent.DANGER} className="troubleshooting-tips">
                <strong>Common Issues:</strong>
                <ul>
                  <li>API key permissions or tool access issues</li>
                  <li>Topic too specific or no information available online</li>
                  <li>Network or timeout issues during execution</li>
                  <li>Agent configuration or prompt issues</li>
                </ul>
                <strong>Troubleshooting:</strong>
                <ul>
                  <li>Check the execution log for detailed error messages</li>
                  <li>Try a broader or more well-known topic</li>
                  <li>Verify API keys and tool configurations</li>
                  <li>Review the agent trace for specific failure points</li>
                </ul>
              </Callout>
            </div>
          }
          action={
            onRetry && (
              <Button
                intent={Intent.PRIMARY}
                icon="refresh"
                onClick={onRetry}
              >
                Create New Team
              </Button>
            )
          }
        />
      </Card>
    );
  }

  // Handle empty results (team completed but no entities)
  if (!entities || entities.length === 0) {
    if (teamStatus === 'completed') {
      return (
        <Card className="entities-display">
          <NonIdealState
            icon="search"
            title="No Entities Found"
            description={
              <div className="empty-description">
                <p>The team completed its research but did not extract any entities.</p>
                <Callout intent={Intent.WARNING} className="troubleshooting-tips">
                  <strong>Possible Reasons:</strong>
                  <ul>
                    <li>The topic may be too specific or niche</li>
                    <li>Limited information available in online sources</li>
                    <li>Search tools returned no relevant results</li>
                    <li>Entity extraction criteria not met</li>
                  </ul>
                  <strong>Suggestions:</strong>
                  <ul>
                    <li>Try a broader or more general topic</li>
                    <li>Use more common or well-documented subjects</li>
                    <li>Check if the topic exists in mainstream sources</li>
                    <li>Review the execution log for insights</li>
                  </ul>
                </Callout>
              </div>
            }
            action={
              onRetry && (
                <Button
                  intent={Intent.PRIMARY}
                  icon="refresh"
                  onClick={onRetry}
                >
                  Try Different Topic
                </Button>
              )
            }
          />
        </Card>
      );
    }

    // Team still running
    return (
      <Card className="entities-display">
        <NonIdealState
          icon={<div className="bp5-spinner"><div className="bp5-spinner-animation"></div></div>}
          title="Extracting Entities"
          description="The team is working on extracting entities from the research. This may take a few moments..."
        />
      </Card>
    );
  }

  return (
    <Card className="entities-display">
      <div className="entities-header">
        <div className="entities-title-section">
          <h3>Extracted Entities</h3>
          <Tag large intent="primary">
            {entities.length} Total
          </Tag>
        </div>

        <div className="entities-filters">
          <HTMLSelect
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            options={entityTypes.map(type => ({
              label: type === 'all' ? 'All Types' : `${type} (${groupedEntities[type]?.length || 0})`,
              value: type
            }))}
          />
          <InputGroup
            leftIcon="search"
            placeholder="Search entities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            rightElement={
              searchQuery ? (
                <Button
                  icon="cross"
                  minimal
                  small
                  onClick={() => setSearchQuery('')}
                />
              ) : undefined
            }
          />
        </div>
      </div>

      {hasFilters && (
        <div className="filter-status">
          <Callout intent="primary">
            Showing {filteredEntities.length} of {entities.length} entities
            <Button
              minimal
              small
              icon="cross"
              onClick={clearFilters}
              style={{ marginLeft: '1rem' }}
            >
              Clear Filters
            </Button>
          </Callout>
        </div>
      )}

      {filteredEntities.length === 0 ? (
        <NonIdealState
          icon="filter"
          title="No Matching Entities"
          description="Try adjusting your filters or search query."
          action={
            <Button onClick={clearFilters} icon="cross">
              Clear Filters
            </Button>
          }
        />
      ) : (
        <div className="entities-groups">
          {Object.entries(filteredGrouped)
            .sort(([typeA], [typeB]) => typeA.localeCompare(typeB))
            .map(([type, typeEntities]) => (
              <div key={type} className="entity-type-group">
                <div className="entity-type-header">
                  <h4>{type}</h4>
                  <Tag minimal>{typeEntities.length}</Tag>
                </div>
                <div className="entity-type-list">
                  {typeEntities.map((entity, idx) => (
                    <EntityCard
                      key={idx}
                      entity={{
                        ...entity,
                        name: searchQuery ? highlightMatch(entity.name, searchQuery) : entity.name,
                        description: searchQuery && entity.description ? 
                          highlightMatch(entity.description, searchQuery) : 
                          entity.description
                      }}
                    />
                  ))}
                </div>
              </div>
            ))}
        </div>
      )}
    </Card>
  );
}

export default EntitiesDisplay;
