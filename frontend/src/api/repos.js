const API_URL = 'http://localhost:8000';

export const authApi = {
  async getAuthUrl() {
    const response = await fetch(`${API_URL}/auth/github`, { method: 'POST' });
    return response.json();
  },

  async handleCallback(code) {
    const response = await fetch(`${API_URL}/auth/github/callback?code=${code}`);
    return response.json();
  },
};

export const reposApi = {
  async list(userId) {
    const response = await fetch(`${API_URL}/repos?user_id=${userId}`);
    return response.json();
  },

  async create(userId, data) {
    const response = await fetch(`${API_URL}/repos?user_id=${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async getSettings(repoId) {
    const response = await fetch(`${API_URL}/repos/${repoId}/settings`);
    return response.json();
  },

  async saveSettings(repoId, settings) {
    const response = await fetch(`${API_URL}/repos/${repoId}/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings),
    });
    return response.json();
  },
};
