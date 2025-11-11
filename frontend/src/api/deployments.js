const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api`;

export const deploymentsApi = {
  async list(repoId) {
    const response = await fetch(`${API_BASE}/repos/${repoId}/deployments`);
    return response.json();
  },

  async get(deploymentId) {
    const response = await fetch(`${API_BASE}/deployments/${deploymentId}`);
    return response.json();
  },

  async getLogs(deploymentId) {
    const response = await fetch(`${API_BASE}/deployments/${deploymentId}/logs`);
    return response.json();
  },
};
