import { LineChart, Line, XAxis, YAxis, Tooltip,
    ResponsiveContainer, CartesianGrid } from 'recharts';

export default function YearlyChart({ data }) {
const filtered = data.filter(d => d.release_year >= 2000);
return (
<div className="card">
 <h2>Game releases per year (2000 – 2024)</h2>
 <ResponsiveContainer width="100%" height={260}>
   <LineChart data={filtered}
              margin={{ left: 0, right: 20, top: 10, bottom: 0 }}>
     <CartesianGrid strokeDasharray="3 3" stroke="#f0f0e8" />
     <XAxis dataKey="release_year" tick={{ fontSize: 12 }} />
     <YAxis tick={{ fontSize: 12 }} />
     <Tooltip contentStyle={{ fontSize: 13 }} />
     <Line type="monotone" dataKey="game_count"
           stroke="#534AB7" strokeWidth={2}
           dot={{ r: 3 }} activeDot={{ r: 5 }}
           name="Games released" />
   </LineChart>
 </ResponsiveContainer>
</div>
);
}