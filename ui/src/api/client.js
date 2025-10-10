import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const agentTeamsAPI = {
  getAll: () => apiClient.get('/agent-teams'),
  getById: (id) => apiClient.get(`/agent-teams/${id}`),
  create: (data) => apiClient.post('/agent-teams', data),
  getTrace: (id) => apiClient.get(`/agent-teams/${id}/trace`),
  getExecutionStats: (id) => apiClient.get(`/agent-teams/${id}/execution-stats`),
  getAgentConfiguration: () => apiClient.get('/agent-configuration'),
  getAggregateStats: (params) => apiClient.get('/stats/aggregate', { params }),
  exportStats: (params) => apiClient.get('/stats/export', { params, responseType: 'blob' }),
};

export default apiClient;
