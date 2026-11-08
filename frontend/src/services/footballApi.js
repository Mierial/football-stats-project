const BASE_URL = 'http://127.0.0.1:8000';

const request = async (endpoint) => {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`);

        if (!response.ok) {
            throw new Error('Помилка сервера або проблема з CORS!');
        }
        const data = await response.json();

        return data;

    } catch (error) {
        console.error("❌ Помилка в api.js:", error);
        throw error;
    }
}

export const getLeagueTable = (leagueCode) => {
    return request(`/tables/?group__tournament__code=${leagueCode}`);
};

export const getTeamDetails = (teamId) => {
    return request(`/teams/${teamId}/`);
};

export const getLeagueMatchesByMatchday = (leagueCode, matchday) => {
    return request(`/matches/?tournament__code=${leagueCode}&matchday=${matchday}`)
}

export const getMatchById = (matchId) => {
    return request(`/matches/${matchId}`)
}

export const getTeamMatches = (teamId) => {
    return request(`/matches/?team=${teamId}&ordering=date`)
}

export const getPlayersStatsByTeam = (teamId) => {
    return request(`player_stats/team=${teamId}`)
}

export const getPlayersStatsByTournament = (tournamentCode, filter) => {
    return request(`/player_stats/?tournament__code=${tournamentCode}&ordering=${filter}`)
}
export const getTeamOverview = (teamId) => {
    return request(`/teams/${teamId}/overview`)
}

export const getHomePage = () => {
    return request('/home')
}

export const getTournamentStats = (tournamentId) => {
    return request(`/tournaments/${tournamentId}/stats`)
}