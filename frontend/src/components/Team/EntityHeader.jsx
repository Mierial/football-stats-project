import React from 'react';
import { Link } from 'react-router-dom';
import './EntityHeader.css'
const EntityHeader = (props) => {
    const {
        name,
        image,
        coach,
        stadium,
        country,
        website,
        main_league,
        tabs = [],
        tournament,
        changeTab,
        tabId,
    } = props;

    const displayTitle = name || tournament?.name || 'Без назви'
    const displayLogo = image || tournament?.image
    const breadcrumbLeague = main_league
    const hasDetails = website || coach || stadium
    const displayCountry = country || tournament?.country
    const percents = 2

    return (
        <>
        <header className="page-header">
            <div className="page-header__container container">
                {breadcrumbLeague && (
                <div className="page-header__breadcrumbs">
                    <Link to={`/tournament/${breadcrumbLeague.code}`} className="breadcrumbs__link">
                        <img src={breadcrumbLeague.image} alt="" className="breadcrumbs__logo" />
                        <span className="breadcrumbs__name">{breadcrumbLeague.name}</span>
                    </Link>
                    <span className='breadcrumbs__separator'>{"/"}</span>
                    <span className="breadcrumbs__current">{displayTitle}</span>
                </div>
                )}

                <div className="page-header__content"> 
                    <div className="page-header__main-info">
                        <img src={displayLogo} alt="entity-logo" className="page-header__logo" />
                        <div className="page-header__text-block">
                            <h4 className="page-header__title">{displayTitle}</h4>
                                <div className="page-header__badge">
                                    <img src={displayCountry.flag} alt="" className="badge__flag" />
                                    <p className="badge__text">{displayCountry.name}</p>
                                </div>
                        </div>
                    </div>
                    {tournament && (
                        <div className="page-header__date">
                            <span className="date__period">{`${tournament.start_date} - ${tournament.end_date}`}</span>
                            <span className="date__end">{`Залишиилось: ${tournament.days_to_end} дн.`}</span>
                            <div className="date__progress-bar">
                                <div className="date__progress-fill" 
                                style={{width: `${percents}%`}}
                                />
                            </div>
                        </div>
                    )}
                    {hasDetails && (
                    <div className="page-header__details">
                        <div className="page-header__card">
                            <span className="card__label">Тренер</span>
                            <span className="card__value">{coach ?? 'Немає інформації'}</span>
                        </div>
                        
                        <div className="page-header__card">
                            <span className="card__label">Домашня арена</span>
                            <span className="card__value">{stadium}</span>
                        </div>
                        
                        <div className="page-header__card page-header__card--link">
                            <span className="card__label">Офіційний сайт</span>
                            <a className="card__link" href={website} target="_blank" rel="noreferrer">Відвідати сайт</a>
                        </div>
                    </div>
                    )}
                </div> 
            </div>
        </header>
        <div className="team-page__navigation">
            {tabs.map((tab)=>{
                return <button key={tab.id} className={`navigation__button ${tabId === tab.id ? 'navigation__button--active' : ''}`}
                onClick={()=>{changeTab(tab.id)}}>{tab.label}</button>
            })}
        </div>
        </>
    );
};

export default EntityHeader;