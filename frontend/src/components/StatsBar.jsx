export default function StatsBar({ stats }) {
    const items = [
      { label: 'Total games',     value: stats.total_games.toLocaleString() },
      { label: 'Genres',          value: stats.total_genres },
      { label: 'Platforms',       value: stats.total_platforms },
      { label: 'Avg rating',      value: stats.avg_rating },
      { label: 'Avg metacritic',  value: stats.avg_metacritic },
    ];
    return (
      <div className="stats-bar">
        {items.map(item => (
          <div className="stat-card" key={item.label}>
            <div className="label">{item.label}</div>
            <div className="value">{item.value}</div>
          </div>
        ))}
      </div>
    );
  }