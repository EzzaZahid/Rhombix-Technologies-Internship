// import React, { useState, useEffect } from 'react';
// import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

// const COLORS = [
//   '#00e5ff','#00cfeb','#00bad7','#00a4c3','#00aeff',
//   '#7c3aed','#8b5cf6','#a78bfa','#c4b5fd','#ddd6fe',
//   '#10b981','#34d399','#f59e0b','#fbbf24','#ef4444',
// ];

// const FEATURE_EXPLANATIONS = {
//   user_replay_rate:        'Fraction of songs this user has replayed historically. The single strongest predictor.',
//   song_global_replay_rate: 'Fraction of all users who replay this song. High = globally popular/sticky.',
//   times_played_before:     'How many times this user has played this exact song before this event.',
//   user_avg_completion:     "Average fraction of songs this user listens to. Low completion → casual or picky listener.",
//   song_avg_completion:     'Average fraction users listen to of this song. Low = boring or polarizing.',
//   user_skip_rate:          'Fraction of plays this user skips (< 30% completion). High skip rate = hard to please.',
//   song_energy:             'Spotify audio feature: perceptual intensity and activity. Workout songs score high.',
//   song_valence:            'Spotify audio feature: musical positivity. High = happy/upbeat, low = sad/dark.',
//   song_danceability:       'Spotify audio feature: how suitable the song is for dancing.',
//   user_total_plays:        'Total play events from this user. Power users generate more reliable signals.',
//   song_total_plays:        'Total plays of this song across all users. Popularity proxy.',
//   user_genre_diversity:    'Entropy of genres this user listens to. Low = focused taste, high = eclectic.',
//   same_artist_plays_before:'How many songs by the same artist this user has played. Artist loyalty signal.',
//   hour_of_day:             'Hour when this play happened. Users tend to replay certain song types at certain hours.',
//   day_of_week:             'Day of the week. Weekend vs weekday listening patterns differ significantly.',
// };

// export default function Features({ status }) {
//   const [features, setFeatures] = useState(null);
//   const [selected, setSelected] = useState(null);

//   useEffect(() => {
//     if (status?.status !== 'ready') return;
//     fetch('/api/feature-importance').then(r=>r.json())
//       .then(d => { setFeatures(d.features); setSelected(d.features[0]); })
//       .catch(()=>{});
//   }, [status?.status]);

//   if (status?.status !== 'ready') return (
//     <div>
//       <div className="page-header"><div className="page-title">Feature Importance</div></div>
//       <div className="empty-state"><div className="icon">◫</div><div>Train a model first.</div></div>
//     </div>
//   );

//   if (!features) return <div className="empty-state"><span className="spinner"/></div>;

//   const maxImp = Math.max(...features.map(f => f.importance));
//   const tooltipStyle = {background:'#0e1320', border:'1px solid #1e2638', fontSize:12, color:'#e8eaf0'};

//   return (
//     <div>
//       <div className="page-header">
//         <div className="page-title">Feature Importance</div>
//         <div className="page-sub">Which signals matter most to the LightGBM model?</div>
//       </div>

//       <div className="grid-2" style={{gap:24, alignItems:'start'}}>
//         {/* Bar chart */}
//         <div className="card">
//           <div className="card-title">Top Features by Importance Score</div>
//           <ResponsiveContainer width="100%" height={420}>
//             <BarChart
//               data={features}
//               layout="vertical"
//               margin={{left:10, right:20, top:0, bottom:0}}
//               onClick={e => e?.activePayload && setSelected(e.activePayload[0].payload)}
//             >
//               <XAxis type="number" tick={{fill:'#6b7694',fontSize:10}} axisLine={false} tickLine={false}/>
//               <YAxis type="category" dataKey="feature" tick={{fill:'#6b7694',fontSize:11}} width={160} axisLine={false} tickLine={false}/>
//               <Tooltip
//                 contentStyle={tooltipStyle}
//                 formatter={v => [v.toLocaleString(), 'Importance']}
//                 cursor={{fill:'rgba(0,229,255,0.05)'}}
//               />
//               <Bar dataKey="importance" radius={[0,4,4,0]}>
//                 {features.map((f, i) => (
//                   <Cell
//                     key={f.feature}
//                     fill={selected?.feature === f.feature ? '#00e5ff' : COLORS[i % COLORS.length]}
//                     opacity={selected?.feature === f.feature ? 1 : 0.75}
//                   />
//                 ))}
//               </Bar>
//             </BarChart>
//           </ResponsiveContainer>
//           <div style={{fontSize:11, color:'var(--muted)', marginTop:8}}>Click a bar to learn what that feature means</div>
//         </div>

//         {/* Detail panel */}
//         <div style={{display:'flex', flexDirection:'column', gap:16}}>
//           {/* Selected feature explainer */}
//           {selected && (
//             <div className="card" style={{borderColor:'rgba(0,229,255,0.25)'}}>
//               <div className="card-title" style={{color:'var(--accent)'}}>{selected.feature}</div>
//               <div style={{
//                 fontFamily:'var(--font-head)', fontSize:26, fontWeight:800,
//                 color:'var(--text)', marginBottom:4
//               }}>
//                 {selected.importance.toLocaleString()}
//               </div>
//               <div style={{fontSize:12, color:'var(--muted)', marginBottom:14}}>importance score</div>
//               <div className="progress-wrap" style={{marginBottom:16}}>
//                 <div className="progress-bar" style={{width:`${(selected.importance/maxImp)*100}%`}}/>
//               </div>
//               <div style={{fontSize:13, color:'var(--muted)', lineHeight:1.7}}>
//                 {FEATURE_EXPLANATIONS[selected.feature] || 'A behavioral or audio feature used to predict replay likelihood.'}
//               </div>
//             </div>
//           )}

//           {/* Feature categories */}
//           <div className="card">
//             <div className="card-title">Feature Categories</div>
//             {[
//               ['User behavioral',   'user_replay_rate, user_skip_rate, user_avg_completion…',    'chip-cyan'],
//               ['Song-level',        'song_global_replay_rate, song_energy, song_valence…',        'chip-purple'],
//               ['Interaction',       'times_played_before, same_artist_plays, days_since_first…', 'chip-green'],
//               ['Temporal',          'hour_of_day, day_of_week, is_weekend, month',               'chip-cyan'],
//             ].map(([cat, examples, chipClass]) => (
//               <div key={cat} style={{padding:'12px 0', borderBottom:'1px solid var(--border)'}}>
//                 <div style={{display:'flex', alignItems:'center', gap:8, marginBottom:4}}>
//                   <span className={`chip ${chipClass}`}>{cat}</span>
//                 </div>
//                 <div style={{fontSize:12, color:'var(--muted)'}}>{examples}</div>
//               </div>
//             ))}
//           </div>

//           <div className="card">
//             <div className="card-title">Why Feature Importance Matters</div>
//             <div style={{fontSize:13, color:'var(--muted)', lineHeight:1.7}}>
//               High-importance features are the ones the model relies on most.
//               If <span style={{color:'var(--accent)'}}>user_replay_rate</span> dominates,
//               your model learned that past behavior is the strongest predictor —
//               which matches real-world intuition.
//               If only audio features rank high, you may have a data leakage issue
//               to investigate.
//             </div>
//           </div>
//         </div>
//       </div>

//       {/* Full table */}
//       <div className="section-gap card">
//         <div className="card-title">All Features Ranked</div>
//         <div className="table-wrap">
//           <table>
//             <thead>
//               <tr><th>#</th><th>Feature</th><th>Importance</th><th>Relative</th><th>Explanation</th></tr>
//             </thead>
//             <tbody>
//               {features.map((f, i) => (
//                 <tr key={f.feature} onClick={() => setSelected(f)} style={{cursor:'pointer'}}>
//                   <td style={{color:'var(--muted)', width:32}}>{i+1}</td>
//                   <td className="td-mono">{f.feature}</td>
//                   <td style={{fontFamily:'var(--font-head)', fontWeight:700}}>{f.importance.toLocaleString()}</td>
//                   <td style={{width:180}}>
//                     <div className="td-bar-wrap">
//                       <div className="td-bar">
//                         <div className="td-bar-fill" style={{width:`${(f.importance/maxImp)*100}%`}}/>
//                       </div>
//                       <span style={{fontSize:11,color:'var(--muted)',width:38}}>
//                         {((f.importance/maxImp)*100).toFixed(0)}%
//                       </span>
//                     </div>
//                   </td>
//                   <td style={{fontSize:11, color:'var(--muted)', maxWidth:260}}>
//                     {(FEATURE_EXPLANATIONS[f.feature]||'').slice(0, 70)}…
//                   </td>
//                 </tr>
//               ))}
//             </tbody>
//           </table>
//         </div>
//       </div>
//     </div>
//   );
// }









import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const COLORS=['#00e5ff','#00cfeb','#7c3aed','#8b5cf6','#a78bfa','#10b981','#34d399','#f59e0b','#fbbf24','#ef4444','#00aeff','#0090d4','#005fa3','#003d75','#001f4a'];
const EXPLAIN={
  user_replay_rate:'Fraction of songs this user has replayed historically. The single strongest predictor.',
  song_global_replay_rate:'Fraction of all users who replay this song. High = globally sticky.',
  times_played_before:'How many times this user has played this exact song before.',
  user_avg_completion:'Average fraction of songs this user listens to. Low = picky listener.',
  song_avg_completion:'Average fraction users listen to of this song. Low = polarizing.',
  user_skip_rate:'Fraction of plays this user skips. High = hard to please.',
  song_energy:'Perceptual intensity. Workout songs score high.',
  song_valence:'Musical positivity. High = happy, low = sad/dark.',
  song_danceability:'How suitable for dancing.',
  user_total_plays:'Total play events from this user. Power users = more reliable signals.',
  song_total_plays:'Total plays across all users. Popularity proxy.',
  user_genre_diversity:'Entropy of genres listened to. Low = focused, high = eclectic.',
  same_artist_plays_before:'Songs by same artist this user played. Artist loyalty signal.',
  hour_of_day:'Hour of play. Users replay certain song types at certain hours.',
  day_of_week:'Day of week. Weekend vs weekday patterns differ.',
};
const TS={background:'#0e1320',border:'1px solid #1e2638',fontSize:12,color:'#e8eaf0'};

export default function Features({ status }) {
  const [features, setFeatures] = useState(null);
  const [selected, setSelected] = useState(null);
  useEffect(()=>{if(status?.status!=='ready')return;fetch('/api/feature-importance').then(r=>r.json()).then(d=>{setFeatures(d.features);setSelected(d.features[0]);}).catch(()=>{});},[status?.status]);

  if (status?.status!=='ready') return <div><div className="page-header"><div className="page-title">Feature Importance</div></div><div className="empty-state"><div className="icon">◫</div><div>Train a model first.</div></div></div>;
  if (!features) return <div className="empty-state"><span className="spinner"/></div>;

  const maxImp = Math.max(...features.map(f=>f.importance));

  return (
    <div>
      <div className="page-header"><div className="page-title">Feature Importance</div><div className="page-sub">Which signals matter most to the LightGBM model?</div></div>
      <div className="grid-2" style={{gap:24,alignItems:'start'}}>
        <div className="card">
          <div className="card-title">Top Features — click any bar to learn more</div>
          <ResponsiveContainer width="100%" height={420}>
            <BarChart data={features} layout="vertical" margin={{left:10,right:20}} onClick={e=>e?.activePayload&&setSelected(e.activePayload[0].payload)}>
              <XAxis type="number" tick={{fill:'#6b7694',fontSize:10}} axisLine={false} tickLine={false}/>
              <YAxis type="category" dataKey="feature" tick={{fill:'#6b7694',fontSize:11}} width={160} axisLine={false} tickLine={false}/>
              <Tooltip contentStyle={TS} formatter={v=>[v.toLocaleString(),'Importance']} cursor={{fill:'rgba(0,229,255,.05)'}}/>
              <Bar dataKey="importance" radius={[0,4,4,0]}>
                {features.map((f,i)=><Cell key={f.feature} fill={selected?.feature===f.feature?'#00e5ff':COLORS[i%COLORS.length]} opacity={selected?.feature===f.feature?1:0.75}/>)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div style={{display:'flex',flexDirection:'column',gap:16}}>
          {selected&&(
            <div className="card" style={{borderColor:'rgba(0,229,255,.25)'}}>
              <div className="card-title" style={{color:'var(--accent)'}}>{selected.feature}</div>
              <div style={{fontFamily:'var(--font-head)',fontSize:26,fontWeight:800,marginBottom:4}}>{selected.importance.toLocaleString()}</div>
              <div style={{fontSize:12,color:'var(--muted)',marginBottom:14}}>importance score</div>
              <div className="progress-wrap" style={{marginBottom:16}}><div className="progress-bar" style={{width:`${(selected.importance/maxImp)*100}%`}}/></div>
              <div style={{fontSize:13,color:'var(--muted)',lineHeight:1.7}}>{EXPLAIN[selected.feature]||'A behavioral or audio feature used to predict replay likelihood.'}</div>
            </div>
          )}
          <div className="card">
            <div className="card-title">Feature Categories</div>
            {[['User behavioral','user_replay_rate, user_skip_rate, user_avg_completion…','chip-cyan'],['Song-level','song_global_replay_rate, song_energy, song_valence…','chip-purple'],['Interaction','times_played_before, same_artist_plays…','chip-green'],['Temporal','hour_of_day, day_of_week, is_weekend, month','chip-cyan']].map(([cat,ex,cls])=>(
              <div key={cat} style={{padding:'12px 0',borderBottom:'1px solid var(--border)'}}>
                <div style={{marginBottom:4}}><span className={`chip ${cls}`}>{cat}</span></div>
                <div style={{fontSize:12,color:'var(--muted)'}}>{ex}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="section-gap card">
        <div className="card-title">All Features Ranked</div>
        <table><thead><tr><th>#</th><th>Feature</th><th>Importance</th><th>Relative</th></tr></thead>
        <tbody>
          {features.map((f,i)=>(
            <tr key={f.feature} onClick={()=>setSelected(f)} style={{cursor:'pointer'}}>
              <td style={{color:'var(--muted)',width:32}}>{i+1}</td>
              <td className="td-mono">{f.feature}</td>
              <td style={{fontFamily:'var(--font-head)',fontWeight:700}}>{f.importance.toLocaleString()}</td>
              <td style={{width:180}}><div className="td-bar-wrap"><div className="td-bar"><div className="td-bar-fill" style={{width:`${(f.importance/maxImp)*100}%`}}/></div><span style={{fontSize:11,color:'var(--muted)',width:38}}>{((f.importance/maxImp)*100).toFixed(0)}%</span></div></td>
            </tr>
          ))}
        </tbody></table>
      </div>
    </div>
  );
}