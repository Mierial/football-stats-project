import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import {} from "../../services/footballApi"
import './Match.css'
const Match = ({match}) => {
    const getFormattedDate = (dateString) => {
        return dateString 
            ? new Date(dateString).toLocaleString('uk-UA', { 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit' 
              })
            : 'Час не визначено';
    };

    return (
        <Link className="match__link" to={`/matches/${match.id}`} key={match.id}>
            <div className="match-row">
                <div className="match-row__date">
                    {getFormattedDate(match.date)}
                </div>

                <div className="match-row__main">
                    <div className="match-row__team match-row__team--home">
                        <span className="match-row__team-name">{match.home_team?.name}</span>
                    </div>

                    <div className="match-row__center-core">
                        <img 
                            src={match.home_team?.logo} 
                            alt={match.home_team?.name || "Home Team"} 
                            className="match-row__logo" 
                            style={{ filter: 'var(--team-logo-shadow)' }}
                        />
                        
                        <div className="match-row__score-box">
                            <span className="match-row__score-digit">{match.home_goals ?? '-'}</span>
                            <span className="match-row__score-colon">:</span>
                            <span className="match-row__score-digit">{match.away_goals ?? '-'}</span>
                        </div>

                        <img 
                            src={match.away_team?.logo} 
                            alt={match.away_team?.name || "Away Team"} 
                            className="match-row__logo"
                            style={{ filter: 'var(--team-logo-shadow)' }}
                        />
                    </div>

                    <div className="match-row__team match-row__team--away">
                        <span className="match-row__team-name">{match.away_team?.name}</span>
                    </div>
                </div>
            </div>
        </Link>
    );
}
export default Match;
