// import React, { useState, useEffect } from 'react';

// function AudioBar({ label, value }) {
//   return (
//     <div className="audio-bar-row">
//       <span className="audio-bar-label">{label}</span>
//       <div className="audio-bar-track">
//         <div className="audio-bar-fill" style={{width: `${(value||0)*100}%`}}/>
//       </div>
//       <span style={{width:34, textAlign:'right', fontSize:10}}>{value ? (value*100).toFixed(0)+'%' : '—'}</span>
//     </div>
//   );
// }

// function RecCard({ rec, rank }) {
//   const prob = rec.replay_probability;
//   const pct = (prob * 100).toFixed(1);
//   const color = prob > 0.7 ? 'var(--success)' : prob > 0.4 ? 'var(--accent)' : 'var(--muted)';

//   return (
//     <div className="rec-card">
//       <div className="rec-rank">#{rank}</div>
//       <div className="rec-song-id">{rec.song_id}</div>
//       <div className="rec-prob" style={{color}}>{pct}%</div>
//       <div className="rec-prob-label">replay probability</div>

//       <div className="audio-bars">
//         <AudioBar label="energy"   value={rec.song_energy} />
//         <AudioBar label="valence"  value={rec.song_valence} />
//         <AudioBar label="dance"    value={rec.song_danceability} />
//       </div>

//       {rec.song_tempo && (
//         <div style={{marginTop:10, fontSize:11, color:'var(--muted)'}}>
//           ♩ {Math.round(rec.song_tempo)} BPM
//         </div>
//       )}
//     </div>
//   );
// }

// export default function Recommend({ status }) {
//   const [users, setUsers] = useState([]);
//   const [selectedUser, setSelectedUser] = useState('');
//   const [recs, setRecs] = useState(null);
//   const [topK, setTopK] = useState(10);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);

//   const ready = status?.status === 'ready';

//   useEffect(() => {
//     if (!ready) return;
//     fetch('/api/users').then(r=>r.json()).then(d => {
//       setUsers(d.users || []);
//       if (d.users?.length) setSelectedUser(d.users[0]);
//     });
//   }, [ready]);

//   const getRecommendations = async () => {
//     if (!selectedUser) return;
//     setLoading(true); setError(null);
//     try {
//       const r = await fetch(`/api/recommend/${selectedUser}?top_k=${topK}`);
//       const d = await r.json();
//       if (!r.ok) throw new Error(d.detail);
//       setRecs(d);
//     } catch(e) { setError(e.message); }
//     setLoading(false);
//   };

//   if (!ready) return (
//     <div>
//       <div className="page-header">
//         <div className="page-title">Recommendations</div>
//         <div className="page-sub">Train a model first to generate recommendations</div>
//       </div>
//       <div className="empty-state">
//         <div className="icon">▶</div>
//         <div>Train a model on the <strong>Train Model</strong> page first.</div>
//       </div>
//     </div>
//   );

//   return (
//     <div>
//       <div className="page-header">
//         <div className="page-title">Recommendations</div>
//         <div className="page-sub">Select a user and get their top-K predicted replay songs</div>
//       </div>

//       <div className="card" style={{marginBottom:28}}>
//         <div style={{display:'flex', gap:16, alignItems:'flex-end', flexWrap:'wrap'}}>
//           <div className="input-group" style={{flex:1, minWidth:180}}>
//             <label className="input-label">Select User</label>
//             <select className="input" value={selectedUser}
//               onChange={e => { setSelectedUser(e.target.value); setRecs(null); }}>
//               {users.map(u => <option key={u} value={u}>{u}</option>)}
//             </select>
//           </div>

//           <div className="input-group" style={{width:120}}>
//             <label className="input-label">Top K</label>
//             <select className="input" value={topK}
//               onChange={e => setTopK(+e.target.value)}>
//               {[5,10,15,20].map(k => <option key={k}>{k}</option>)}
//             </select>
//           </div>

//           <button className="btn btn-primary" onClick={getRecommendations} disabled={loading}>
//             {loading ? <><span className="spinner"/> Getting recs…</> : '▶ Get Recommendations'}
//           </button>
//         </div>
//       </div>

//       {error && <div className="log-box error" style={{marginBottom:16}}>{error}</div>}

//       {recs && (
//         <>
//           <div className="flex-between" style={{marginBottom:16}}>
//             <div>
//               <span style={{fontFamily:'var(--font-head)', fontWeight:700, fontSize:16}}>
//                 Top {recs.recommendations.length} songs for
//               </span>
//               <span className="chip chip-cyan" style={{marginLeft:10}}>{recs.user_id}</span>
//             </div>
//             <span style={{fontSize:12, color:'var(--muted)'}}>sorted by replay probability ↓</span>
//           </div>

//           <div className="rec-grid">
//             {recs.recommendations.map((r, i) => (
//               <RecCard key={r.song_id} rec={r} rank={i+1} />
//             ))}
//           </div>

//           <div className="section-gap">
//             <div className="card">
//               <div className="card-title">How recommendations are generated</div>
//               <div style={{fontSize:13, color:'var(--muted)', lineHeight:1.7}}>
//                 The trained LightGBM model scores every song in the catalog for this user.
//                 For each (user, song) pair it predicts the probability of the user replaying
//                 that song within 30 days. The percentage shown is that probability.
//                 Songs are ranked by this score and the top-K returned.
//                 Audio bars show the song's Spotify-style audio features.
//               </div>
//             </div>
//           </div>
//         </>
//       )}
//     </div>
//   );
// }








import React, { useState, useEffect } from 'react';

function AudioBar({ label, value }) {
  return (
    <div className="audio-bar-row">
      <span className="audio-bar-label">{label}</span>
      <div className="audio-bar-track"><div className="audio-bar-fill" style={{width:`${(value||0)*100}%`}}/></div>
      <span style={{width:34,textAlign:'right',fontSize:10}}>{value?(value*100).toFixed(0)+'%':'—'}</span>
    </div>
  );
}

function RecCard({ rec, rank }) {
  const prob = rec.replay_probability;
  const color = prob>0.7?'var(--success)':prob>0.4?'var(--accent)':'var(--muted)';
  return (
    <div className="rec-card">
      <div className="rec-rank">#{rank}</div>
      <div className="rec-song-id">{rec.song_id}</div>
      <div className="rec-prob" style={{color}}>{(prob*100).toFixed(1)}%</div>
      <div className="rec-prob-label">replay probability</div>
      <div className="audio-bars">
        <AudioBar label="energy"  value={rec.song_energy} />
        <AudioBar label="valence" value={rec.song_valence} />
        <AudioBar label="dance"   value={rec.song_danceability} />
      </div>
      {rec.song_tempo&&<div style={{marginTop:10,fontSize:11,color:'var(--muted)'}}>♩ {Math.round(rec.song_tempo)} BPM</div>}
    </div>
  );
}

export default function Recommend({ status }) {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [recs, setRecs] = useState(null);
  const [topK, setTopK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const ready = status?.status === 'ready';

  useEffect(() => {
    if (!ready) return;
    fetch('/api/users').then(r=>r.json()).then(d=>{setUsers(d.users||[]);if(d.users?.length)setSelectedUser(d.users[0]);});
  }, [ready]);

  const getRecommendations = async () => {
    setLoading(true); setError(null);
    try {
      const r = await fetch(`/api/recommend/${selectedUser}?top_k=${topK}`);
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail);
      setRecs(d);
    } catch(e) { setError(e.message); }
    setLoading(false);
  };

  if (!ready) return (
    <div><div className="page-header"><div className="page-title">Recommendations</div></div>
    <div className="empty-state"><div className="icon">▶</div><div>Train a model on the Train Model page first.</div></div></div>
  );

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Recommendations</div>
        <div className="page-sub">Select a user and get their top-K predicted replay songs</div>
      </div>
      <div className="card" style={{marginBottom:28}}>
        <div style={{display:'flex',gap:16,alignItems:'flex-end',flexWrap:'wrap'}}>
          <div className="input-group" style={{flex:1,minWidth:180}}>
            <label className="input-label">Select User</label>
            <select className="input" value={selectedUser} onChange={e=>{setSelectedUser(e.target.value);setRecs(null);}}>
              {users.map(u=><option key={u} value={u}>{u}</option>)}
            </select>
          </div>
          <div className="input-group" style={{width:120}}>
            <label className="input-label">Top K</label>
            <select className="input" value={topK} onChange={e=>setTopK(+e.target.value)}>
              {[5,10,15,20].map(k=><option key={k}>{k}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={getRecommendations} disabled={loading}>
            {loading?<><span className="spinner"/> Getting recs…</>:'▶ Get Recommendations'}
          </button>
        </div>
      </div>
      {error&&<div className="log-box error" style={{marginBottom:16}}>{error}</div>}
      {recs&&(
        <>
          <div className="flex-between" style={{marginBottom:16}}>
            <div><span style={{fontFamily:'var(--font-head)',fontWeight:700,fontSize:16}}>Top {recs.recommendations.length} songs for </span><span className="chip chip-cyan">{recs.user_id}</span></div>
            <span style={{fontSize:12,color:'var(--muted)'}}>sorted by replay probability ↓</span>
          </div>
          <div className="rec-grid">{recs.recommendations.map((r,i)=><RecCard key={r.song_id} rec={r} rank={i+1}/>)}</div>
        </>
      )}
    </div>
  );
}