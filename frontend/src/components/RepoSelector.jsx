import { useState } from 'react';

export default function RepoSelector({ onContinue }) {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [technology, setTechnology] = useState('react-vite');
  const [cronSchedule, setCronSchedule] = useState('0 */6 * * *');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!repoUrl.trim()) {
      alert('Please enter a repository URL');
      return;
    }
    onContinue({
      repo_url: repoUrl,
      branch,
      technology,
      cron_schedule: cronSchedule
    });
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Configure Repository</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        {/* Repository URL */}
        <div style={styles.field}>
          <label style={styles.label}>Repository URL</label>
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repo"
            style={styles.input}
          />
        </div>

        {/* Branch */}
        <div style={styles.field}>
          <label style={styles.label}>Branch</label>
          <input
            type="text"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="main"
            style={styles.input}
          />
        </div>

        {/* Technology */}
        <div style={styles.field}>
          <label style={styles.label}>Technology</label>
          <select
            value={technology}
            onChange={(e) => setTechnology(e.target.value)}
            style={styles.select}
          >
            <option value="react-vite">React + Vite</option>
            <option value="fastapi">FastAPI</option>
            <option value="nestjs">NestJS</option>
          </select>
        </div>

        {/* Cron Schedule */}
        <div style={styles.field}>
          <label style={styles.label}>Cron Schedule</label>
          <input
            type="text"
            value={cronSchedule}
            onChange={(e) => setCronSchedule(e.target.value)}
            placeholder="0 */6 * * *"
            style={styles.input}
          />
          <small style={styles.hint}>
            Cron expression for automatic deployments (default: every 6 hours)
          </small>
        </div>

        {/* Submit Button */}
        <button type="submit" style={styles.button}>
          Fork & Setup Workflow
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '20px',
  },
  title: {
    color: '#000',
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '20px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    color: '#000',
    fontSize: '14px',
    fontWeight: '500',
  },
  input: {
    padding: '10px',
    border: '1px solid #000',
    backgroundColor: '#fff',
    color: '#000',
    fontSize: '14px',
    fontFamily: 'monospace',
  },
  select: {
    padding: '10px',
    border: '1px solid #000',
    backgroundColor: '#fff',
    color: '#000',
    fontSize: '14px',
    fontFamily: 'monospace',
  },
  button: {
    padding: '12px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
    marginTop: '10px',
  },
  hint: {
    color: '#666',
    fontSize: '12px',
    fontStyle: 'italic',
  },
};
