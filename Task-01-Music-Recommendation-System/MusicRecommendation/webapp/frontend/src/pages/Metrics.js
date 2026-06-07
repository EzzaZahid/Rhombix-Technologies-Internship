// import React, { useState, useEffect } from 'react';
// import {
//   RadarChart, Radar, PolarGrid, PolarAngleAxis,
//   BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, Legend
// } from 'recharts';

// const CYAN   = '#00e5ff';
// const PURPLE = '#a78bfa';
// const BG3    = '#141926';

// function MetricCard({ name, lgbm, baseline, description, lowerBetter }) {
//   const better = lowerBetter ? lgbm < baseline : lgbm > baseline;
//   const diff = lowerBetter ? baseline - lgbm : lgbm - baseline;
//   return (
//     <div className="card" style={{display:'flex', flexDirection:'column', gap:10}}>
//       <div className="card-title">{name}</div>
//       <div style={{display:'flex', gap:16, alignItems:'flex-end'}}>
//         <div>
//           <div style={{fontSize:11, color:'var(--muted)', marginBottom:4}}>LightGBM</div>
//           <div style={{fontFamily:'var(--font-head)', fontSize:28, fontWeight:800,
//             color: better ? 'var(--success)' : 'var(--error)'}}>
//             {lgbm?.toFixed(4)}
//           </div>
//         </div>
//         <div>
//           <div style={{fontSize:11, color:'var(--muted)', marginBottom:4}}>Baseline</div>
//           <div style={{fontFamily:'var(--font-head)', fontSize:20, fontWeight:600, color:'var(--muted)'}}>
//             {baseline?.toFixed(4)}
//           </div>
//         </div>
//         <div style={{marginLeft:'auto', textAlign:'right'}}>
//           <span style={{
//             fontSize:12, fontWeight:700,
//             color: better ? 'var(--success)' : 'var(--error)',
//           }}>
//             {better ? '▲' : '▼'} {Math.abs(diff*100).toFixed(1)}%
//           </span>
//           <div style={{fontSize:10, color:'var(--muted)'}}>vs baseline</div>
//         </div>
//       </div>
//       <div style={{fontSize:12, color:'var(--muted)', lineHeight:1.6, borderTop:'1px solid var(--border)', paddingTop:10}}>
//         {description}
//       </div>
//     </div>
//   );
// }

// export default function Metrics({ status }) {
//   const [data, setData] = useState(null);

//   useEffect(() => {
//     if (status?.status !== 'ready') return;
//     fetch('/api/metrics').then(r=>r.json()).then(setData).catch(()=>{});
//   }, [status?.status]);

//   if (status?.status !== 'ready') return (
//     <div>
//       <div className="page-header"><div className="page-title">Evaluation Metrics</div></div>
//       <div className="empty-state"><div className="icon">◉</div><div>Train a model first.</div></div>
//     </div>
//   );

//   if (!data) return <div className="empty-state"><span className="spinner"/></div>;

//   const { lgbm, baseline } = data;
//   const ks = [5, 10, 20];

//   // Bar chart data for @K metrics
//   const barData = ks.map(k => ({
//     k: `@${k}`,
//     'LightGBM Precision': lgbm[`precision_at_${k}`],
//     'Baseline Precision': baseline[`precision_at_${k}`],
//     'LightGBM NDCG': lgbm[`ndcg_at_${k}`],
//     'Baseline NDCG': baseline[`ndcg_at_${k}`],
//   }));

//   // Radar chart data
//   const radarData = [
//     { metric: 'AUC-ROC',  lgbm: lgbm.auc_roc,    base: baseline.auc_roc    },
//     { metric: 'NDCG@10',  lgbm: lgbm.ndcg_at_10, base: baseline.ndcg_at_10 },
//     { metric: 'P@10',     lgbm: lgbm.precision_at_10, base: baseline.precision_at_10 },
//     { metric: 'R@10',     lgbm: lgbm.recall_at_10,    base: baseline.recall_at_10    },
//     { metric: 'F1',       lgbm: lgbm.f1,              base: baseline.f1              },
//     { metric: 'Avg Prec', lgbm: lgbm.avg_precision,   base: baseline.avg_precision   },
//   ];

//   const tooltipStyle = { background:'#0e1320', border:'1px solid #1e2638', fontSize:12, color:'#e8eaf0' };

//   return (
//     <div>
//       <div className="page-header">
//         <div className="page-title">Evaluation Metrics</div>
//         <div className="page-sub">LightGBM vs Logistic Regression baseline — never skip this comparison</div>
//       </div>

//       {/* Key metrics grid */}
//       <div className="grid-2" style={{gap:16}}>
//         <MetricCard name="AUC-ROC"
//           lgbm={lgbm.auc_roc} baseline={baseline.auc_roc}
//           description="Does the model rank a song the user will replay above one they won't? 0.5 = random, 1.0 = perfect. The primary model quality metric." />
//         <MetricCard name="NDCG@10"
//           lgbm={lgbm.ndcg_at_10} baseline={baseline.ndcg_at_10}
//           description="Are the best replay songs ranked highest in the top-10 list? Position-aware — rank #1 is worth more than rank #10." />
//         <MetricCard name="Log Loss"
//           lgbm={lgbm.log_loss} baseline={baseline.log_loss} lowerBetter
//           description="Are predicted probabilities well-calibrated? Heavily penalises confident wrong predictions. Lower is always better." />
//         <MetricCard name="Avg Precision (PR-AUC)"
//           lgbm={lgbm.avg_precision} baseline={baseline.avg_precision}
//           description="Area under the Precision-Recall curve. Better than AUC-ROC for heavily imbalanced datasets where most labels are 0." />
//       </div>

//       {/* Charts */}
//       <div className="section-gap grid-2" style={{gap:24}}>
//         {/* Radar */}
//         <div className="card">
//           <div className="card-title">Model Capability Radar</div>
//           <ResponsiveContainer width="100%" height={280}>
//             <RadarChart data={radarData}>
//               <PolarGrid stroke="#1e2638"/>
//               <PolarAngleAxis dataKey="metric" tick={{fill:'#6b7694', fontSize:12}}/>
//               <Radar name="LightGBM" dataKey="lgbm" stroke={CYAN}   fill={CYAN}   fillOpacity={0.18}/>
//               <Radar name="Baseline" dataKey="base" stroke={PURPLE} fill={PURPLE} fillOpacity={0.12}/>
//               <Legend wrapperStyle={{fontSize:12}}/>
//               <Tooltip contentStyle={tooltipStyle} formatter={v => v.toFixed(4)}/>
//             </RadarChart>
//           </ResponsiveContainer>
//         </div>

//         {/* Bar chart @K */}
//         <div className="card">
//           <div className="card-title">Precision@K — LightGBM vs Baseline</div>
//           <ResponsiveContainer width="100%" height={280}>
//             <BarChart data={barData} barGap={4}>
//               <XAxis dataKey="k" tick={{fill:'#6b7694', fontSize:12}} axisLine={false} tickLine={false}/>
//               <YAxis tick={{fill:'#6b7694', fontSize:11}} axisLine={false} tickLine={false} domain={[0,1]}/>
//               <Tooltip contentStyle={tooltipStyle} formatter={v => v.toFixed(4)}/>
//               <Legend wrapperStyle={{fontSize:12}}/>
//               <Bar dataKey="LightGBM Precision" fill={CYAN}   radius={[4,4,0,0]}/>
//               <Bar dataKey="Baseline Precision"  fill={PURPLE} radius={[4,4,0,0]}/>
//             </BarChart>
//           </ResponsiveContainer>
//         </div>
//       </div>

//       {/* Full comparison table */}
//       <div className="section-gap card">
//         <div className="card-title">Full Metrics Table</div>
//         <div className="table-wrap">
//           <table>
//             <thead>
//               <tr>
//                 <th>Metric</th>
//                 <th><span className="chip chip-cyan">LightGBM</span></th>
//                 <th><span className="chip chip-purple">Baseline</span></th>
//                 <th>Winner</th>
//                 <th>Target</th>
//               </tr>
//             </thead>
//             <tbody>
//               {[
//                 ['AUC-ROC',        lgbm.auc_roc,         baseline.auc_roc,         false, '> 0.75'],
//                 ['Log Loss',       lgbm.log_loss,         baseline.log_loss,         true,  '< 0.45'],
//                 ['F1 Score',       lgbm.f1,               baseline.f1,               false, '> 0.60'],
//                 ['Avg Precision',  lgbm.avg_precision,    baseline.avg_precision,    false, '> 0.55'],
//                 ['Precision@5',    lgbm.precision_at_5,   baseline.precision_at_5,   false, '> 0.50'],
//                 ['Precision@10',   lgbm.precision_at_10,  baseline.precision_at_10,  false, '> 0.45'],
//                 ['Recall@10',      lgbm.recall_at_10,     baseline.recall_at_10,     false, '> 0.30'],
//                 ['NDCG@5',         lgbm.ndcg_at_5,        baseline.ndcg_at_5,        false, '> 0.60'],
//                 ['NDCG@10',        lgbm.ndcg_at_10,       baseline.ndcg_at_10,       false, '> 0.60'],
//                 ['NDCG@20',        lgbm.ndcg_at_20,       baseline.ndcg_at_20,       false, '> 0.55'],
//               ].map(([name, l, b, lower, target]) => {
//                 const lgbmWins = lower ? l < b : l > b;
//                 return (
//                   <tr key={name}>
//                     <td style={{fontWeight:500}}>{name}</td>
//                     <td className="td-mono">{l?.toFixed(4)}</td>
//                     <td style={{color:'var(--muted)'}}>{b?.toFixed(4)}</td>
//                     <td>
//                       <span className={`chip ${lgbmWins ? 'chip-cyan' : 'chip-purple'}`}>
//                         {lgbmWins ? 'LightGBM' : 'Baseline'}
//                       </span>
//                     </td>
//                     <td style={{fontSize:12, color:'var(--muted)'}}>{target}</td>
//                   </tr>
//                 );
//               })}
//             </tbody>
//           </table>
//         </div>
//       </div>
//     </div>
//   );
// }





import React, { useState, useEffect } from 'react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const CYAN='#00e5ff', PURPLE='#a78bfa';
const TS = {background:'#0e1320',border:'1px solid #1e2638',fontSize:12,color:'#e8eaf0'};

function MetricCard({ name, lgbm, baseline, description, lowerBetter }) {
  const better = lowerBetter ? lgbm < baseline : lgbm > baseline;
  const diff = lowerBetter ? baseline - lgbm : lgbm - baseline;
  return (
    <div className="card" style={{display:'flex',flexDirection:'column',gap:10}}>
      <div className="card-title">{name}</div>
      <div style={{display:'flex',gap:16,alignItems:'flex-end'}}>
        <div><div style={{fontSize:11,color:'var(--muted)',marginBottom:4}}>LightGBM</div><div style={{fontFamily:'var(--font-head)',fontSize:28,fontWeight:800,color:better?'var(--success)':'var(--error)'}}>{lgbm?.toFixed(4)}</div></div>
        <div><div style={{fontSize:11,color:'var(--muted)',marginBottom:4}}>Baseline</div><div style={{fontFamily:'var(--font-head)',fontSize:20,fontWeight:600,color:'var(--muted)'}}>{baseline?.toFixed(4)}</div></div>
        <div style={{marginLeft:'auto',textAlign:'right'}}><span style={{fontSize:12,fontWeight:700,color:better?'var(--success)':'var(--error)'}}>{better?'▲':'▼'} {Math.abs(diff*100).toFixed(1)}%</span><div style={{fontSize:10,color:'var(--muted)'}}>vs baseline</div></div>
      </div>
      <div style={{fontSize:12,color:'var(--muted)',lineHeight:1.6,borderTop:'1px solid var(--border)',paddingTop:10}}>{description}</div>
    </div>
  );
}

export default function Metrics({ status }) {
  const [data, setData] = useState(null);
  useEffect(()=>{if(status?.status!=='ready')return;fetch('/api/metrics').then(r=>r.json()).then(setData).catch(()=>{});},[status?.status]);

  if (status?.status!=='ready') return <div><div className="page-header"><div className="page-title">Evaluation Metrics</div></div><div className="empty-state"><div className="icon">◉</div><div>Train a model first.</div></div></div>;
  if (!data) return <div className="empty-state"><span className="spinner"/></div>;

  const {lgbm,baseline}=data;
  const radarData=[
    {metric:'AUC-ROC',lgbm:lgbm.auc_roc,base:baseline.auc_roc},
    {metric:'NDCG@10',lgbm:lgbm.ndcg_at_10,base:baseline.ndcg_at_10},
    {metric:'P@10',lgbm:lgbm.precision_at_10,base:baseline.precision_at_10},
    {metric:'R@10',lgbm:lgbm.recall_at_10,base:baseline.recall_at_10},
    {metric:'F1',lgbm:lgbm.f1,base:baseline.f1},
    {metric:'AvgPrec',lgbm:lgbm.avg_precision,base:baseline.avg_precision},
  ];
  const barData=[5,10,20].map(k=>({k:`@${k}`,'LightGBM':lgbm[`precision_at_${k}`],'Baseline':baseline[`precision_at_${k}`]}));

  return (
    <div>
      <div className="page-header"><div className="page-title">Evaluation Metrics</div><div className="page-sub">LightGBM vs Logistic Regression baseline</div></div>
      <div className="grid-2" style={{gap:16}}>
        <MetricCard name="AUC-ROC" lgbm={lgbm.auc_roc} baseline={baseline.auc_roc} description="Does the model rank replay songs above non-replay songs? 0.5=random, 1.0=perfect."/>
        <MetricCard name="NDCG@10" lgbm={lgbm.ndcg_at_10} baseline={baseline.ndcg_at_10} description="Are the best replay songs ranked highest? Position-aware — rank #1 is worth more than #10."/>
        <MetricCard name="Log Loss" lgbm={lgbm.log_loss} baseline={baseline.log_loss} lowerBetter description="Are probabilities well-calibrated? Penalises confident wrong predictions. Lower is better."/>
        <MetricCard name="Avg Precision" lgbm={lgbm.avg_precision} baseline={baseline.avg_precision} description="Area under Precision-Recall curve. Better than AUC-ROC for imbalanced datasets."/>
      </div>
      <div className="section-gap grid-2" style={{gap:24}}>
        <div className="card">
          <div className="card-title">Capability Radar</div>
          <ResponsiveContainer width="100%" height={280}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#1e2638"/><PolarAngleAxis dataKey="metric" tick={{fill:'#6b7694',fontSize:12}}/>
              <Radar name="LightGBM" dataKey="lgbm" stroke={CYAN} fill={CYAN} fillOpacity={0.18}/>
              <Radar name="Baseline" dataKey="base" stroke={PURPLE} fill={PURPLE} fillOpacity={0.12}/>
              <Legend wrapperStyle={{fontSize:12}}/><Tooltip contentStyle={TS} formatter={v=>v.toFixed(4)}/>
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <div className="card-title">Precision@K Comparison</div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={barData} barGap={4}>
              <XAxis dataKey="k" tick={{fill:'#6b7694',fontSize:12}} axisLine={false} tickLine={false}/>
              <YAxis tick={{fill:'#6b7694',fontSize:11}} axisLine={false} tickLine={false} domain={[0,1]}/>
              <Tooltip contentStyle={TS} formatter={v=>v.toFixed(4)}/><Legend wrapperStyle={{fontSize:12}}/>
              <Bar dataKey="LightGBM" fill={CYAN} radius={[4,4,0,0]}/><Bar dataKey="Baseline" fill={PURPLE} radius={[4,4,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="section-gap card">
        <div className="card-title">Full Metrics Table</div>
        <table><thead><tr><th>Metric</th><th>LightGBM</th><th>Baseline</th><th>Winner</th><th>Target</th></tr></thead>
        <tbody>
          {[['AUC-ROC',lgbm.auc_roc,baseline.auc_roc,false,'> 0.75'],['Log Loss',lgbm.log_loss,baseline.log_loss,true,'< 0.45'],['F1 Score',lgbm.f1,baseline.f1,false,'> 0.60'],['NDCG@5',lgbm.ndcg_at_5,baseline.ndcg_at_5,false,'> 0.60'],['NDCG@10',lgbm.ndcg_at_10,baseline.ndcg_at_10,false,'> 0.60'],['Precision@10',lgbm.precision_at_10,baseline.precision_at_10,false,'> 0.45'],['Recall@10',lgbm.recall_at_10,baseline.recall_at_10,false,'> 0.30']].map(([name,l,b,lower,target])=>{
            const lgbmWins=lower?l<b:l>b;
            return(<tr key={name}><td style={{fontWeight:500}}>{name}</td><td className="td-mono">{l?.toFixed(4)}</td><td style={{color:'var(--muted)'}}>{b?.toFixed(4)}</td><td><span className={`chip ${lgbmWins?'chip-cyan':'chip-purple'}`}>{lgbmWins?'LightGBM':'Baseline'}</span></td><td style={{fontSize:12,color:'var(--muted)'}}>{target}</td></tr>);
          })}
        </tbody></table>
      </div>
    </div>
  );
}