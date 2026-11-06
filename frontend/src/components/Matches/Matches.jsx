import React from "react";
import Match from "./Match";
import './Matches.css';

const Matches = ({ matches = [] }) => {
  if (!matches) { return <div className="">Завантаження</div> }
  return (
    <div className="matches_container">
      {matches.map((matchData, index) => (
        <Match match={matchData} key={matchData.id || index} />
      ))}
    </div>
  );
};

export default Matches;