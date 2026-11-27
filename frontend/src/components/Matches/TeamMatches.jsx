import { useState, useEffect } from "react";
import { getTeamMatches } from "../../services/footballApi";
import Match from "./Match";

const TeamMatches = ({ teamId }) => {
    const [matches, setMatches] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!teamId) return;

        let isActive = true;
        setIsLoading(true);
        setError(null);

        getTeamMatches(teamId)
            .then((data) => isActive && setMatches(data))
            .catch(() => isActive && setError("Не вдалося завантажити матчі"))
            .finally(() => isActive && setIsLoading(false));

        return () => {
            isActive = false;
        };
    }, [teamId]);

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

export default TeamMatches;