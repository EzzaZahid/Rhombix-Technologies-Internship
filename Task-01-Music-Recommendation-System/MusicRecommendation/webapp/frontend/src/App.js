import React, { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import Train from './pages/Train';
import Recommend from './pages/Recommend';
import Metrics from './pages/Metrics';
import Features from './pages/Features';
import './App.css';

const NAV = [
  { id: 'dashboard', label: 'Dashboard',   icon: '◈' },
  { id: 'train',     label: 'Train Model', icon: '⬡' },
  { id: 'recommend', label: 'Recommend',   icon: '▶' },
  { id: 'metrics',   label: 'Metrics',     icon: '◉' },
  { id: 'features',  label: 'Features',    icon: '◫' },
];

export default function App() {
  const [page, setPage] = useState('dashboard');
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const poll = () =>
      fetch('/api/status').then(r => r.json()).then(setStatus).catch(() => {});
    poll();
    const id = setInterval(poll, 2000);
    return () => clearInterval(id);
  }, []);

  const pages = {
    dashboard: Dashboard,
    train: Train,
    recommend: Recommend,
    metrics: Metrics,
    features: Features
  };
  const Page = pages[page];

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">♫</span>
          <span className="logo-text">MusicRec</span>
        </div>
        <nav className="sidebar-nav">
          {NAV.map(n => (
            <button
              key={n.id}
              className={`nav-item ${page === n.id ? 'active' : ''}`}
              onClick={() => setPage(n.id)}
            >
              <span className="nav-icon">{n.icon}</span>
              <span className="nav-label">{n.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-status">
          <div className={`status-dot ${status?.status || 'idle'}`} />
          <span className="status-text">
            {status?.status === 'ready'      ? 'Model Ready' :
             status?.status === 'training'   ? 'Training...' :
             status?.status === 'generating' ? 'Generating...' :
             status?.status === 'error'      ? 'Error' : 'No Model'}
          </span>
        </div>
      </aside>
      <main className="content">
        <Page status={status} />
      </main>
    </div>
  );
}