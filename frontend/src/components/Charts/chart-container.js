import { useEffect, useState } from 'react';
import React from 'react';
import {
  Line,
  LineChart,
  XAxis,
  YAxis,
  Legend,
  ReferenceLine,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'
import axios from 'axios';
import 'react-dropdown/style.css';
import StopWatch from '../Timer/Stopwatch';
import RealtimeChart from './lineChart';
import '../style.css';


const ChartContainer = (props) => {
  const [data,setData] = useState([]);
  const [inputList, setInputList] = useState([]);

  const freezeChart = (data,line) => {

    return <div className='frozen-chart'>
                <ResponsiveContainer height="100%" width="100%">  
                <LineChart width={600} height={350} data={data}>
                    <XAxis dataKey="x"/>
                    <YAxis domain={[-1, 1]}/>
                    <ReferenceLine i={line} stroke="red" />
                    <Line type="monotone" isAnimationActive={false} dataKey="BHN" stroke="#8884d8" dot={false}/>
                    <Line type="monotone" isAnimationActive={false} dataKey="BHZ" stroke="#82ca9d" dot={false}/>
                    <Line type="monotone" isAnimationActive={false} dataKey="BHE" stroke="#ffc658" dot={false}/>
                </LineChart>
                </ResponsiveContainer>
            </div>
  }

  useEffect(() => {
    console.log(props.url+"  "+props.stasiun)
    inputList.concat(<RealtimeChart key={props.key} url={props.url} stasiun={props.stasiun} setDataframe={setData} />)
    
  }, []);
  
  
  return (
    <div>
        {inputList}
    </div>
    
  );
};
export default ChartContainer
