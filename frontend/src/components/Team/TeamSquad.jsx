import './TeamSquad.css';

const formatMarketValue = (value) => {
    if (!value || value === 0) return 'Ціна невідома';
    
    return new Intl.NumberFormat('uk-UA', { 
        style: 'currency', 
        currency: 'EUR',
        maximumFractionDigits: 0
    }).format(value);
};

const TeamSquad = ({ squad }) => {
    if (!squad || squad.length === 0) {
        return <div className="players-empty">Склад команди тимчасово недоступний або оновлюється перед сезоном 🛠️</div>;
    }
    return (
        <div className="players-section">
            <h2 className="players-section__title">Склад команди</h2>
            
            <div className="players-grid">
                {squad.map((player) => (
                    <div className="player-card" key={player.id}>
                        
                        <div className="player-card__header">
                            <div className="player-card__image-wrapper">
                                <img 
                                    src={player.image} 
                                    alt={player.full_name} 
                                    className="player-card__image" 
                                />
                            </div>
                            
                            {player.team_logo && (
                                <img 
                                    src={player.team_logo} 
                                    alt={player.team_name} 
                                    className="player-card__team-logo" 
                                    title={player.team_name}
                                />
                            )}
                        </div>

                        <div className="player-card__body">
                            <h3 className="player-card__name" title={player.full_name}>
                                {player.full_name}
                            </h3>
                            
                            <div className="player-card__details">
                                <span className="player-card__position">
                                    {player.position_name || 'Невідома позиція'}
                                </span>
                                <span className="player-card__value">
                                    {formatMarketValue(player.market_value)}
                                </span>
                            </div>
                        </div>

                    </div>
                ))}
            </div>
        </div>
    );
};

export default TeamSquad;