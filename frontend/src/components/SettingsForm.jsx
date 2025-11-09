import { useState } from 'react';

export default function SettingsForm({ onSubmit }) {
  const [envVars, setEnvVars] = useState([{ key: '', value: '' }]);
  const [buildArgs, setBuildArgs] = useState([{ key: '', value: '' }]);
  const [port, setPort] = useState('');

  const addEnvVar = () => {
    setEnvVars([...envVars, { key: '', value: '' }]);
  };

  const removeEnvVar = (index) => {
    setEnvVars(envVars.filter((_, i) => i !== index));
  };

  const updateEnvVar = (index, field, value) => {
    const updated = [...envVars];
    updated[index][field] = value;
    setEnvVars(updated);
  };

  const addBuildArg = () => {
    setBuildArgs([...buildArgs, { key: '', value: '' }]);
  };

  const removeBuildArg = (index) => {
    setBuildArgs(buildArgs.filter((_, i) => i !== index));
  };

  const updateBuildArg = (index, field, value) => {
    const updated = [...buildArgs];
    updated[index][field] = value;
    setBuildArgs(updated);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!port || port < 1 || port > 65535) {
      alert('Please enter a valid port (1-65535)');
      return;
    }

    const envVarsObj = {};
    envVars.forEach(({ key, value }) => {
      if (key.trim()) envVarsObj[key] = value;
    });

    const buildArgsObj = {};
    buildArgs.forEach(({ key, value }) => {
      if (key.trim()) buildArgsObj[key] = value;
    });

    onSubmit({ envVars: envVarsObj, buildArgs: buildArgsObj, port: parseInt(port) });
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Configure Settings</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        {/* Port */}
        <div style={styles.section}>
          <h3 style={styles.sectionTitle}>Port</h3>
          <input
            type="number"
            value={port}
            onChange={(e) => setPort(e.target.value)}
            placeholder="3000"
            style={styles.input}
            min="1"
            max="65535"
          />
        </div>

        {/* Environment Variables */}
        <div style={styles.section}>
          <h3 style={styles.sectionTitle}>Environment Variables</h3>
          {envVars.map((env, index) => (
            <div key={index} style={styles.kvPair}>
              <input
                type="text"
                placeholder="KEY"
                value={env.key}
                onChange={(e) => updateEnvVar(index, 'key', e.target.value)}
                style={styles.kvInput}
              />
              <input
                type="text"
                placeholder="value"
                value={env.value}
                onChange={(e) => updateEnvVar(index, 'value', e.target.value)}
                style={styles.kvInput}
              />
              <button
                type="button"
                onClick={() => removeEnvVar(index)}
                style={styles.removeBtn}
              >
                -
              </button>
            </div>
          ))}
          <button type="button" onClick={addEnvVar} style={styles.addBtn}>
            + Add Variable
          </button>
        </div>

        {/* Build Arguments */}
        <div style={styles.section}>
          <h3 style={styles.sectionTitle}>Build Arguments</h3>
          {buildArgs.map((arg, index) => (
            <div key={index} style={styles.kvPair}>
              <input
                type="text"
                placeholder="ARG"
                value={arg.key}
                onChange={(e) => updateBuildArg(index, 'key', e.target.value)}
                style={styles.kvInput}
              />
              <input
                type="text"
                placeholder="value"
                value={arg.value}
                onChange={(e) => updateBuildArg(index, 'value', e.target.value)}
                style={styles.kvInput}
              />
              <button
                type="button"
                onClick={() => removeBuildArg(index)}
                style={styles.removeBtn}
              >
                -
              </button>
            </div>
          ))}
          <button type="button" onClick={addBuildArg} style={styles.addBtn}>
            + Add Argument
          </button>
        </div>

        <button type="submit" style={styles.submitBtn}>
          Save and Deploy
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: { maxWidth: '600px', margin: '0 auto', padding: '20px' },
  title: { color: '#000', fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' },
  form: { display: 'flex', flexDirection: 'column', gap: '24px' },
  section: { display: 'flex', flexDirection: 'column', gap: '12px' },
  sectionTitle: { color: '#000', fontSize: '18px', fontWeight: '600' },
  kvPair: { display: 'flex', gap: '8px' },
  kvInput: {
    flex: 1,
    padding: '8px',
    border: '1px solid #000',
    backgroundColor: '#fff',
    color: '#000',
    fontFamily: 'monospace',
  },
  input: {
    padding: '10px',
    border: '1px solid #000',
    backgroundColor: '#fff',
    color: '#000',
    fontFamily: 'monospace',
  },
  removeBtn: {
    padding: '8px 16px',
    backgroundColor: '#fff',
    color: '#000',
    border: '1px solid #000',
    cursor: 'pointer',
  },
  addBtn: {
    padding: '8px',
    backgroundColor: '#fff',
    color: '#000',
    border: '1px solid #000',
    cursor: 'pointer',
    alignSelf: 'flex-start',
  },
  submitBtn: {
    padding: '12px',
    backgroundColor: '#000',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
  },
};
