const API_URL = 'http://localhost:8000';

export const deploymentsApi = {
  async list(repoId) {
    const response = await fetch(`${API_URL}/repos/${repoId}/deployments`);
    return response.json();
  },

  async get(deploymentId) {
    const response = await fetch(`${API_URL}/deployments/${deploymentId}`);
    return response.json();
  },

  async getLogs(deploymentId) {
    const response = await fetch(`${API_URL}/deployments/${deploymentId}/logs`);
    return response.json();
  },
};
