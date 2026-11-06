import { useState, useEffect } from 'react';
import { getTeamOverview } from "../../services/footballApi";
import './TeamOverview.css';

const TeamOverview = ({ teamId }) => {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    getTeamOverview(teamId)
      .then((responseData) => {
        setData(responseData);
      })
      .catch((error) => {
        console.error("Помилка завантаження даних:", error);
      })
      .finally(() => setIsLoading(false));
  }, [teamId]);


  if (isLoading) {
    return (
      <div className="team-overview-wrapper" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <div style={{ color: 'var(--title-color)', fontSize: '1.25rem', fontWeight: 'bold' }}>
          Завантаження даних...
        </div>
      </div>
    );
  }

  const formatMatchDate = (isoString) => {
    const date = new Date(isoString);
    return new Intl.DateTimeFormat('uk-UA', {
      day: 'numeric',
      month: 'long',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const getFormClass = (result) => {
    switch (result) {
      case 'W': return 'form-w';
      case 'D': return 'form-d';
      case 'L': return 'form-l';
      default: return 'form-u';
    }
  };

  const { next_match, recent_form, mini_standings, main_league } = data;

  return (
    <div className="team-overview-wrapper">
      <div className="overview-container">
        
        <section className="overview-card next-match-card">
          <div className="next-match-bg"></div>
          
          <span className="league-badge">
            {main_league} • Тур {next_match.matchday}
          </span>
          
          <div className="match-content">
            <div className="team-info">
              <div className="team-logo-wrapper">
                <img src={next_match.home_team.logo} alt={next_match.home_team.name} className="team-logo" />
              </div>
              <span className="team-name">{next_match.home_team.name}</span>
            </div>

            <div className="match-status-center">
              <span className="status-label">Заплановано</span>
              <div className="match-date">
                {formatMatchDate(next_match.date)}
              </div>
            </div>

            {/* Команда гостей */}
            <div className="team-info">
              <div className="team-logo-wrapper">
                <img src={next_match.away_team.logo} alt={next_match.away_team.name} className="team-logo" />
              </div>
              <span className="team-name">{next_match.away_team.name}</span>
            </div>
          </div>
        </section>

        <div className="grid-container">
          {/* 2. Блок "Форма команди" */}
          <section className="overview-card">
            <h3 className="card-title">
              Форма команди
              <span className="card-subtitle">Останні 5</span>
            </h3>
            
            <div className="form-list">
              {recent_form.map((match, index) => (
                <div key={index} className="form-item">
                  <div className={`form-circle ${getFormClass(match.result)}`}>
                    {match.result}
                  </div>
                  
                  {/* Tooltip */}
                  <div className="form-tooltip">
                    <span className="tooltip-opponent">{match.opponent}</span>
                    <span className="tooltip-score">
                      Рахунок: <span>{match.score}</span>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* 3. Блок "Міні-таблиця" */}
          <section className="overview-card">
            <h3 className="card-title">Турнірна таблиця (Топ-3)</h3>
            <div className="table-wrapper">
              <table className="standings-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th style={{ width: '100%' }}>Команда</th>
                    <th className="td-center">І</th>
                    <th className="td-center">+/-</th>
                    <th className="td-center" style={{ color: 'var(--points-color)' }}>О</th>
                  </tr>
                </thead>
                <tbody>
                  {mini_standings.map((row) => {
                    // Використовуємо teamId з пропсів для перевірки
                    const isCurrentTeam = row.team.id === teamId;
                    
                    return (
                      <tr key={row.id} className={`table-row ${isCurrentTeam ? 'active' : ''}`}>
                        <td style={{ fontWeight: 'bold' }}>{row.place}</td>
                        <td>
                          <div className="team-cell">
                            <img src={row.image} alt={row.team.name} />
                            <span>{row.team.name}</span>
                          </div>
                        </td>
                        <td className="td-center">{row.games_played}</td>
                        <td className="td-center">
                          {row.goal_difference > 0 ? `+${row.goal_difference}` : row.goal_difference}
                        </td>
                        <td className="points-cell">{row.points}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

export default TeamOverview;