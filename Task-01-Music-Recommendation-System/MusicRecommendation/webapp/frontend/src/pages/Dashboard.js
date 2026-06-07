// import React from 'react';

// export default function Dashboard({ status }) {
//   const s = status;
//   const ready = s?.status === 'ready';

//   return (
//     <div>
//       <div className="page-header">
//         <div className="page-title">Dashboard</div>
//         <div className="page-sub">Overview of your music recommendation ML pipeline</div>
//       </div>

//       {/* Status banner */}
//       <div className={`log-box ${ready ? 'ok' : s?.status === 'error' ? 'error' : 'info'}`}>
//         {s?.message || 'Loading…'}
//       </div>

//       {/* Dataset stats */}
//       <div className="section-gap">
//         <div className="grid-4">
//           <div className="stat-tile">
//             <div className="stat-label">Users</div>
//             <div className={`stat-value ${ready ? 'accent' : ''}`}>
//               {s?.n_users ? s.n_users.toLocaleString() : '—'}
//             </div>
//             <div className="stat-sub">unique listeners</div>
//           </div>
//           <div className="stat-tile">
//             <div className="stat-label">Songs</div>
//             <div className={`stat-value ${ready ? 'accent' : ''}`}>
//               {s?.n_songs ? s.n_songs.toLocaleString() : '—'}
//             </div>
//             <div className="stat-sub">in catalog</div>
//           </div>
//           <div className="stat-tile">
//             <div className="stat-label">Events</div>
//             <div className={`stat-value ${ready ? 'accent' : ''}`}>
//               {s?.n_events ? (s.n_events / 1000).toFixed(0) + 'k' : '—'}
//             </div>
//             <div className="stat-sub">play events</div>
//           </div>
//           <div className="stat-tile">
//             <div className="stat-label">Replay rate</div>
//             <div className={`stat-value ${ready ? 'success' : ''}`}>
//               {s?.replay_rate ? (s.replay_rate * 100).toFixed(1) + '%' : '—'}
//             </div>
//             <div className="stat-sub">label = 1 rate</div>
//           </div>
//         </div>
//       </div>

//       {/* Model metrics summary */}
//       {ready && s?.metrics && (
//         <div className="section-gap grid-2">
//           <div className="card">
//             <div className="card-title">Primary Metrics — LightGBM</div>
//             {[
//               ['AUC-ROC',  s.metrics.auc_roc,    0.75, 0.65],
//               ['NDCG@10',  s.metrics.ndcg_at_10, 0.70, 0.55],
//               ['Log loss', s.metrics.log_loss,   null, null, true],
//               ['F1 Score', s.metrics.f1,         0.65, 0.50],
//             ].map(([name, val, good, ok, lower]) => {
//               const cls = lower
//                 ? (val < 0.40 ? 'good' : val < 0.55 ? 'ok' : 'bad')
//                 : (val >= (good||0) ? 'good' : val >= (ok||0) ? 'ok' : 'bad');
//               return (
//                 <div className="metric-row" key={name}>
//                   <span className="metric-name">{name}</span>
//                   <span className={`metric-val ${cls}`}>{val?.toFixed(4)}</span>
//                 </div>
//               );
//             })}
//           </div>

//           <div className="card">
//             <div className="card-title">How to Read These Numbers</div>
//             <div style={{fontSize:13,color:'var(--muted)',lineHeight:1.7}}>
//               <p><span style={{color:'var(--accent)'}}>AUC-ROC</span> — &gt;0.75 is good. Measures if replayed songs rank above non-replayed ones.</p>
//               <br/>
//               <p><span style={{color:'var(--accent)'}}>NDCG@10</span> — &gt;0.65 is good. Did the best songs land at the top of the list?</p>
//               <br/>
//               <p><span style={{color:'var(--accent)'}}>Log loss</span> — lower is better. Are the predicted probabilities well-calibrated?</p>
//               <br/>
//               <p><span style={{color:'var(--accent)'}}>Why not accuracy?</span> — Most songs are NOT replayed (imbalanced). A model predicting all-0 would have high accuracy but be useless.</p>
//             </div>
//           </div>
//         </div>
//       )}

//       {/* Pipeline steps */}
//       <div className="section-gap">
//         <div className="card">
//           <div className="card-title">Pipeline Overview</div>
//           <div style={{display:'flex', gap:0, alignItems:'center', flexWrap:'wrap'}}>
//             {[
//               ['Generate Data', 'Synthetic or real Spotify history'],
//               ['Time Split',    'Train on past, test on future'],
//               ['Feature Eng.',  '24 behavioral + audio signals'],
//               ['Train LGBM',    'Binary classifier with early stop'],
//               ['Evaluate',      'AUC · NDCG · Precision@K'],
//               ['Recommend',     'Score all songs per user'],
//             ].map((step, i) => (
//               <React.Fragment key={i}>
//                 <div style={{
//                   background:'var(--bg3)', border:'1px solid var(--border)',
//                   borderRadius:8, padding:'12px 16px', minWidth:130
//                 }}>
//                   <div style={{fontSize:11, color:'var(--accent)', letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:4}}>Step {i+1}</div>
//                   <div style={{fontFamily:'var(--font-head)', fontSize:14, fontWeight:700, color:'var(--text)', marginBottom:2}}>{step[0]}</div>
//                   <div style={{fontSize:11, color:'var(--muted)'}}>{step[1]}</div>
//                 </div>
//                 {i < 5 && <div style={{color:'var(--border)', fontSize:20, padding:'0 8px'}}>→</div>}
//               </React.Fragment>
//             ))}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }








import React from 'react';

export default function Dashboard({ status }) {
  const s = status;
  const ready = s?.status === 'ready';
  return (
    <div>
      <div className="page-header">
        <div className="page-title">Dashboard</div>
        <div className="page-sub">Overview of your music recommendation ML pipeline</div>
      </div>
      <div className={`log-box ${ready ? 'ok' : s?.status === 'error' ? 'error' : 'info'}`}>
        {s?.message || 'Loading…'}
      </div>
      <div className="section-gap">
        <div className="grid-4">
          <div className="stat-tile"><div className="stat-label">Users</div><div className={`stat-value ${ready?'accent':''}`}>{s?.n_users?s.n_users.toLocaleString():'—'}</div><div className="stat-sub">unique listeners</div></div>
          <div className="stat-tile"><div className="stat-label">Songs</div><div className={`stat-value ${ready?'accent':''}`}>{s?.n_songs?s.n_songs.toLocaleString():'—'}</div><div className="stat-sub">in catalog</div></div>
          <div className="stat-tile"><div className="stat-label">Events</div><div className={`stat-value ${ready?'accent':''}`}>{s?.n_events?(s.n_events/1000).toFixed(0)+'k':'—'}</div><div className="stat-sub">play events</div></div>
          <div className="stat-tile"><div className="stat-label">Replay rate</div><div className={`stat-value ${ready?'success':''}`}>{s?.replay_rate?(s.replay_rate*100).toFixed(1)+'%':'—'}</div><div className="stat-sub">label = 1 rate</div></div>
        </div>
      </div>
      {ready && s?.metrics && (
        <div className="section-gap grid-2">
          <div className="card">
            <div className="card-title">Primary Metrics — LightGBM</div>
            {[['AUC-ROC',s.metrics.auc_roc,0.75,0.65],['NDCG@10',s.metrics.ndcg_at_10,0.70,0.55],['Log loss',s.metrics.log_loss,null,null,true],['F1 Score',s.metrics.f1,0.65,0.50]].map(([name,val,good,ok,lower])=>{
              const cls=lower?(val<0.40?'good':val<0.55?'ok':'bad'):(val>=(good||0)?'good':val>=(ok||0)?'ok':'bad');
              return(<div className="metric-row" key={name}><span className="metric-name">{name}</span><span className={`metric-val ${cls}`}>{val?.toFixed(4)}</span></div>);
            })}
          </div>
          <div className="card">
            <div className="card-title">How to Read These Numbers</div>
            <div style={{fontSize:13,color:'var(--muted)',lineHeight:1.7}}>
              <p><span style={{color:'var(--accent)'}}>AUC-ROC</span> — &gt;0.75 is good. Ranks replay songs above non-replay ones.</p><br/>
              <p><span style={{color:'var(--accent)'}}>NDCG@10</span> — &gt;0.65 is good. Best songs land at the top of the list.</p><br/>
              <p><span style={{color:'var(--accent)'}}>Log loss</span> — lower is better. Measures probability calibration.</p><br/>
              <p><span style={{color:'var(--accent)'}}>Why not accuracy?</span> — Data is imbalanced. All-zero model scores high but is useless.</p>
            </div>
          </div>
        </div>
      )}
      <div className="section-gap">
        <div className="card">
          <div className="card-title">Pipeline Overview</div>
          <div style={{display:'flex',gap:8,alignItems:'center',flexWrap:'wrap'}}>
            {[['Generate Data','Synthetic or Spotify'],['Time Split','Train past, test future'],['Feature Eng.','24 behavioral signals'],['Train LGBM','Binary classifier'],['Evaluate','AUC·NDCG·Precision@K'],['Recommend','Score songs per user']].map((step,i)=>(
              <React.Fragment key={i}>
                <div style={{background:'var(--bg3)',border:'1px solid var(--border)',borderRadius:8,padding:'12px 16px',minWidth:120}}>
                  <div style={{fontSize:10,color:'var(--accent)',letterSpacing:'.1em',textTransform:'uppercase',marginBottom:4}}>Step {i+1}</div>
                  <div style={{fontFamily:'var(--font-head)',fontSize:13,fontWeight:700,marginBottom:2}}>{step[0]}</div>
                  <div style={{fontSize:11,color:'var(--muted)'}}>{step[1]}</div>
                </div>
                {i<5&&<div style={{color:'var(--border)',fontSize:18}}>→</div>}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}