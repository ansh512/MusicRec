import React,{useEffect} from 'react';
import Song from './Song';
import '../styles/Box.css'; 

const Box = (props) => {

 
  return (
    <div className="container">
      <div className="row">
        {props.random.map((song, index) => (
          <Song key={index} songs={song} />
        ))}
      </div>
    </div>
  );
};

export default Box;