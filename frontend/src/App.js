import { useState, useEffect } from 'react';
import StatsBar from './components/StatsBar';
import TopGames from './components/TopGames';
import GenreChart from './components/GenreChart';
import YearlyChart from './components/YearlyChart';
import PlatformChart from './components/PlatformChart';
import './App.css';

const API = process.env.REACT_APP_API_URL;

export default function App() {
  const [stats,    setStats]    = useState(null);
  const [games,    setGames]    = useState([]);
  const [genres,   setGenres]   = useState([]);
  const [yearly,   setYearly]   = useState([]);
  const [platforms,setPlatforms]= useState([]);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/stats`).then(r => r.json()),
      fetch(`${API}/api/games?limit=20&order=rating`).then(r => r.json()),
      fetch(`${API}/api/genres`).then(r => r.json()),
      fetch(`${API}/api/yearly`).then(r => r.json()),
      fetch(`${API}/api/platforms`).then(r => r.json()),
    ]).then(([s, g, ge, y, p]) => {
      setStats(s);
      setGames(g);
      setGenres(ge);
      setYearly(y);
      setPlatforms(p);
      setLoading(false);
    });
  }, []);

  if (loading) return (
    <div style={{ display:'flex', alignItems:'center',
                  justifyContent:'center', height:'100vh',
                  fontSize:16, color:'#888' }}>
      Loading GamePulse...
    </div>
  );

  return (
    <div className="app">
      <header className="header">
        <h1>GamePulse</h1>
        <p>Gaming analytics dashboard — {stats.total_games.toLocaleString()} games tracked</p>
      </header>
      <main className="main">
        <StatsBar stats={stats} />
        <div className="grid-2">
          <GenreChart  data={genres} />
          <PlatformChart data={platforms} />
        </div>
        <YearlyChart data={yearly} />
        <TopGames    data={games} />
      </main>
    </div>
  );
}