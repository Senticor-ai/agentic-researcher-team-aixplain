import { useState } from 'react';
import { Card, Button, Tag, Intent, Callout, NonIdealState, Collapse } from '@blueprintjs/core';
import './SachstandDisplay.css';

function SachstandDisplay({ sachstand, teamStatus, teamId }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const formatJSON = (obj) => {
    return JSON.stringify(obj, null, 2);
  };

  const validateJSONLD = (data) => {
    if (!data) return { valid: false, message: 'No data' };
    
    // Check for required JSON-LD fields
    if (!data['@context']) {
      return { valid: false, message: 'Missing @context' };
    }
    if (!data['@type']) {
      return { valid: false, message: 'Missing @type' };
    }
    
    return { valid: true, message: 'Valid JSON-LD' };
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(formatJSON(sachstand));
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const downloadSachstand = () => {
    const dataStr = formatJSON(sachstand);
    const dataBlob = new Blob([dataStr], { type: 'application/ld+json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sachstand_${teamId}.jsonld`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const openInNewTab = () => {
    const dataStr = formatJSON(sachstand);
    const blob = new Blob([dataStr], { type: 'application/ld+json' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  const getCompletionIntent = (status) => {
    switch (status) {
      case 'complete':
        return Intent.SUCCESS;
      case 'partial':
        return Intent.WARNING;
      case 'failed':
      case 'error':
        return Intent.DANGER;
      default:
        return Intent.NONE;
    }
  };

  const getCompletionLabel = (status) => {
    switch (status) {
      case 'complete':
        return '✓ Complete';
      case 'partial':
        return '⚠ Partial';
      case 'failed':
        return '✗ Failed';
      case 'error':
        return '✗ Error';
      default:
        return 'Unknown';
    }
  };

  // Show loading state
  if (teamStatus === 'pending' || teamStatus === 'running' || teamStatus === 'initializing') {
    return (
      <Card className="sachstand-display">
        <NonIdealState
          icon={<div className="bp5-spinner"><div className="bp5-spinner-animation"></div></div>}
          title="Generating Sachstand"
          description="The team is still working on the research. The Sachstand will be available once the team completes."
        />
      </Card>
    );
  }

  // Show empty state
  if (!sachstand) {
    return (
      <Card className="sachstand-display">
        <NonIdealState
          icon="document"
          title="No Sachstand Available Yet"
          description={
            teamStatus === 'failed' 
              ? 'The team execution failed. No Sachstand was generated.'
              : 'The Sachstand will be available once the team completes its research.'
          }
        />
      </Card>
    );
  }

  const validation = validateJSONLD(sachstand);
  const completionStatus = sachstand.completionStatus || 'unknown';
  const entityCount = sachstand.hasPart?.length || 0;

  return (
    <Card className="sachstand-display">
      <div className="sachstand-header">
        <div className="sachstand-title-section">
          <h3>JSON-LD Sachstand</h3>
          <div className="sachstand-badges">
            <Tag
              large
              intent={getCompletionIntent(completionStatus)}
              icon={completionStatus === 'complete' ? 'tick-circle' : 
                    completionStatus === 'partial' ? 'warning-sign' : 
                    'error'}
            >
              {getCompletionLabel(completionStatus)}
            </Tag>
            <Tag large intent={validation.valid ? Intent.SUCCESS : Intent.DANGER}>
              {validation.valid ? '✓ Valid JSON-LD' : '✗ Invalid JSON-LD'}
            </Tag>
            <Tag large minimal>
              {entityCount} Entities
            </Tag>
          </div>
        </div>

        <div className="sachstand-actions">
          <Button
            icon={copySuccess ? 'tick' : 'duplicate'}
            intent={copySuccess ? Intent.SUCCESS : Intent.NONE}
            onClick={copyToClipboard}
          >
            {copySuccess ? 'Copied!' : 'Copy'}
          </Button>
          <Button
            icon="download"
            onClick={downloadSachstand}
          >
            Download
          </Button>
          <Button
            icon="share"
            onClick={openInNewTab}
          >
            Open in New Tab
          </Button>
        </div>
      </div>

      {completionStatus === 'partial' && sachstand.remainingWork && (
        <Callout intent={Intent.WARNING} className="remaining-work-callout">
          <strong>Partial Results:</strong> The following work remains:
          <ul>
            {Array.isArray(sachstand.remainingWork) ? (
              sachstand.remainingWork.map((work, idx) => (
                <li key={idx}>{work}</li>
              ))
            ) : (
              <li>{sachstand.remainingWork}</li>
            )}
          </ul>
        </Callout>
      )}

      {completionStatus === 'failed' && (
        <Callout intent={Intent.DANGER} className="error-callout">
          <strong>Execution Failed:</strong> The team was unable to complete the research successfully.
        </Callout>
      )}

      <div className="sachstand-metadata">
        <div className="metadata-row">
          <span className="metadata-label">Report Name:</span>
          <span className="metadata-value">{sachstand.name}</span>
        </div>
        <div className="metadata-row">
          <span className="metadata-label">Created:</span>
          <span className="metadata-value">
            {sachstand.dateCreated ? new Date(sachstand.dateCreated).toLocaleString() : 'N/A'}
          </span>
        </div>
        <div className="metadata-row">
          <span className="metadata-label">Type:</span>
          <span className="metadata-value">{sachstand['@type']}</span>
        </div>
        {sachstand.author && (
          <div className="metadata-row">
            <span className="metadata-label">Author:</span>
            <span className="metadata-value">
              {sachstand.author.name} v{sachstand.author.version}
            </span>
          </div>
        )}
      </div>

      <div className="sachstand-content">
        <div className="sachstand-content-header">
          <h4>Full JSON-LD Document</h4>
          <Button
            minimal
            small
            icon={isExpanded ? 'chevron-up' : 'chevron-down'}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? 'Collapse' : 'Expand'}
          </Button>
        </div>

        <Collapse isOpen={isExpanded}>
          <div className="json-viewer">
            <pre className="json-content">{formatJSON(sachstand)}</pre>
          </div>
        </Collapse>

        {!isExpanded && (
          <div className="json-preview">
            <pre className="json-content">{formatJSON(sachstand).split('\n').slice(0, 10).join('\n')}
...
(Click "Expand" to see full document)</pre>
          </div>
        )}
      </div>
    </Card>
  );
}

export default SachstandDisplay;
