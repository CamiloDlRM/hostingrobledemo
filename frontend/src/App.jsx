import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import RepoConfig from './pages/RepoConfig';
import Deployments from './pages/Deployments';

export default function App() {
  return (
    <BrowserRouter>
      <div style={styles.app}>
        <header style={styles.header}>
          <h1 style={styles.logo}>Hosting Roble</h1>
        </header>
        <main style={styles.main}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/repo/new" element={<RepoConfig />} />
            <Route path="/deployment/:deploymentId" element={<Deployments />} />
            <Route path="/deployments/:repoId" element={<Deployments />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#fff',
  },
  header: {
    padding: '20px 40px',
    borderBottom: '2px solid #000',
    backgroundColor: '#fff',
  },
  logo: {
    color: '#000',
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
  },
  main: {
    minHeight: 'calc(100vh - 80px)',
  },
};
