import { useState } from 'react';
import { Card, Tag, Collapse, Button, Icon } from '@blueprintjs/core';
import './EntityCard.css';

function EntityCard({ entity }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getEntityIcon = (type) => {
    switch (type) {
      case 'Person':
        return '👤';
      case 'Organization':
      case 'GovernmentOrganization':
        return '🏢';
      case 'Event':
        return '📅';
      case 'Place':
        return '📍';
      case 'Legislation':
        return '⚖️';
      case 'CreativeWork':
        return '📄';
      case 'GovernmentService':
        return '🏛️';
      default:
        return '📌';
    }
  };

  const getEntityTypeColor = (type) => {
    switch (type) {
      case 'Person':
        return '#2ecc71';
      case 'Organization':
      case 'GovernmentOrganization':
        return '#3498db';
      case 'Event':
        return '#9b59b6';
      case 'Place':
        return '#e74c3c';
      case 'Legislation':
        return '#f39c12';
      case 'CreativeWork':
        return '#1abc9c';
      case 'GovernmentService':
        return '#34495e';
      default:
        return '#95a5a6';
    }
  };

  return (
    <Card className="entity-card" elevation={1}>
      <div className="entity-card-header">
        <div className="entity-card-title">
          <span className="entity-icon">{getEntityIcon(entity['@type'] || entity.type)}</span>
          <div className="entity-name-section">
            <h4 className="entity-name">{entity.name}</h4>
            <Tag
              minimal
              style={{
                backgroundColor: `${getEntityTypeColor(entity['@type'] || entity.type)}20`,
                color: getEntityTypeColor(entity['@type'] || entity.type),
                borderColor: getEntityTypeColor(entity['@type'] || entity.type)
              }}
            >
              {entity['@type'] || entity.type}
            </Tag>
          </div>
        </div>
        <Button
          minimal
          small
          icon={isExpanded ? 'chevron-up' : 'chevron-down'}
          onClick={() => setIsExpanded(!isExpanded)}
        />
      </div>

      {entity.description && (
        <div className="entity-description">
          {entity.description}
        </div>
      )}

      <Collapse isOpen={isExpanded}>
        <div className="entity-details">
          {/* Properties */}
          {(entity.jobTitle || entity.url) && (
            <div className="entity-properties">
              <h5>Properties</h5>
              {entity.jobTitle && (
                <div className="entity-property">
                  <span className="property-label">Job Title:</span>
                  <span className="property-value">{entity.jobTitle}</span>
                </div>
              )}
              {entity.url && (
                <div className="entity-property">
                  <span className="property-label">URL:</span>
                  <a
                    href={entity.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="property-link"
                  >
                    {entity.url}
                  </a>
                </div>
              )}
            </div>
          )}

          {/* Sources/Citations */}
          {entity.citation && entity.citation.length > 0 && (
            <div className="entity-sources">
              <h5>Sources ({entity.citation.length})</h5>
              <div className="sources-list">
                {entity.citation.map((citation, idx) => (
                  <div key={idx} className="source-item">
                    <div className="source-header">
                      <Icon icon="link" size={12} />
                      <a
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-link"
                      >
                        {citation.url}
                      </a>
                    </div>
                    {citation.excerpt && (
                      <div className="source-excerpt">
                        "{citation.excerpt}"
                      </div>
                    )}
                    {citation.dateAccessed && (
                      <div className="source-date">
                        Accessed: {new Date(citation.dateAccessed).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Wikipedia/Wikidata links */}
          {entity.sameAs && entity.sameAs.length > 0 && (
            <div className="entity-links">
              <h5>External Links</h5>
              <div className="external-links-list">
                {entity.sameAs.map((link, idx) => (
                  <a
                    key={idx}
                    href={link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="external-link"
                  >
                    {link.includes('wikipedia') ? '📖 Wikipedia' : 
                     link.includes('wikidata') ? '🔗 Wikidata' : 
                     '🔗 External Link'}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      </Collapse>
    </Card>
  );
}

export default EntityCard;
