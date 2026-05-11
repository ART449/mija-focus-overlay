import React, { useState, useEffect, useRef } from 'react';
import { 
  Terminal, Activity, Database, Search, Cpu, 
  ShieldAlert, Lock, Zap, Server, ChevronRight,
  Trash2, Settings, Sliders
} from 'lucide-react';

// === CONFIGURACIÓN IARTLABS ===
const API_BASE_URL = 'http://localhost:8080';
const WS_BASE_URL = 'ws://localhost:8080';
const BEE_API_URL = 'http://localhost:8000'; 

export default function SovereignDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [serverStatus, setServerStatus] = useState('conectando');
  const [beeStatus, setBeeStatus] = useState('offline');
  const [logs, setLogs] = useState([]);
  const logsEndRef = useRef(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [memKey, setMemKey] = useState('');
  const [memVal, setMemVal] = useState('');
  const [memoryItems, setMemoryItems] = useState([
    { key: 'axiom_config', value: 'v1.0.0-stable' },
    { key: 'vortex_nodes', value: '4 active' }
  ]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const addLog = (msg, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { time: timestamp, msg, type }]);
  };

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/`);
        setServerStatus(res.ok || res.status === 404 ? 'online' : 'offline');
        const beeRes = await fetch(`${BEE_API_URL}/status`);
        setBeeStatus(beeRes.ok ? 'online' : 'offline');
      } catch (err) { 
        setServerStatus('offline'); 
        setBeeStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let ws;
    let reconnectTimer;
    const connectWS = () => {
      ws = new WebSocket(`${WS_BASE_URL}/ws/logs`);
      ws.onopen = () => addLog('✓ Enlace Telemetría Vortex ESTABLECIDO.', 'success');
      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          addLog(data.msg || e.data, data.type || 'info');
        } catch { addLog(e.data, 'info'); }
      };
      ws.onclose = () => { reconnectTimer = setTimeout(connectWS, 5000); };
    };
    connectWS();
    return () => { clearTimeout(reconnectTimer); if (ws) ws.close(); };
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-emerald-500 font-mono flex flex-col md:flex-row overflow-hidden">
      
      {/* Sidebar */}
      <div className="w-full md:w-96 bg-slate-900 border-r border-emerald-900 p-6 flex flex-col z-10 shrink-0">
        <div className="flex items-center gap-3 mb-8">
          <Terminal className="w-10 h-10 text-emerald-500" />
          <h1 className="text-2xl font-bold text-white tracking-widest uppercase">SOVEREIGN</h1>
        </div>

        <nav className="flex flex-col gap-2 flex-grow">
          <NavItem icon={<Activity />} label="Overview" active={activeTab === 'overview'} onClick={() => setActiveTab('overview')} />
          <NavItem icon={<Search />} label="Deep Search" active={activeTab === 'search'} onClick={() => setActiveTab('search')} />
          <NavItem icon={<Database />} label="MemStore" active={activeTab === 'memory'} onClick={() => setActiveTab('memory')} />
          <NavItem icon={<Settings />} label="Opciones" active={activeTab === 'options'} onClick={() => setActiveTab('options')} />
        </nav>

        <div className="mt-auto pt-6 border-t border-emerald-900 space-y-3">
          <StatusIndicator label="Status" status={serverStatus} port="8080" color="text-blue-500" />
          <StatusIndicator label="Bee" status={beeStatus} port="8000" color="text-emerald-500" />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen relative">
        <header className="bg-slate-900/50 border-b border-emerald-900 p-6 flex justify-between items-center backdrop-blur-sm">
          <h2 className="text-xl font-bold text-emerald-400 uppercase tracking-widest">{activeTab.toUpperCase()} PANEL</h2>
          <button onClick={() => fetch(`${BEE_API_URL}/clear`, {method: 'POST'})} className="hover:text-red-500">
            <Trash2 className="w-6 h-6" />
          </button>
        </header>

        <main className="flex-1 overflow-auto p-8 space-y-8">
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-in fade-in">
              <StatCard title="Total Nodos" value="12" desc="Operativos en red" />
              <StatCard title="Memoria Libre" value="1.4 GB" desc="Asignación HEAP" />
              <StatCard title="Operaciones/s" value="482" desc="Tráfico actual" />
              <div className="col-span-3 bg-slate-900 border border-emerald-900 rounded-xl p-6 shadow-inner">
                <h3 className="text-emerald-400 font-bold mb-4 uppercase text-sm tracking-widest">Actividad Vortex</h3>
                <div className="h-40 flex items-end gap-1 overflow-hidden opacity-60">
                  {Array.from({length: 80}).map((_, i) => (
                    <div key={i} className="bg-emerald-600 w-full" style={{height: `${Math.random()*100}%`}}></div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'search' && (
            <div className="max-w-4xl space-y-6 animate-in slide-in-from-right-4">
              <div className="bg-slate-900 border border-emerald-900 p-8 rounded-2xl shadow-2xl">
                <h3 className="text-xl font-bold text-white mb-6 uppercase tracking-widest">Búsqueda Profunda</h3>
                <div className="flex gap-4">
                  <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Consultar Nodo..." className="flex-1 bg-slate-950 border border-emerald-800 text-emerald-100 px-6 py-4 rounded-xl text-xl focus:outline-none focus:border-emerald-500" />
                  <button className="bg-emerald-800 hover:bg-emerald-600 text-white px-8 py-4 rounded-xl font-bold transition-all"><Search /></button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'memory' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in slide-in-from-left-4">
              <form onSubmit={(e) => {
                e.preventDefault();
                if (!memKey || !memVal) return;
                addLog(`Inyectando [${memKey}]`, 'info');
                setTimeout(() => {
                  setMemoryItems(prev => [{ key: memKey, value: memVal }, ...prev]);
                  setMemKey(''); setMemVal('');
                  addLog('✓ Persistencia exitosa.', 'success');
                }, 300)
              }} className="bg-slate-900 border border-emerald-900 p-8 rounded-2xl space-y-4">
                <h3 className="text-emerald-400 font-bold uppercase tracking-widest">MemStore Ingest</h3>
                <input type="text" value={memKey} onChange={(e) => setMemKey(e.target.value)} placeholder="Key" className="w-full bg-slate-950 border border-emerald-800 text-emerald-100 px-6 py-4 rounded-xl text-xl focus:outline-none" />
                <textarea value={memVal} onChange={(e) => setMemVal(e.target.value)} placeholder="Value" className="w-full h-40 bg-slate-950 border border-emerald-800 text-emerald-100 px-6 py-4 rounded-xl text-xl resize-none focus:outline-none"></textarea>
                <button type="submit" className="w-full bg-emerald-800 hover:bg-emerald-600 text-white py-4 rounded-xl font-bold text-xl uppercase transition-all">Sincronizar</button>
              </form>
              <div className="bg-slate-950 border border-emerald-950 rounded-2xl p-4 h-[500px] overflow-y-auto space-y-4">
                {memoryItems.map((item, i) => (
                  <div key={i} className="p-4 bg-slate-900 border-l-4 border-emerald-500 rounded-r-xl shadow-lg">
                    <div className="text-emerald-100 font-bold">{item.key}</div>
                    <div className="text-slate-500 text-sm mt-1 truncate">{item.value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'options' && (
            <div className="max-w-3xl space-y-6 animate-in zoom-in-95">
                <div className="bg-slate-900 border border-emerald-900 p-8 rounded-2xl shadow-2xl">
                    <h3 className="text-xl font-bold text-white mb-8 flex items-center gap-3 uppercase italic"><Sliders className="text-emerald-500"/> Configuración</h3>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center p-4 bg-slate-950 rounded-xl border border-emerald-900/20">
                            <span>Escalado 4K Inteligente</span>
                            <div className="w-12 h-6 bg-emerald-600 rounded-full flex items-center px-1"><div className="w-4 h-4 bg-white rounded-full ml-auto"></div></div>
                        </div>
                    </div>
                </div>
            </div>
          )}
        </main>

        <div className="h-64 bg-slate-950 border-t-2 border-emerald-900 p-6 font-mono text-lg overflow-y-auto z-10 shadow-2xl">
          <div className="text-emerald-800 mb-4 font-bold border-b border-emerald-900/30 pb-2 uppercase tracking-[0.3em]">=== TERMINAL SOVEREIGN ===</div>
          <div className="space-y-1">
            {logs.map((log, idx) => (
              <div key={idx} className="flex gap-4">
                <span className="text-slate-700 shrink-0">[{log.time}]</span>
                <span className={log.type === 'error' ? 'text-red-400' : log.type === 'success' ? 'text-emerald-400' : 'text-emerald-200'}>
                  {log.msg}
                </span>
              </div>
            ))}
          </div>
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button onClick={onClick} className={`flex items-center gap-4 w-full p-4 rounded-xl transition-all text-left ${active ? 'bg-emerald-900/30 text-emerald-400 border-l-4 border-emerald-400 shadow-lg' : 'text-slate-500 hover:bg-slate-800'}`}>
      {React.cloneElement(icon, { className: 'w-6 h-6' })}
      <span className="font-bold text-lg uppercase tracking-wider">{label}</span>
    </button>
  );
}

function StatusIndicator({ label, status, port, color }) {
  const isOnline = status === 'online';
  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-slate-950 rounded-lg border border-emerald-900/30 shadow-inner">
        <div className={`w-3 h-3 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
        <div className="flex flex-col">
            <span className="text-[10px] text-slate-700 font-bold uppercase tracking-tighter">{label}</span>
            <span className={`text-base font-bold ${isOnline ? color : 'text-red-500'}`}>{status.toUpperCase()}</span>
        </div>
        <span className="text-xs text-slate-800 ml-auto font-bold tracking-widest">:{port}</span>
    </div>
  );
}

function StatCard({ title, value, desc }) {
  return (
    <div className="bg-slate-900 border border-emerald-900 rounded-2xl p-6 shadow-xl flex flex-col justify-center min-h-[160px] hover:border-emerald-500 transition-all">
      <h4 className="text-slate-500 text-xs font-bold mb-1 uppercase tracking-widest">{title}</h4>
      <div className="text-4xl font-bold tracking-tighter text-emerald-400 mb-1">{value}</div>
      <div className="text-sm text-slate-400 font-medium">{desc}</div>
    </div>
  );
}
