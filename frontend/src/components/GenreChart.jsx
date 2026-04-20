import { BarChart, Bar, XAxis, YAxis, Tooltip,
    ResponsiveContainer, Cell } from 'recharts';

const COLORS = ['#534AB7','#1D9E75','#D85A30','#D4537E',
           '#888780','#378ADD','#639922','#BA7517'];

export default function GenreChart({ data }) {
const top = data.slice(0, 8);
return (
<div className="card">
 <h2>Games by genre</h2>
 <ResponsiveContainer width="100%" height={280}>
   <BarChart data={top} layout="vertical"
             margin={{ left: 80, right: 20, top: 0, bottom: 0 }}>
     <XAxis type="number" tick={{ fontSize: 12 }} />
     <YAxis type="category" dataKey="genre"
            tick={{ fontSize: 12 }} width={80} />
     <Tooltip
       formatter={(val, name) => [val, 'Games']}
       contentStyle={{ fontSize: 13 }}
     />
     <Bar dataKey="game_count" radius={[0, 4, 4, 0]}>
       {top.map((_, i) => (
         <Cell key={i} fill={COLORS[i % COLORS.length]} />
       ))}
     </Bar>
   </BarChart>
 </ResponsiveContainer>
</div>
);
}