import './Table.css'
import { Link } from 'react-router-dom'

const TeamItem = (props) => {
 
   const {
        place,
        team,
        games_played,
        wins,
        draws, 
        losses,
        goals_for,
        goals_against, 
        goal_difference,
        points,
        image
    } = props



    return (
        <div className="team-container">
            <p className="team-container__place">{place}</p>
            <div className="team-container__info">
                <img src={image} alt={`${team.name} flag`} className="team-container__image" />
                <Link className="team-container__name" to={`/team/${team.id}`}>{team.name}</Link>
            </div>
            <p className="team-container__games">{games_played}</p>
            <p className="team-container__wins">{wins}</p>
            <p className="team-container__draws">{draws}</p>
            <p className="team-container__loses">{losses}</p>
            <p className="team-container__goals_for">{goals_for}</p>
            <p className="team-container__goals_against">{goals_against}</p>
            <p className="team-container__difference">{goal_difference}</p>
            <p className="team-container__points"><strong>{points}</strong></p>
        </div>
    )
}

export default TeamItem