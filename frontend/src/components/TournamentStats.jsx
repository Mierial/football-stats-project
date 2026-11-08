import { useState, useEffect } from "react";
import { getTournamentStats } from "../services/footballApi";
import "./TournamentStats.css";

const toPercent = (part, total) => `${(part / total) * 100}%`;

const TournamentStats = ({ tournamentId }) => {
    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setIsLoading(true);
        setError(null);

        getTournamentStats(tournamentId)
            .then((data) => setStats(data))
            .catch(() => setError("Не вдалося завантажити статистику"))
            .finally(() => setIsLoading(false));
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
        </section>
    );
};

export default TournamentStats;