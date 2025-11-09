import { useState, useEffect } from 'react';

export default function DeployStatus({ deploymentId, onViewLogs }) {
  const [deployment, setDeployment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDeployment();
    const interval = setInterval(() => {
      if (deployment && !['success', 'failed'].includes(deployment.status)) {
        fetchDeployment();
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [deploymentId, deployment]);

  const fetchDeployment = async () => {
    try {
      const response = await fetch(`http://localhost:8000/deployments/${deploymentId}`);
      const data = await response.json();
      setDeployment(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching deployment:', error);
      setLoading(false);
    }
  };

  if (loading) return <div style={styles.loading}>Loading...</div>;
  if (!deployment) return <div style={styles.error}>Deployment not found</div>;

  const statusStyles = getStatusStyles(deployment.status);

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Deployment Status</h2>
      
      <div style={{ ...styles.badge, ...statusStyles }}>
        {deployment.status.toUpperCase()}
      </div>

      <div style={styles.info}>
        <div style={styles.row}>
          <span style={styles.label}>Started:</span>
          <span style={styles.value}>{new Date(deployment.started_at).toLocaleString()}</span>
        </div>

        {deployment.finished_at && (
          <div style={styles.row}>
            <span style={styles.label}>Finished:</span>
            <span style={styles.value}>{new Date(deployment.finished_at).toLocaleString()}</span>
          </div>
        )}

        {deployment.domain && deployment.status === 'success' && (
          <div style={styles.row}>
            <span style={styles.label}>URL:</span>
            <a 
              href={`https://${deployment.domain}`} 
              target="_blank" 
              rel="noopener noreferrer"
              style={styles.link}
            >
              {deployment.domain}
            </a>
          </div>
        )}

        {deployment.error_message && deployment.status === 'failed' && (
          <div style={styles.error}>
            <strong>Error:</strong> {deployment.error_message}
          </div>
        )}
      </div>

      {deployment.status === 'failed' && onViewLogs && (
        <button onClick={() => onViewLogs(deploymentId)} style={styles.button}>
          View Logs
        </button>
      )}
    </div>
  );
}

function getStatusStyles(status) {
  switch (status) {
    case 'pending':
      return { backgroundColor: '#f5f5f5', color: '#666', border: '2px solid #ccc' };
    case 'building':
      return { backgroundColor: '#666', color: '#fff', animation: 'pulse 1.5s infinite' };
    case 'deploying':
      return { backgroundColor: '#000', color: '#fff', animation: 'pulse 1.5s infinite' };
    case 'success':
      return { backgroundColor: '#fff', color: '#000', border: '3px solid #000' };
    case 'failed':
      return { backgroundColor: '#8B0000', color: '#fff' };
    default:
      return { backgroundColor: '#f5f5f5', color: '#000' };
  }
}

const styles = {
  container: { maxWidth: '600px', margin: '0 auto', padding: '20px' },
  title: { color: '#000', fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' },
  loading: { color: '#666', textAlign: 'center', padding: '40px' },
  badge: {
    display: 'inline-block',
    padding: '12px 24px',
    fontWeight: 'bold',
    fontSize: '14px',
    marginBottom: '20px',
  },
  info: { display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' },
  row: { display: 'flex', gap: '12px' },
  label: { color: '#666', fontWeight: '600', minWidth: '100px' },
  value: { color: '#000', fontFamily: 'monospace' },
  link: { color: '#000', textDecoration: 'underline' },
  error: { color: '#8B0000', padding: '12px', border: '1px solid #8B0000', marginTop: '12px' },
  button: {
    padding: '12px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
  },
};
