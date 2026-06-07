// import React, { useState } from 'react';

// export default function Train({ status }) {
//   const [cfg, setCfg] = useState({ n_users: 300, n_songs: 1000, n_events: 50000 });
//   const [loading, setLoading] = useState(false);

//   const running = ['generating','training'].includes(status?.status);

//   const start = async () => {
//     setLoading(true);
//     await fetch('/api/train', {
//       method: 'POST',
//       headers: {'Content-Type':'application/json'},
//       body: JSON.stringify(cfg),
//     });
//     setLoading(false);
//   };

//   const reset = () => fetch('/api/reset', { method:'POST' });

//   const progress = status?.progress || 0;

//   return (
//     <div>
//       <div className="page-header">
//         <div className="page-title">Train Model</div>
//         <div className="page-sub">Configure dataset size and launch the full ML pipeline</div>
//       </div>

//       <div className="grid-2" style={{gap:24}}>
//         {/* Config panel */}
//         <div className="card">
//           <div className="card-title">Dataset Configuration</div>

//           <div style={{display:'flex', flexDirection:'column', gap:18}}>
//             <div className="input-group">
//               <label className="input-label">Number of Users</label>
//               <input className="input" type="number" min={50} max={5000}
//                 value={cfg.n_users}
//                 onChange={e => setCfg(p => ({...p, n_users: +e.target.value}))}
//               />
//               <span style={{fontSize:11,color:'var(--muted)'}}>50–5000 recommended</span>
//             </div>

//             <div className="input-group">
//               <label className="input-label">Number of Songs</label>
//               <input className="input" type="number" min={100} max={10000}
//                 value={cfg.n_songs}
//                 onChange={e => setCfg(p => ({...p, n_songs: +e.target.value}))}
//               />
//               <span style={{fontSize:11,color:'var(--muted)'}}>100–10,000 recommended</span>
//             </div>

//             <div className="input-group">
//               <label className="input-label">Play Events</label>
//               <input className="input" type="number" min={5000} max={500000} step={5000}
//                 value={cfg.n_events}
//                 onChange={e => setCfg(p => ({...p, n_events: +e.target.value}))}
//               />
//               <span style={{fontSize:11,color:'var(--muted)'}}>More events → better model, slower training</span>
//             </div>

//             <div style={{display:'flex', gap:10, marginTop:6}}>
//               <button className="btn btn-primary" onClick={start}
//                 disabled={running || loading}>
//                 {running ? <><span className="spinner"/> Training…</> : '▶ Start Pipeline'}
//               </button>
//               <button className="btn btn-danger" onClick={reset} disabled={running}>
//                 ↺ Reset
//               </button>
//             </div>
//           </div>
//         </div>

//         {/* Progress panel */}
//         <div className="card">
//           <div className="card-title">Pipeline Progress</div>

//           <div style={{marginBottom:20}}>
//             <div className="flex-between" style={{marginBottom:8}}>
//               <span style={{fontSize:13,color:'var(--muted)'}}>Progress</span>
//               <span style={{fontFamily:'var(--font-head)',fontWeight:700,color:'var(--accent)'}}>{progress}%</span>
//             </div>
//             <div className="progress-wrap">
//               <div className="progress-bar" style={{width: `${progress}%`}}/>
//             </div>
//           </div>

//           <div className={`log-box ${
//             status?.status === 'ready' ? 'ok' :
//             status?.status === 'error' ? 'error' : 'info'
//           }`} style={{marginBottom:20}}>
//             {status?.message || 'Idle. Configure and start the pipeline.'}
//           </div>

//           {/* Steps checklist */}
//           {[
//             ['Generate Data',   5],
//             ['Load & Clean',    25],
//             ['Feature Eng.',    40],
//             ['Train Baseline',  60],
//             ['Train LightGBM',  80],
//             ['Evaluate',        100],
//           ].map(([label, threshold]) => {
//             const done = progress >= threshold && status?.status !== 'error';
//             const active = running && progress < threshold && progress >= threshold - 20;
//             return (
//               <div key={label} style={{
//                 display:'flex', alignItems:'center', gap:12,
//                 padding:'8px 0', borderBottom:'1px solid var(--border)',
//                 opacity: done || active ? 1 : 0.4,
//               }}>
//                 <span style={{
//                   width:18, height:18, borderRadius:'50%', flexShrink:0,
//                   display:'flex', alignItems:'center', justifyContent:'center',
//                   fontSize:10, fontWeight:700,
//                   background: done ? 'var(--success)' : active ? 'var(--accent3)' : 'var(--bg3)',
//                   color: done||active ? '#000' : 'var(--muted)',
//                   border: done||active ? 'none' : '1px solid var(--border)',
//                   transition:'all 0.3s',
//                 }}>
//                   {done ? '✓' : active ? <span className="spinner"/> : '○'}
//                 </span>
//                 <span style={{fontSize:13, color: done ? 'var(--text)' : active ? 'var(--accent3)' : 'var(--muted)'}}>
//                   {label}
//                 </span>
//               </div>
//             );
//           })}
//         </div>
//       </div>

//       {/* Error display */}
//       {status?.error && (
//         <div className="section-gap">
//           <div className="card" style={{borderColor:'rgba(239,68,68,0.3)'}}>
//             <div className="card-title" style={{color:'var(--error)'}}>Error Details</div>
//             <pre style={{fontSize:12, color:'var(--error)', overflowX:'auto', whiteSpace:'pre-wrap'}}>
//               {status.error}
//             </pre>
//           </div>
//         </div>
//       )}

//       {/* What happens section */}
//       <div className="section-gap">
//         <div className="card">
//           <div className="card-title">What This Pipeline Does</div>
//           <div style={{display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:16, marginTop:4}}>
//             {[
//               ['No Spotify Needed', 'The generator creates realistic synthetic listening history — proper user personas, skip behaviors, genre preferences, and replay labels.'],
//               ['Time-Based Split', 'Data is split chronologically, not randomly. Training happens on past events, testing on future ones — same as real deployment.'],
//               ['Two Models Compared', 'A Logistic Regression baseline is trained first. LightGBM must beat it to justify its complexity. You see both sets of metrics.'],
//             ].map(([title, body]) => (
//               <div key={title} style={{padding:16, background:'var(--bg3)', borderRadius:8, border:'1px solid var(--border)'}}>
//                 <div style={{fontFamily:'var(--font-head)', fontSize:14, fontWeight:700, color:'var(--accent)', marginBottom:8}}>{title}</div>
//                 <div style={{fontSize:12, color:'var(--muted)', lineHeight:1.65}}>{body}</div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }









import React, { useState } from 'react';

export default function Train({ status }) {
  const [cfg, setCfg] = useState({ n_users: 300, n_songs: 1000, n_events: 50000 });
  const [loading, setLoading] = useState(false);
  const running = ['generating','training'].includes(status?.status);
  const progress = status?.progress || 0;

  const start = async () => {
    setLoading(true);
    await fetch('/api/train', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(cfg) });
    setLoading(false);
  };
  const reset = () => fetch('/api/reset', { method:'POST' });

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Train Model</div>
        <div className="page-sub">Configure dataset size and launch the full ML pipeline</div>
      </div>
      <div className="grid-2" style={{gap:24}}>
        <div className="card">
          <div className="card-title">Dataset Configuration</div>
          <div style={{display:'flex',flexDirection:'column',gap:18}}>
            <div className="input-group">
              <label className="input-label">Number of Users</label>
              <input className="input" type="number" min={50} max={5000} value={cfg.n_users} onChange={e=>setCfg(p=>({...p,n_users:+e.target.value}))} />
              <span style={{fontSize:11,color:'var(--muted)'}}>50–5000 recommended</span>
            </div>
            <div className="input-group">
              <label className="input-label">Number of Songs</label>
              <input className="input" type="number" min={100} max={10000} value={cfg.n_songs} onChange={e=>setCfg(p=>({...p,n_songs:+e.target.value}))} />
              <span style={{fontSize:11,color:'var(--muted)'}}>100–10,000 recommended</span>
            </div>
            <div className="input-group">
              <label className="input-label">Play Events</label>
              <input className="input" type="number" min={5000} max={500000} step={5000} value={cfg.n_events} onChange={e=>setCfg(p=>({...p,n_events:+e.target.value}))} />
              <span style={{fontSize:11,color:'var(--muted)'}}>More events = better model, slower training</span>
            </div>
            <div style={{display:'flex',gap:10,marginTop:6}}>
              <button className="btn btn-primary" onClick={start} disabled={running||loading}>
                {running?<><span className="spinner"/> Training…</>:'▶ Start Pipeline'}
              </button>
              <button className="btn btn-danger" onClick={reset} disabled={running}>↺ Reset</button>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-title">Pipeline Progress</div>
          <div style={{marginBottom:20}}>
            <div style={{display:'flex',justifyContent:'space-between',marginBottom:8}}>
              <span style={{fontSize:13,color:'var(--muted)'}}>Progress</span>
              <span style={{fontFamily:'var(--font-head)',fontWeight:700,color:'var(--accent)'}}>{progress}%</span>
            </div>
            <div className="progress-wrap"><div className="progress-bar" style={{width:`${progress}%`}}/></div>
          </div>
          <div className={`log-box ${status?.status==='ready'?'ok':status?.status==='error'?'error':'info'}`} style={{marginBottom:20}}>
            {status?.message||'Idle. Configure and start the pipeline.'}
          </div>
          {[['Generate Data',5],['Load & Clean',25],['Feature Eng.',40],['Train Baseline',60],['Train LightGBM',80],['Evaluate',100]].map(([label,threshold])=>{
            const done=progress>=threshold&&status?.status!=='error';
            const active=running&&progress<threshold&&progress>=threshold-20;
            return(
              <div key={label} style={{display:'flex',alignItems:'center',gap:12,padding:'8px 0',borderBottom:'1px solid var(--border)',opacity:done||active?1:0.4}}>
                <span style={{width:18,height:18,borderRadius:'50%',flexShrink:0,display:'flex',alignItems:'center',justifyContent:'center',fontSize:10,fontWeight:700,background:done?'var(--success)':active?'var(--accent3)':'var(--bg3)',color:done||active?'#000':'var(--muted)',border:done||active?'none':'1px solid var(--border)',transition:'all .3s'}}>
                  {done?'✓':active?<span className="spinner"/>:'○'}
                </span>
                <span style={{fontSize:13,color:done?'var(--text)':active?'var(--accent3)':'var(--muted)'}}>{label}</span>
              </div>
            );
          })}
        </div>
      </div>
      {status?.error&&(
        <div className="section-gap">
          <div className="card" style={{borderColor:'rgba(239,68,68,.3)'}}>
            <div className="card-title" style={{color:'var(--error)'}}>Error Details</div>
            <pre style={{fontSize:12,color:'var(--error)',overflowX:'auto',whiteSpace:'pre-wrap'}}>{status.error}</pre>
          </div>
        </div>
      )}
    </div>
  );
}