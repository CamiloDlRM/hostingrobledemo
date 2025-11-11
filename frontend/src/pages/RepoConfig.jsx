import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RepoSelector from '../components/RepoSelector';

export default function RepoConfig() {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleRepoSubmit = async (data) => {
    try {
      setLoading(true);
      setMessage('');

      // Get or create demo user ID
      let userId = localStorage.getItem('userId');
      if (!userId) {
        userId = 'demo-user-' + Date.now();
        localStorage.setItem('userId', userId);

        // Create demo user in backend
        const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
        await fetch(`${backendUrl}/api/users`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: 'demo-user',
            email: 'demo@example.com'
          }),
        }).catch(() => {
          // User might already exist, ignore error
        });
      }

      setMessage('Forking repository to organization...');

      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/repos?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fork repository');
      }

      const result = await response.json();

      setSuccess(true);
      setMessage(
        `Repository forked successfully!\n` +
        `Fork: ${result.forked_repo_url}\n` +
        `Workflow with cron schedule added automatically.`
      );

      // Navigate to dashboard after 3 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 3000);
    } catch (error) {
      console.error('Error:', error);
      setMessage('Error: ' + error.message);
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Add New Repository</h1>
      <p style={styles.subtitle}>
        Enter a GitHub repository URL. We'll fork it to our organization and set up
        automatic deployments with cron scheduling.
      </p>

      {success ? (
        <div style={styles.success}>
          <h2 style={styles.successTitle}>✓ Success!</h2>
          <pre style={styles.message}>{message}</pre>
          <p style={styles.redirectText}>Redirecting to dashboard...</p>
        </div>
      ) : loading ? (
        <div style={styles.loading}>
          <div style={styles.spinner}></div>
          <p style={styles.loadingText}>{message || 'Processing...'}</p>
        </div>
      ) : (
        <RepoSelector onContinue={handleRepoSubmit} />
      )}

      {!success && !loading && message && (
        <div style={styles.error}>
          <p>{message}</p>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { maxWidth: '800px', margin: '0 auto', padding: '40px 20px' },
  title: {
    color: '#000',
    fontSize: '32px',
    fontWeight: 'bold',
    marginBottom: '12px',
  },
  subtitle: {
    color: '#666',
    fontSize: '16px',
    marginBottom: '40px',
    lineHeight: '1.6',
  },
  loading: {
    textAlign: 'center',
    padding: '60px 20px',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid #f3f3f3',
    borderTop: '4px solid #000',
    borderRadius: '50%',
    margin: '0 auto 20px',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    color: '#666',
    fontSize: '16px',
  },
  success: {
    textAlign: 'center',
    padding: '60px 20px',
    backgroundColor: '#f0fff0',
    border: '2px solid #00aa00',
  },
  successTitle: {
    color: '#00aa00',
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '20px',
  },
  message: {
    color: '#000',
    fontSize: '14px',
    fontFamily: 'monospace',
    textAlign: 'left',
    whiteSpace: 'pre-wrap',
    backgroundColor: '#fff',
    padding: '20px',
    border: '1px solid #ddd',
    marginBottom: '20px',
  },
  redirectText: {
    color: '#666',
    fontSize: '14px',
  },
  error: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#fff0f0',
    border: '2px solid #ff0000',
    color: '#cc0000',
  },
};
