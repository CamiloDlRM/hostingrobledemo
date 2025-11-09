const API_URL = 'http://localhost:8000';

export const workflowsApi = {
  async deploy(repoId, port) {
    const response = await fetch(`${API_URL}/repos/${repoId}/deploy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port }),
    });
    return response.json();
  },
};
