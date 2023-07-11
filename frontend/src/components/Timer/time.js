import React from 'react';
import { useTime } from 'react-timer-hook';
import '../style.css'
function MyTime() {
  const {
    seconds,
    minutes,
    hours,
    ampm,
  } = useTime({ format: '24-hour'});

  return (
    <div style={{textAlign: 'center'}}>
      <div style={{fontSize: '16px', padding: '2px'}}>
        <span>TIME : </span><span className='time'><span>{('0'+(hours).toString()).slice(-2)}</span>:<span>{('0'+(minutes).toString()).slice(-2)}</span>:<span>{('0'+(seconds).toString()).slice(-2)}</span><span>{ampm}</span></span>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <div>
      <MyTime />
    </div>
  );
}