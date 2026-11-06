import StadingsTable from '../components/StandingsTable/StandingsTable'
import GroupTable from '../components/StandingsTable/GroupTable'
import EntityHeader from '../components/Team/EntityHeader'
import Matches from '../components/Matches/Match'
import Scorers from '../components/Tabs/PlayerStats'
import { getLeagueTable } from '../services/footballApi'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'

const TournamentPage = () => {
    const [teamStandings, setTeamStandings] = useState([])
    const { leagueCode } = useParams()
    const [isLoading, setIsLoading] = useState(true)

    const [activeTab, setActiveTab] = useState('table')
    
    const LEAGUE_TABS = [
    { id: 'table', label: 'Турнірна таблиця' },
    { id: 'matches', label: 'Календар і результати' },
    { id: 'scorers', label: 'Статистика гравців' },
    ];

    const COMPONENT_CHOICES = 
        {'table': StadingsTable, 
         'matches': Matches,
         'scorers': Scorers,   
        }
    

    const changeTab = (tabId) => {
        setActiveTab(tabId)
    }

    const ActiveComponent = COMPONENT_CHOICES[activeTab]

    useEffect(()=>{
        setIsLoading(true)
        getLeagueTable(leagueCode).then(data=>{
            setTeamStandings(data)
        }).catch(()=>{
            setTeamStandings(null)
        }).finally(()=>{
            setIsLoading(false)
        })
    }, [leagueCode])

    if (isLoading) return <div>Завантаження таблиці...</div>;
    if (!teamStandings) return <div>Не вдалося завантажити дані.</div>;

    const tournament = teamStandings.tournament
    return(
        <>
            <EntityHeader tabs={LEAGUE_TABS} 
            tournament={tournament} 
            changeTab={changeTab} 
            tabId={activeTab}/>
            {ActiveComponent&& (
            <div className="main-content__tab">
            <ActiveComponent teamStats={teamStandings} tournamentCode={tournament.code} currentMatchday={tournament.matchday} />
            </div>
            )}
        </>
    )
}

export default TournamentPage