const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const API_BASE = `${API_URL}/api`;

export const workflowsApi = {
  async deploy(repoId, port) {
    const response = await fetch(`${API_BASE}/repos/${repoId}/deploy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ port }),
    });
    return response.json();
  },
};
