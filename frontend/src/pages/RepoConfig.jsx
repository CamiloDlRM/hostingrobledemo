import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RepoSelector from '../components/RepoSelector';
import SettingsForm from '../components/SettingsForm';

export default function RepoConfig() {
  const [step, setStep] = useState(1);
  const [repoData, setRepoData] = useState(null);
  const [repoId, setRepoId] = useState(null);
  const navigate = useNavigate();

  const handleRepoSubmit = async (data) => {
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) {
        alert('Please login first');
        return;
      }

      const response = await fetch(`http://localhost:8000/repos?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error('Failed to create repository');

      const result = await response.json();
      setRepoData(data);
      setRepoId(result.id);
      setStep(2);
    } catch (error) {
      console.error('Error:', error);
      alert('Error creating repository: ' + error.message);
    }
  };

  const handleSettingsSubmit = async (settings) => {
    try {
      const saveSettingsResponse = await fetch(
        `http://localhost:8000/repos/${repoId}/settings`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            env_vars: settings.envVars,
            build_args: settings.buildArgs,
          }),
        }
      );

      if (!saveSettingsResponse.ok) throw new Error('Failed to save settings');

      const deployResponse = await fetch(
        `http://localhost:8000/repos/${repoId}/deploy`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ port: settings.port }),
        }
      );

      if (!deployResponse.ok) throw new Error('Failed to start deployment');

      const deployResult = await deployResponse.json();
      navigate(`/deployment/${deployResult.deployment_id}`);
    } catch (error) {
      console.error('Error:', error);
      alert('Error starting deployment: ' + error.message);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.steps}>
        <div style={step === 1 ? styles.stepActive : styles.step}>1. Repository</div>
        <div style={step === 2 ? styles.stepActive : styles.step}>2. Settings</div>
      </div>

      {step === 1 && <RepoSelector onContinue={handleRepoSubmit} />}
      {step === 2 && <SettingsForm onSubmit={handleSettingsSubmit} />}
    </div>
  );
}

const styles = {
  container: { maxWidth: '800px', margin: '0 auto', padding: '40px 20px' },
  steps: {
    display: 'flex',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '40px',
  },
  step: {
    padding: '12px 24px',
    backgroundColor: '#f5f5f5',
    color: '#666',
    border: '1px solid #ccc',
    fontWeight: 'bold',
  },
  stepActive: {
    padding: '12px 24px',
    backgroundColor: '#000',
    color: '#fff',
    border: '1px solid #000',
    fontWeight: 'bold',
  },
};
