import { useState, useEffect } from "react";
import { getTournamentStats } from "../services/footballApi";
import "./TournamentStats.css";

const toPercent = (part, total) => `${(part / total) * 100}%`;

const TournamentStats = ({ tournamentId }) => {
    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let isActive = true;

        setIsLoading(true);
        setError(null);

        getTournamentStats(tournamentId)
            .then((data) => isActive && setStats(data))
            .catch(() => isActive && setError("Не вдалося завантажити статистику"))
            .finally(() => isActive && setIsLoading(false));

        return () => {
            isActive = false;
        };
    }, [tournamentId]);

    if (isLoading) {
        return <p className="tournament-stats__message">Завантаження...</p>;
    }

    if (error) {
        return <p className="tournament-stats__message tournament-stats__message--error">{error}</p>;
    }

    if (!stats?.matches) {
        return <p className="tournament-stats__message">У турнірі ще немає завершених матчів</p>;
    }

    const summary = [
        { label: "Матчів", value: stats.matches },
        { label: "Голів", value: stats.total_goals },
        { label: "Середньо за матч", value: stats.avg_goals },
        { label: "Найбільше в матчі", value: stats.max_goals_in_match },
    ];

    const outcomes = [
        { label: "Господарі", value: stats.home_wins_count, modifier: "home" },
        { label: "Нічиї", value: stats.draws_count, modifier: "draw" },
        { label: "Гості", value: stats.away_wins_count, modifier: "away" },
    ];

    const topTeams = stats.top_teams_by_goals ?? [];
    const matchdays = stats.goals_by_matchday ?? [];

    const maxTeamGoals = Math.max(...topTeams.map(({ goals }) => goals), 1);
    const maxMatchdayGoals = Math.max(...matchdays.map(({ goals }) => goals), 1);

    return (
        <section className="tournament-stats">
            <h2 className="tournament-stats__title">Статистика турніру</h2>

            <dl className="tournament-stats__grid">
                {summary.map(({ label, value }) => (
                    <div key={label} className="tournament-stats__card">
                        <dt className="tournament-stats__label">{label}</dt>
                        <dd className="tournament-stats__value">{value}</dd>
                    </div>
                ))}
            </dl>

            <div className="tournament-stats__outcomes">
                <div className="tournament-stats__bar">
                    {outcomes.map(({ modifier, value }) => (
                        <span
                            key={modifier}
                            className={`tournament-stats__segment tournament-stats__segment--${modifier}`}
                            style={{ width: toPercent(value, stats.matches) }}
                        />
                    ))}
                </div>

                <ul className="tournament-stats__legend">
                    {outcomes.map(({ label, value, modifier }) => (
                        <li key={modifier} className="tournament-stats__legend-item">
                            <span className={`tournament-stats__dot tournament-stats__segment--${modifier}`} />
                            {label}: <strong>{value}</strong>
                        </li>
                    ))}
                </ul>
            </div>

            {topTeams.length > 0 && (
                <div className="tournament-stats__block">
                    <h3 className="tournament-stats__subtitle">Найрезультативніші команди</h3>

                    <ol className="tournament-stats__teams">
                        {topTeams.map(({ team, goals }, index) => (
                            <li key={team} className="tournament-stats__team">
                                <span className="tournament-stats__team-place">{index + 1}</span>
                                <span className="tournament-stats__team-name">{team}</span>
                                <span className="tournament-stats__team-track">
                                    <span
                                        className="tournament-stats__team-bar"
                                        style={{ width: toPercent(goals, maxTeamGoals) }}
                                    />
                                </span>
                                <span className="tournament-stats__team-goals">{goals}</span>
                            </li>
                        ))}
                    </ol>
                </div>
            )}

            {matchdays.length > 0 && (
                <div className="tournament-stats__block">
                    <h3 className="tournament-stats__subtitle">Голи по турах</h3>

                    <div className="tournament-stats__chart">
                        {matchdays.map(({ matchday, matches, goals }) => (
                            <div
                                key={matchday}
                                className="tournament-stats__column"
                                title={
                                    matches
                                        ? `Тур ${matchday}: голів ${goals}, матчів ${matches}`
                                        : `Тур ${matchday}: голів ${goals}`
                                }
                            >
                                <div className="tournament-stats__column-track">
                                    <span className="tournament-stats__column-value">{goals}</span>
                                    <span
                                        className="tournament-stats__column-bar"
                                        style={{ height: `calc((100% - 18px) * ${goals / maxMatchdayGoals})` }}
                                    />
                                </div>
                                <span className="tournament-stats__column-label">{matchday}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </section>
    );
};

export default TournamentStats;