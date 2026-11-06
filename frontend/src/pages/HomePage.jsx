import React, { useState, useEffect } from 'react';
import { getHomePage } from '../services/footballApi';
import './HomePage.css';
import Matches from '../components/Matches/Matches';

const HomePage = () => {
  const [matches, setMatches] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const [matchesStatus, setMatchesStatus] = useState('ALL');
  const [dayOfMatch, setDayOfMatch] = useState('today');

  const matchesStatuses = ['ALL', 'IN_PLAY', 'FINISHED', 'TIMED'];
  const matchesStatusesDict = {
    'ALL': 'Всі',
    'IN_PLAY': 'Лайв',
    'FINISHED': 'Завершені',
    'TIMED': 'Заплановані',
  };

  useEffect(() => {
    setIsLoading(true);
    getHomePage()
      .then(data => setMatches(data.matches))
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <div className="loading">loading...</div>;
  }

  const dayMatches = matches?.[dayOfMatch] || [];
  const filteredMatches = dayMatches.filter((iter_match) => {
    if (matchesStatus === 'ALL') return true;
    if (iter_match.status === 'SCHEDULED' && matchesStatus === 'TIMED') return true;
    return iter_match.status === matchesStatus;
  });

  return (
    <div className="home-page__container">

      <div className="matches__status">
        {matchesStatuses.map((status) => (
          <button
            className={`status__btn ${matchesStatus === status ? 'active' : ''}`}
            key={status}
            onClick={() => setMatchesStatus(status)}
          >
            {matchesStatusesDict[status]}
          </button>
        ))}
      </div>

      <Matches matches={filteredMatches} />
    </div>
  );
};

export default HomePage;