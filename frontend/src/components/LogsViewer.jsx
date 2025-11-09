import { useState, useEffect, useRef } from 'react';

export default function LogsViewer({ deploymentId }) {
  const [logs, setLogs] = useState('');
  const [errors, setErrors] = useState([]);
  const [workflowUrl, setWorkflowUrl] = useState('');
  const [loading, setLoading] = useState(true);
  const logsRef = useRef(null);

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, [deploymentId]);

  useEffect(() => {
    if (logsRef.current) {
      logsRef.current.scrollTop = logsRef.current.scrollHeight;
    }
  }, [logs]);

  const fetchLogs = async () => {
    try {
      const response = await fetch(`http://localhost:8000/deployments/${deploymentId}/logs`);
      const data = await response.json();
      setLogs(data.logs || 'No logs available');
      setErrors(data.errors || []);
      setWorkflowUrl(data.workflow_url || '');
      setLoading(false);
    } catch (error) {
      console.error('Error fetching logs:', error);
      setLogs('Error loading logs');
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Deployment Logs</h2>
        <div style={styles.buttons}>
          <button onClick={fetchLogs} style={styles.button}>
            Refresh
          </button>
          {workflowUrl && (
            <a 
              href={workflowUrl} 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.link}
            >
              View on GitHub
            </a>
          )}
        </div>
      </div>

      {loading && <div style={styles.loading}>Loading logs...</div>}

      {errors.length > 0 && (
        <div style={styles.errorsSection}>
          <h3 style={styles.errorsTitle}>Errors Found:</h3>
          {errors.map((error, index) => (
            <div key={index} style={styles.errorLine}>
              {error}
            </div>
          ))}
        </div>
      )}

      <pre ref={logsRef} style={styles.logs}>
        {logs}
      </pre>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '100%',
    margin: '0 auto',
    padding: '20px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    color: '#000',
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
  },
  buttons: {
    display: 'flex',
    gap: '12px',
  },
  button: {
    padding: '8px 16px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  link: {
    padding: '8px 16px',
    backgroundColor: '#fff',
    color: '#000',
    border: '1px solid #000',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: 'bold',
    display: 'inline-block',
  },
  loading: {
    color: '#666',
    textAlign: 'center',
    padding: '20px',
  },
  errorsSection: {
    marginBottom: '20px',
    padding: '16px',
    backgroundColor: '#fff',
    border: '2px solid #8B0000',
  },
  errorsTitle: {
    color: '#8B0000',
    fontSize: '16px',
    fontWeight: 'bold',
    marginBottom: '12px',
  },
  errorLine: {
    color: '#8B0000',
    fontFamily: 'monospace',
    fontSize: '12px',
    marginBottom: '4px',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-all',
  },
  logs: {
    backgroundColor: '#000',
    color: '#f5f5f5',
    padding: '16px',
    fontFamily: 'monospace',
    fontSize: '12px',
    lineHeight: '1.5',
    overflowX: 'auto',
    overflowY: 'auto',
    maxHeight: '600px',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-all',
    margin: 0,
  },
};
