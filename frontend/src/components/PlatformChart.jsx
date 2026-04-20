import { BarChart, Bar, XAxis, YAxis, Tooltip,
    ResponsiveContainer, Cell } from 'recharts';

export default function PlatformChart({ data }) {
const top = data.slice(0, 8);
return (
<div className="card">
 <h2>Games by platform</h2>
 <ResponsiveContainer width="100%" height={280}>
   <BarChart data={top} layout="vertical"
             margin={{ left: 100, right: 20, top: 0, bottom: 0 }}>
     <XAxis type="number" tick={{ fontSize: 12 }} />
     <YAxis type="category" dataKey="platform"
            tick={{ fontSize: 12 }} width={100} />
     <Tooltip
       formatter={(val) => [val, 'Games']}
       contentStyle={{ fontSize: 13 }}
     />
     <Bar dataKey="game_count" fill="#1D9E75"
          radius={[0, 4, 4, 0]} />
   </BarChart>
 </ResponsiveContainer>
</div>
);
}