import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [view, setView] = useState('home');
  const [status, setStatus] = useState('checking...');
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [lastAction, setLastAction] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE = 'http://localhost:8000';

  // Check backend health on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`, { timeout: 5000 });
      setStatus(response.data.status || 'healthy');
    } catch (err) {
      setStatus('backend offline');
      console.error('Health check failed:', err.message);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/auth/register`, { email, password });
      alert(`Registration successful! User ID: ${res.data.id}`);
      setEmail('');
      setPassword('');
      setView('home');
    } catch (err) {
      alert(`Registration failed: ${err.response?.data?.error || err.message}`);
    }
    setIsLoading(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/auth/login`, { email, password });
      const tok = res.data.access_token;
      setToken(tok);
      localStorage.setItem('token', tok);
      setEmail('');
      setPassword('');
      setView('home');
      alert('Login successful!');
    } catch (err) {
      alert(`Login failed: ${err.response?.data?.error || err.message}`);
    }
    setIsLoading(false);
  };

  const handleLogout = () => {
    setToken(null);
    localStorage.removeItem('token');
    setView('home');
  };

  const fetchAnalytics = async () => {
    try {
      const res = await axios.get(`${API_BASE}/analytics/summary`);
      setAnalytics(res.data);
    } catch (err) {
      console.error('Analytics fetch failed:', err);
      setAnalytics({ error: err.message });
    }
  };

  const connectWebSocket = () => {
    setWsStatus('connecting...');
    const ws = new WebSocket(`ws://localhost:8000/ws/emotion`);
    
    ws.onopen = () => {
      setWsStatus('connected');
      console.log('WebSocket connected');
      
      // Send test emotion data
      const testData = {
        emotion_score: 0.7,
        performance_score: 0.6,
        facial_score: 0.65,
        speech_score: 0.75,
        typing_score: 0.55
      };
      ws.send(JSON.stringify(testData));
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLastAction(data.adaptive_action || 'received');
      console.log('WebSocket message:', data);
    };
    
    ws.onerror = (err) => {
      setWsStatus('error: ' + err.message);
      console.error('WebSocket error:', err);
    };
    
    ws.onclose = () => {
      setWsStatus('disconnected');
      console.log('WebSocket disconnected');
    };
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>🧠 Emotion-Adaptive Learning System</h1>
        <div className="status">
          <span className={`status-badge ${status === 'healthy' ? 'healthy' : 'error'}`}>
            Backend: {status}
          </span>
        </div>
      </header>

      {/* Navigation */}
      <nav className="nav">
        <button 
          className={`nav-btn ${view === 'home' ? 'active' : ''}`}
          onClick={() => setView('home')}
        >
          Home
        </button>
        {token && (
          <>
            <button 
              className={`nav-btn ${view === 'test' ? 'active' : ''}`}
              onClick={() => setView('test')}
            >
              WebSocket Test
            </button>
            <button 
              className={`nav-btn ${view === 'analytics' ? 'active' : ''}`}
              onClick={() => setView('analytics')}
            >
              Analytics
            </button>
            <button className="nav-btn logout" onClick={handleLogout}>
              Logout ({email})
            </button>
          </>
        )}
        {!token && (
          <>
            <button 
              className={`nav-btn ${view === 'login' ? 'active' : ''}`}
              onClick={() => setView('login')}
            >
              Login
            </button>
            <button 
              className={`nav-btn ${view === 'register' ? 'active' : ''}`}
              onClick={() => setView('register')}
            >
              Register
            </button>
          </>
        )}
      </nav>

      {/* Main Content */}
      <main className="content">
        {/* Home View */}
        {view === 'home' && (
          <div className="card">
            <h2>Welcome!</h2>
            <p>This is the Emotion-Adaptive Learning System demo.</p>
            {token ? (
              <>
                <p>✓ You are logged in as: <strong>{email}</strong></p>
                <p>Try:</p>
                <ul>
                  <li>Test WebSocket connection</li>
                  <li>View analytics dashboard</li>
                  <li>System status: {status}</li>
                </ul>
              </>
            ) : (
              <p>Please register or login to get started.</p>
            )}
          </div>
        )}

        {/* Login View */}
        {view === 'login' && (
          <div className="card form-card">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? 'Logging in...' : 'Login'}
              </button>
            </form>
          </div>
        )}

        {/* Register View */}
        {view === 'register' && (
          <div className="card form-card">
            <h2>Register</h2>
            <form onSubmit={handleRegister}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <input
                type="password"
                placeholder="Password (min 6 chars)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength="6"
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? 'Registering...' : 'Register'}
              </button>
            </form>
          </div>
        )}

        {/* WebSocket Test View */}
        {token && view === 'test' && (
          <div className="card">
            <h2>WebSocket Test</h2>
            <p>Status: <strong>{wsStatus}</strong></p>
            <button onClick={connectWebSocket} className="btn-primary">
              Connect to Emotion WebSocket
            </button>
            {lastAction && (
              <div className="result">
                <h3>Last Adaptive Action: <span className="action">{lastAction}</span></h3>
              </div>
            )}
            <p className="info">
              Will send test emotion data and log responses. Check browser console for details.
            </p>
          </div>
        )}

        {/* Analytics View */}
        {token && view === 'analytics' && (
          <div className="card">
            <h2>Analytics Dashboard</h2>
            <button onClick={fetchAnalytics} className="btn-primary">
              Fetch Analytics
            </button>
            {analytics && (
              <div className="analytics">
                {analytics.error ? (
                  <p className="error">Error: {analytics.error}</p>
                ) : (
                  <div>
                    <p>Average Emotion: <strong>{analytics.average_emotion?.toFixed(2) || 'N/A'}</strong></p>
                    <p>Average Performance: <strong>{analytics.average_performance?.toFixed(2) || 'N/A'}</strong></p>
                    <p>Engagement Score: <strong>{analytics.engagement_score?.toFixed(2) || 'N/A'}</strong></p>
                    <p>Total Logs: <strong>{analytics.total_logs || 0}</strong></p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>Emotion-Adaptive Learning System v1.0 | Running on Starlette + SQLite</p>
      </footer>
    </div>
  );
}

export default App;
