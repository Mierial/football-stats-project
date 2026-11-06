import TableHeader from "./TableHeader";
import TeamItem from "./TeamItem";
import { getLeagueTable } from "../../services/footballApi";
import {useState, useEffect} from "react"
const StandingsTable = ({tournamentCode}) => { 
  const [teamStats, setTeamStats] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(()=>{
    if(tournamentCode){
      setIsLoading(true)
      getLeagueTable(tournamentCode)
      .then(data => setTeamStats(data))
      .catch(error => console.log(error))
      .finally(()=>setIsLoading(false))
    }
  }, [tournamentCode])
  if(isLoading) return <div className="">{"Загрузка таблиці"}</div>
  return ( 
    <div className="main-content__table">
      <TableHeader />
      {teamStats.standings.map(team => 
        <TeamItem {...team} key={team.id} />
      )} 
    </div>
  );
};

export default StandingsTable;