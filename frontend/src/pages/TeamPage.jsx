import TeamHeader from '../components/Team/EntityHeader'
import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getTeamDetails, getTeamMatches } from '../services/footballApi';
import './TeamPage.css'
import EntityHeader from '../components/Team/EntityHeader';
import Matches from '../components/Matches/Matches'
import TeamSquad from '../components/Team/TeamSquad'
import StandingsTable from '../components/StandingsTable/StandingsTable';
import TeamOverview from '../components/Team/TeamOverview';

const COMPONENT_CHOICES = {
    'matches': Matches,
    'squad': TeamSquad,
    'table': StandingsTable,
    'overview': TeamOverview,
}

const TEAM_TABS = [
{ id: 'overview', label: 'Огляд' },
{ id: 'matches', label: 'Матчі' },
{ id: 'squad', label: 'Склад' },
{ id: 'table', label: 'Таблиця' },
{ id: 'stats', label: 'Статистика' },
{ id: 'transfers', label: 'Трансфери' },
];

const TeamPage = () => {
    const { teamId } = useParams()

    const [teamData, setTeamData] = useState(null)
    const [isLoading, setIsLoading] = useState(true)

    const [matches, setMatches] = useState(null)
    const [tabId, setTabId] = useState('overview')




    useEffect(()=>{
        let timerId = null;
        const loadTeam = () =>{
            setIsLoading(true)
            getTeamDetails(teamId).then(data=>{
                if(data.status=='pending'){
                    timerId = setTimeout(loadTeam, 1500)
                }
                else{
                    setTeamData(data)
                    setIsLoading(false)
                }
            }).catch(()=>{
                setTeamData(null)
                setIsLoading(false)
            })
        }
        loadTeam()
        return () => {
            if(timerId){ clearTimeout(timerId) }
        }
    }, [teamId])   
    
    
    useEffect(() => {
        if(tabId !== 'matches') return;
        setIsLoading(true);
        getTeamMatches(teamId)
          .then(data => setMatches(data))
          .catch(err => console.error(err))
          .finally(() => setIsLoading(false));
      }, [tabId]);
    if (isLoading ) return <div>Завантаження данних</div>
    if (!teamData) return <div>Не вдалося завантажити дані</div>

    const SelectedComponent = COMPONENT_CHOICES[tabId]
    return (
        <div className="team-page">
        <EntityHeader 
        {...teamData} 
        tabs={TEAM_TABS} 
        tabId={tabId} 
        changeTab={setTabId}/>
        {!SelectedComponent ? <div>Компонент для вкладки ще у розробці...</div> : <SelectedComponent teamId={teamId} squad={teamData.squad} tournamentCode={teamData.main_league.code} matches={matches}/>}
        
        </div>
    )
}

export default TeamPage