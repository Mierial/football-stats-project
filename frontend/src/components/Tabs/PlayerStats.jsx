import { useState, useEffect } from "react"
import { getPlayersStatsByTeam, getPlayersStatsByTournament } from "../../services/footballApi"
import './PlayerStats.css'

const PlayerStats = ({teamId, teamStats}) => {

    const [playersStat, setPlayersStat] = useState({})
    const [isLoading, setIsLoading] = useState(true)
    const tournamentCode = teamStats?.tournament?.code
    const [activeFilter, setActiveFilter] = useState('-goals')

    useEffect(()=>{
        if(!teamId && !tournamentCode){
            return;
        }
        if (teamId) {
            getPlayersStatsByTeam(teamId)
                .then((data) => {
                    setPlayersStat(data);
                })
                .catch((error) => {
                    console.log(error);
                })
                .finally(() => {
                    setIsLoading(false);
                });
            return; 
        }
        if (tournamentCode) {
            getPlayersStatsByTournament(tournamentCode, activeFilter)
                .then((data) => {
                    setPlayersStat(data);
                })
                .catch((error) => {
                    console.log(error);
                })
                .finally(() => {
                    setIsLoading(false);
                });
        }
    }, [tournamentCode, teamId, activeFilter]);

    if(isLoading){ 
        return <div className="">Завантаження данних</div> 
    }
    
    const filteredStatsByGoals = [...playersStat].sort((a,b)=>b.goals-a.goals) 
    const filteredStatsByAssists = [...playersStat].sort((a,b)=>b.assists-a.assists)


    const handleFilterStats = (field) => {
        if(field === activeFilter){
            setActiveFilter(`-${field}`)
        } else if(activeFilter === `-${field}`){
            setActiveFilter(field)
        } else{
            setActiveFilter(`-${field}`)
        }
    } 

    return(
        <div className="player-stats__window">
            <div className="player_stats__filter-options">
                <p className="filter-options__text">#</p>
                <p className="filter-options__text">club</p>
                <p className="filter-options__text">player</p>
                <button className={`filter-options__button ${['goals', '-goals'].includes(activeFilter) ? 'active' : ''}`} onClick={()=>{
                    handleFilterStats('goals')

                    }}
                    >
                    goals
                </button>
                <button className={`filter-options__button ${['assists', '-assists'].includes(activeFilter) ? 'active' : ''}`} onClick={()=>{
                    handleFilterStats('assists')
                    }}
                    >
                        assists
                    </button>

            </div>
            {playersStat.map((stat)=>
                <div className="player_stats__item" key={stat.player.full_name}>
                    <p className="player-stats__position">{stat.place}</p>
                    <img src={stat.player.team_logo} alt="" className="player-stats__image" />
                    <div className="player-stats__info">
                        <p className="player-stats__name">{stat.player.full_name}</p>
                        <img src={stat.player.image} alt="" className="player-stats__image" />
                    </div>
                    <p className={`player-stats__goals ${['goals', '-goals'].includes(activeFilter) ? 'active' : ''}`}>{stat.goals}</p>
                    <p className={`player-stats__assists ${['assists', '-assists'].includes(activeFilter) ? 'active' : ''}`}>{stat.assists}</p>
                </div>
            )}
        </div>
    )
}


export default PlayerStats