import { useEffect, useState,useRef } from 'react';
import React from 'react';
import {
  Label,
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
import 'react-dropdown/style.css';
import '../style.css'

const RealtimeChart = (props) => {
  const [data, setData] = useState(Array.from({length: 100}, (v, k) => {}));
  const [name, setName] = useState(null)
  const [p, setP] = useState(null);

   useEffect(() => {
    
    // if(props.json!==null && props.json[99]!==undefined){
    //   setName(props.json[99].mseed_name);
    //   if(props.json[99].p_Arrival !== 0 && props.json[99].p_Arrival !== null){
    //     setP(props.json[99].p_Arrival);
    //     if (props.json[25].p_Arrival === props.json[25].x){
    //       lst.current = props.json.slice(0,50);
    //       console.log(lst.current);
    //     }
    //     if (lst.current === null){
    //       setData(props.json);
    //     }
    //     else {
    //       setData(lst.current.concat(props.json.slice(50,100))) 
    //     }
    //   }
    //   else {
    //     setData(props.json);
    //   }
    // }
    // else {
      
    // }

    let mappedData = []
    Object.entries(props.json).forEach(([key, value]) => {
      Object.entries(value).forEach(([index, point]) => {
        let points = mappedData[index] != undefined ? mappedData[index] : {}
        points[key] = point
        points["time"] =  new Date(props.time[index]).toLocaleTimeString()
        mappedData[index] = points
      })
    })

    setData((prev) => [...prev.slice(25), ...mappedData])
  
  }, [props]);

  function yAxisFormatter(y) {
    if (y > 0) {
      return y/y
    } else if (y == 0) {
      return 0
    } else {
      return -(y/y)
    }
  }

  return (
    <div data-testid = {props.testid} className='responsive-container'>
      <p className='station-title'>Stasiun {props.stasiun}</p>
      <div data-testid={props.testid} className='flex-container'>
        <ResponsiveContainer height="100%" width="100%">
          <LineChart width={650} height={350} data={data}>
            <XAxis dataKey="time" xAxisId={0} axisLine={true} tick={true} tickLine={true} angle={-45}  padding="gap"/>
            <XAxis dataKey="x" xAxisId={1} axisLine={false} tick={false} tickLine={false}/>
            <YAxis type='number' domain={[-1000, 1000]} tickCount={3} tickFormatter={yAxisFormatter}/>
            <ReferenceLine x={p} stroke="red" xAxisId={1} />
            <Line type="linear" isAnimationActive={false} dataKey="BHN" stroke="#8884d8" dot={false}/>
            <Line type="linear" isAnimationActive={false} dataKey="BHZ" stroke="#82ca9d" dot={false}/>
            <Line type="linear" isAnimationActive={false} dataKey="BHE" stroke="#ffc658" dot={false}/>
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
export default RealtimeChart
