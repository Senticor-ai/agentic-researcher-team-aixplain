import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Dialog, 
  FormGroup, 
  InputGroup, 
  TextArea, 
  Button, 
  Intent,
  Callout
} from '@blueprintjs/core';
import { agentTeamsAPI } from '../api/client';
import '@blueprintjs/core/lib/css/blueprint.css';
import './CreateTeamModal.css';

function CreateTeamModal({ onClose, onTeamCreated, retryData }) {
  const [topic, setTopic] = useState(retryData?.topic || '');
  const [goals, setGoals] = useState(retryData?.goals?.join('\n') || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [topicError, setTopicError] = useState('');
  const navigate = useNavigate();

  const validateTopic = (value) => {
    if (!value.trim()) {
      setTopicError('Topic is required');
      return false;
    }
    // Check for special characters that might cause issues
    const hasSpecialChars = /[<>:"/\\|?*\x00-\x1F]/.test(value);
    if (hasSpecialChars) {
      setTopicError('Topic contains invalid characters (< > : " / \\ | ? *)');
      return false;
    }
    setTopicError('');
    return true;
  };

  const handleTopicChange = (e) => {
    const value = e.target.value;
    setTopic(value);
    if (topicError) {
      validateTopic(value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateTopic(topic)) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await agentTeamsAPI.create({
        topic: topic.trim(),
        goals: goals.trim() ? goals.trim().split('\n').filter(g => g.trim()) : [],
      });

      setSuccess(true);
      
      // Redirect to team detail page after a brief delay
      setTimeout(() => {
        navigate(`/teams/${response.data.team_id}`);
        onTeamCreated();
      }, 1000);
    } catch (err) {
      setError('Failed to create team: ' + (err.response?.data?.detail || err.message));
      setLoading(false);
    }
  };

  return (
    <Dialog
      isOpen={true}
      onClose={onClose}
      title="Create Agent Team"
      icon="add"
      className="create-team-dialog"
    >
      <div className="bp5-dialog-body">
        <form onSubmit={handleSubmit} className="create-team-form">
          <FormGroup
            label="Research Topic"
            labelFor="topic"
            labelInfo="(required)"
            helperText={topicError || "Plain text only - avoid special characters like < > : \" / \\ | ? *"}
            intent={topicError ? Intent.DANGER : Intent.NONE}
          >
            <InputGroup
              id="topic"
              value={topic}
              onChange={handleTopicChange}
              onBlur={() => validateTopic(topic)}
              placeholder="e.g., Wasserstoffnetz Rechtsgrundlage"
              disabled={loading || success}
              intent={topicError ? Intent.DANGER : Intent.NONE}
              autoFocus
            />
          </FormGroup>

          <FormGroup
            label="Research Goals"
            labelFor="goals"
            labelInfo="(optional)"
            helperText="Enter specific research objectives, one per line"
          >
            <TextArea
              id="goals"
              value={goals}
              onChange={(e) => setGoals(e.target.value)}
              placeholder={"Example:\nIdentify key regulations\nFind responsible authorities\nAnalyze legal framework"}
              rows={5}
              disabled={loading || success}
              fill
            />
          </FormGroup>

          {error && (
            <Callout intent={Intent.DANGER} icon="error">
              {error}
            </Callout>
          )}
          
          {success && (
            <Callout intent={Intent.SUCCESS} icon="tick-circle">
              Team created successfully! Redirecting...
            </Callout>
          )}
        </form>
      </div>

      <div className="bp5-dialog-footer">
        <div className="bp5-dialog-footer-actions">
          <Button 
            onClick={onClose}
            disabled={loading || success}
          >
            Cancel
          </Button>
          <Button 
            intent={Intent.PRIMARY}
            onClick={handleSubmit}
            disabled={loading || success}
            loading={loading}
            icon="add"
          >
            Create Team
          </Button>
        </div>
      </div>
    </Dialog>
  );
}

export default CreateTeamModal;
