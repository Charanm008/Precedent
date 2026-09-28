const { useState, useEffect, useCallback } = React;

const BACKEND_URL = "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [apiStatus, setApiStatus] = useState("testing");
  const [latency, setLatency] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [terminalLogs, setTerminalLogs] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const addLog = (endpoint, status, data, timeMs) => {
    const timeStr = new Date().toLocaleTimeString();
    setTerminalLogs(prev => [
      {
        id: Date.now(),
        time: timeStr,
        endpoint,
        status,
        latency: timeMs,
        data: JSON.stringify(data, null, 2)
      },
      ...prev.slice(0, 19)
    ]);
  };

  const fetchHealth = useCallback(async (endpoint = "/api/v1/health") => {
    setApiStatus("testing");
    const start = performance.now();
    try {
      const response = await fetch(`${BACKEND_URL}${endpoint}`);
      const duration = Math.round(performance.now() - start);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status} ${response.statusText}`);
      }
      const data = await response.json();
      setLatency(duration);
      setHealthData(data);
      setApiStatus("online");
      addLog(endpoint, "200 OK", data, duration);
    } catch (err) {
      const duration = Math.round(performance.now() - start);
      setApiStatus("offline");
      setLatency(null);
      addLog(endpoint, "FAILED", { error: err.message }, duration);
    }
  }, []);

  const fetchStatus = useCallback(async () => {
    await fetchHealth("/api/v1/status");
  }, [fetchHealth]);

  useEffect(() => {
    fetchHealth("/api/v1/health");
    
    if (autoRefresh) {
      const timer = setInterval(() => {
        fetchHealth("/api/v1/health");
      }, 10000);
      return () => clearInterval(timer);
    }
  }, [fetchHealth, autoRefresh]);

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand-header">
          <div className="brand-icon">P</div>
          <div>
            <div className="brand-title">Precedent</div>
            <div className="brand-subtitle">AI Sales Strategist</div>
          </div>
        </div>

        <nav className="nav-menu">
          <div 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="nav-icon">⚡</span>
            <span>Dashboard</span>
            <span className="nav-badge active-badge">Phase 0</span>
          </div>

          <div 
            className={`nav-item ${activeTab === 'deals' ? 'active' : ''}`}
            onClick={() => setActiveTab('deals')}
          >
            <span className="nav-icon">💼</span>
            <span>Deal Strategist</span>
            <span className="nav-badge">Phase 1</span>
          </div>

          <div 
            className={`nav-item ${activeTab === 'memory' ? 'active' : ''}`}
            onClick={() => setActiveTab('memory')}
          >
            <span className="nav-icon">🧠</span>
            <span>Hindsight Memory</span>
            <span className="nav-badge">Phase 2</span>
          </div>

          <div 
            className={`nav-item ${activeTab === 'adk' ? 'active' : ''}`}
            onClick={() => setActiveTab('adk')}
          >
            <span className="nav-icon">🤖</span>
            <span>Google ADK Engine</span>
            <span className="nav-badge">Phase 3</span>
          </div>

          <div 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <span className="nav-icon">⚙️</span>
            <span>Settings</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="hack-badge">
            <span>🏆</span>
            <div>
              <div style={{fontWeight: 700}}>HackWithHyderabad 3.0</div>
              <div style={{fontSize: '10px', opacity: 0.8}}>Persistent AI Sales Engine</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Wrapper */}
      <div className="main-wrapper">
        {/* Top Navbar */}
        <header className="navbar">
          <div>
            <h2 style={{fontSize: '18px', fontWeight: 600}}>Phase 0 — Foundation & Connectivity</h2>
            <p style={{fontSize: '12px', color: 'var(--text-muted)'}}>FastAPI + React Core Telemetry Dashboard</p>
          </div>

          <div className="nav-status-group">
            <div className="status-indicator">
              <span className={`status-dot ${apiStatus}`}></span>
              <span style={{textTransform: 'uppercase', fontWeight: 700, fontSize: '12px'}}>
                {apiStatus === 'online' ? 'BACKEND ONLINE' : apiStatus === 'testing' ? 'CONNECTING...' : 'DISCONNECTED'}
              </span>
            </div>

            {latency !== null && (
              <div className="status-indicator">
                <span className="latency-tag">⚡ {latency} ms</span>
              </div>
            )}

            <button 
              className="btn" 
              onClick={() => fetchHealth("/api/v1/health")}
              title="Refresh connection status"
            >
              🔄 Ping
            </button>
          </div>
        </header>

        {/* Content Body */}
        <main className="content-body">
          {/* Hero Card */}
          <div className="hero-card">
            <div className="phase-pill">
              <span>🚀</span> Phase 0 Foundation Active
            </div>
            <h1 className="hero-title">Core Architecture & API Foundation Ready</h1>
            <p className="hero-desc">
              The Precedent foundation layer is fully initialized. Backend services are running on FastAPI with CORS support, 
              API routing schemas, and real-time connectivity telemetry. Next phases will wire the Hindsight persistent deal memory and Google ADK reasoning agent.
            </p>
          </div>

          {/* Subsystems Metric Grid */}
          <div className="grid-4">
            <div className="card">
              <div className="card-header">
                <div className="card-title-group">
                  <div className="card-icon" style={{color: 'var(--accent-purple)'}}>⚡</div>
                  <div>
                    <div className="card-title">FastAPI Backend</div>
                    <div className="card-subtext">Port 8000 / CORS Active</div>
                  </div>
                </div>
                <span className={`badge-status ${apiStatus === 'online' ? 'online' : 'standby'}`}>
                  {apiStatus === 'online' ? 'Active' : 'Offline'}
                </span>
              </div>
              <div className="card-value">v0.1.0</div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title-group">
                  <div className="card-icon" style={{color: 'var(--accent-cyan)'}}>🧠</div>
                  <div>
                    <div className="card-title">Hindsight Memory</div>
                    <div className="card-subtext">Deal History & Vector Store</div>
                  </div>
                </div>
                <span className="badge-status standby">Standby</span>
              </div>
              <div className="card-value">Phase 1 Ready</div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title-group">
                  <div className="card-icon" style={{color: 'var(--accent-pink)'}}>🤖</div>
                  <div>
                    <div className="card-title">Google ADK Agent</div>
                    <div className="card-subtext">Sales Reasoning Engine</div>
                  </div>
                </div>
                <span className="badge-status standby">Standby</span>
              </div>
              <div className="card-value">Phase 2 Ready</div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title-group">
                  <div className="card-icon" style={{color: 'var(--accent-green)'}}>📊</div>
                  <div>
                    <div className="card-title">Data Storage</div>
                    <div className="card-subtext">Deals, Events, Customers</div>
                  </div>
                </div>
                <span className="badge-status ready">Structured</span>
              </div>
              <div className="card-value">Data Ready</div>
            </div>
          </div>

          {/* Workbench Section */}
          <div className="workbench-section">
            {/* API Interactive Control Panel */}
            <div className="panel">
              <div className="panel-title">
                <span>🔌 API Connectivity Workbench</span>
                <span style={{fontSize: '12px', color: 'var(--text-muted)'}}>{BACKEND_URL}</span>
              </div>

              <p style={{fontSize: '13px', color: 'var(--text-muted)', marginBottom: '16px'}}>
                Test core FastAPI endpoints to confirm cross-origin fetch requests, response serialization, and latency metrics.
              </p>

              <div className="btn-group">
                <button 
                  className="btn btn-primary"
                  onClick={() => fetchHealth("/api/v1/health")}
                >
                  GET /api/v1/health
                </button>

                <button 
                  className="btn btn-cyan"
                  onClick={() => fetchStatus()}
                >
                  GET /api/v1/status
                </button>

                <button 
                  className="btn"
                  onClick={() => fetchHealth("/health")}
                >
                  GET /health
                </button>

                <button 
                  className="btn"
                  onClick={() => fetchHealth("/")}
                >
                  GET /
                </button>
              </div>

              <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px'}}>
                <span style={{fontSize: '13px', fontWeight: 600}}>Telemetry & Response Inspector</span>
                <div style={{display: 'flex', gap: '8px'}}>
                  <button 
                    className="btn" 
                    style={{padding: '4px 10px', fontSize: '11px'}}
                    onClick={() => setTerminalLogs([])}
                  >
                    Clear Console
                  </button>
                </div>
              </div>

              <div className="terminal-box">
                {terminalLogs.length === 0 ? (
                  <span style={{color: 'var(--text-dim)'}}>// Console ready. Click any API endpoint above to inspect response payloads...</span>
                ) : (
                  terminalLogs.map(log => (
                    <div key={log.id} style={{marginBottom: '14px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '10px'}}>
                      <div style={{color: 'var(--accent-cyan)', fontSize: '12px', marginBottom: '4px'}}>
                        [{log.time}] {log.endpoint} — {log.status} ({log.latency} ms)
                      </div>
                      <div>{log.data}</div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Development Roadmap Stepper */}
            <div className="panel">
              <div className="panel-title">
                <span>🛣️ Implementation Roadmap</span>
                <span style={{fontSize: '12px', color: 'var(--accent-purple)'}}>6-Phase Plan</span>
              </div>

              <div className="roadmap-container">
                <div className="roadmap-step active">
                  <div className="step-num">0</div>
                  <div className="step-info">
                    <div className="step-title">Phase 0: Foundation & API Core</div>
                    <div className="step-desc">React UI, FastAPI server, CORS, Pydantic settings, Telemetry.</div>
                  </div>
                  <span className="badge-status online">Active</span>
                </div>

                <div className="roadmap-step">
                  <div className="step-num">1</div>
                  <div className="step-info">
                    <div className="step-title">Phase 1: Hindsight Memory Integration</div>
                    <div className="step-desc">Connect Hindsight SDK for deal history & long-term memory.</div>
                  </div>
                  <span className="badge-status standby">Upcoming</span>
                </div>

                <div className="roadmap-step">
                  <div className="step-num">2</div>
                  <div className="step-info">
                    <div className="step-title">Phase 2: Google ADK Reasoning Agent</div>
                    <div className="step-desc">Implement multi-turn sales decision & action recommendations.</div>
                  </div>
                  <span className="badge-status standby">Upcoming</span>
                </div>

                <div className="roadmap-step">
                  <div className="step-num">3</div>
                  <div className="step-info">
                    <div className="step-title">Phase 3: Sales Deal Intelligence & Data Store</div>
                    <div className="step-desc">Customer, interaction, event, and competitor intelligence.</div>
                  </div>
                  <span className="badge-status standby">Upcoming</span>
                </div>

                <div className="roadmap-step">
                  <div className="step-num">4</div>
                  <div className="step-info">
                    <div className="step-title">Phase 4: Strategy & Recommendation UI</div>
                    <div className="step-desc">Interactive next-best-action dashboard & pitch optimizer.</div>
                  </div>
                  <span className="badge-status standby">Upcoming</span>
                </div>

                <div className="roadmap-step">
                  <div className="step-num">5</div>
                  <div className="step-info">
                    <div className="step-title">Phase 5: Demo & Hackathon Packaging</div>
                    <div className="step-desc">End-to-end deal scenario testing and final presentation.</div>
                  </div>
                  <span className="badge-status standby">Upcoming</span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

// Render App
const rootElement = document.getElementById("root");
const root = ReactDOM.createRoot(rootElement);
root.render(<App />);
