import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DeployStatus from '../components/DeployStatus';
import LogsViewer from '../components/LogsViewer';

export default function Deployments() {
  const { deploymentId } = useParams();
  const [showLogs, setShowLogs] = useState(false);
  const navigate = useNavigate();

  const handleViewLogs = () => {
    setShowLogs(true);
  };

  return (
    <div style={styles.container}>
      <button onClick={() => navigate('/dashboard')} style={styles.backButton}>
        ← Back to Dashboard
      </button>

      <DeployStatus 
        deploymentId={deploymentId} 
        onViewLogs={handleViewLogs}
      />

      {showLogs && (
        <div style={styles.logsSection}>
          <LogsViewer deploymentId={deploymentId} />
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '40px 20px',
  },
  backButton: {
    padding: '8px 16px',
    backgroundColor: '#fff',
    color: '#000',
    border: '1px solid #000',
    cursor: 'pointer',
    fontSize: '14px',
    marginBottom: '20px',
  },
  logsSection: {
    marginTop: '40px',
  },
};
