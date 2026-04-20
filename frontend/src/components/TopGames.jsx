export default function TopGames({ data }) {
    return (
      <div className="card">
        <h2>Top rated games</h2>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Game</th>
              <th>Rating</th>
              <th>Metacritic</th>
              <th>Released</th>
              <th>Playtime (hrs)</th>
            </tr>
          </thead>
          <tbody>
            {data.map((game, i) => (
              <tr key={game.id}>
                <td style={{ color: '#888', width: 32 }}>{i + 1}</td>
                <td style={{ fontWeight: 500 }}>{game.name}</td>
                <td>
                  <span style={{
                    background: '#EEEDFE', color: '#3C3489',
                    padding: '2px 8px', borderRadius: 999,
                    fontSize: 12, fontWeight: 500
                  }}>
                    {Number(game.rating).toFixed(2)}
                  </span>
                </td>
                <td>{game.metacritic ?? '—'}</td>
                <td style={{ color: '#888', fontSize: 13 }}>
                  {game.released ? game.released.slice(0, 4) : '—'}
                </td>
                <td>{game.playtime ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }