import TableHeader from '../StandingsTable/TableHeader';
import TeamItem from '../StandingsTable/TeamItem';
import './GroupTable.css';

const TournamentGroup = (props) => {
    console.log('group')

    const {
        data,
    } = props

    return (
        <div className="table">
                {data.map((table) =>{
                    return (
                    <div className={data.length<=1 ? `table__item table__item--single` : `table__item`} key={table.groupName}>
                        <TableHeader groupName={group.groupName}/>
                        
                        { table.map((team)=>{
                            return <TeamItem {...team} key={team.name}/>
                        })}
                    </div>
                    )
                })}
            </div>
    );
};

export default TournamentGroup;