import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleNewDeployment = () => {
    navigate('/repo/new');
  };

  const handleViewDeployments = (repoId) => {
    navigate(`/deployments/${repoId}`);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Deployment Dashboard</h1>
        <button onClick={handleNewDeployment} style={styles.button}>
          + New Deployment
        </button>
      </div>

      {loading ? (
        <div style={styles.loading}>Loading repositories...</div>
      ) : repos.length === 0 ? (
        <div style={styles.empty}>
          <p>No repositories configured yet.</p>
          <button onClick={handleNewDeployment} style={styles.button}>
            Add Your First Repository
          </button>
        </div>
      ) : (
        <div style={styles.grid}>
          {repos.map((repo) => (
            <div key={repo.id} style={styles.card}>
              <h3 style={styles.cardTitle}>{repo.repo_name}</h3>
              <p style={styles.cardInfo}>Owner: {repo.repo_owner}</p>
              <p style={styles.cardInfo}>Branch: {repo.branch}</p>
              <p style={styles.cardInfo}>Tech: {repo.technology}</p>
              <button
                onClick={() => handleViewDeployments(repo.id)}
                style={styles.cardButton}
              >
                View Deployments
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: { maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '40px',
  },
  title: { color: '#000', fontSize: '32px', fontWeight: 'bold', margin: 0 },
  button: {
    padding: '12px 24px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  loading: { color: '#666', textAlign: 'center', padding: '40px' },
  empty: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#666',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px',
  },
  card: {
    border: '1px solid #000',
    padding: '20px',
    backgroundColor: '#fff',
  },
  cardTitle: { color: '#000', fontSize: '18px', fontWeight: 'bold', marginBottom: '12px' },
  cardInfo: { color: '#666', fontSize: '14px', marginBottom: '8px', fontFamily: 'monospace' },
  cardButton: {
    width: '100%',
    padding: '10px',
    marginTop: '12px',
    backgroundColor: '#fff',
    color: '#000',
    border: '1px solid #000',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
  },
};
