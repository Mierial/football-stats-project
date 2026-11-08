// Matches.jsx
import { useState, useEffect } from "react";
import { getLeagueMatchesByMatchday } from "../../services/footballApi";
import Match from "./Match";
import "./Matches.css";

const Matches = ({ tournamentCode, currentMatchday }) => {
    const [matches, setMatches] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!currentMatchday) return;

        let isActive = true;
        setIsLoading(true);
        setError(null);

        getLeagueMatchesByMatchday(tournamentCode, currentMatchday)
            .then((data) => isActive && setMatches(data))
            .catch(() => isActive && setError("Не вдалося завантажити матчі"))
            .finally(() => isActive && setIsLoading(false));

        return () => {
            isActive = false;
        };
    }, [tournamentCode, currentMatchday]);

    if (isLoading) return <div>Завантаження...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="matches_container">
            {matches.map((match) => (
                <Match match={match} key={match.id} />
            ))}
        </div>
    );
};

export default Matches;