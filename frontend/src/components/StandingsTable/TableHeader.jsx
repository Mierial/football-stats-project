import { useContext } from 'react';
import { LanguageContext } from '../../context/LanguageContext';

const TableHeader = (props) => {

    const { tableName } = props;
    
    const { choosedLanguage } = useContext(LanguageContext);

    return (
        <div className="group-header">
            <button className="group-header__show"># </button>
            <p className="group-header__name">{`${choosedLanguage.groupWord}`}</p>
            <p className="group-header__games">{choosedLanguage.stats_games}</p>
            <p className="group-header__wins">{choosedLanguage.stats_wins}</p>
            <p className="group-header__drawes">{choosedLanguage.stats_draws}</p>
            <p className="group-header__loses">{choosedLanguage.stats_losses}</p>
            <p className="group-header__goal-for">{choosedLanguage.stats_goalFor}</p>
            <p className="group-header__goal-against">{choosedLanguage.stats_goalAgainst}</p>
            <p className="group-header__goal-difference">{choosedLanguage.stats_goalDiff}</p>
            <p className="group-header__points">{choosedLanguage.stats_points}</p>
        </div>
    );
};

export default TableHeader;