import { useEffect, useState,useRef } from 'react';
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
import 'react-dropdown/style.css';
import '../style.css'


let window = []
let strDataN = [];
let strDataZ = [];
let strDataE = [];

const RealtimeChart = (props) => {
  const [data,setData] = useState([]);
  const [name,setName] = useState(null)
  const [P,setP] = useState(null);
  const [url,setUrl] = useState(props.url);

  let lst = useRef(null);
  let prevUrl = useRef(props.url);
  useEffect(() => {
    
    if(props.json!==null && props.json[99]!==undefined){
      setName(props.json[99].mseed_name);
      if(props.json[99].p_Arrival!==0 && props.json[99].p_Arrival!==null){
        setP(props.json[99].p_Arrival);
        if (props.json[25].p_Arrival===props.json[25].x){
          lst.current = props.json.slice(0,50);
          console.log(lst.current);
            
        }
        if (lst.current === null){
          setData(props.json);
        }
        else{
          setData(lst.current.concat(props.json.slice(50,100))) 
        }

      }
      else{
        setData(props.json);
      
      }
    }
    else{
    }
  
  }, [url,props]);

  useEffect(() => {
    lst.current = null
    setP(null);
},[url])

  return (
    <div data-testid = {props.testid} className='responsive-container'>
      <h className='station-title'>Stasiun {props.stasiun}</h>
      <div data-testid={name} className='flex-container'>
        <ResponsiveContainer height="100%" width="100%">
          <LineChart width={650} height={350} data={data}>
            <XAxis dataKey="time" xAxisId={0} axisLine={true} tick={true} tickLine={true}/>
            <XAxis dataKey="x" xAxisId={1} axisLine={false} tick={false} tickLine={false}/>
            <YAxis domain={[-1, 1]}/>
            <ReferenceLine x={P} stroke="red" xAxisId={1} />
            <Line type="monotone" isAnimationActive={false} dataKey="N_data" stroke="#8884d8" dot={false}/>
            <Line type="monotone" isAnimationActive={false} dataKey="Z_data" stroke="#82ca9d" dot={false}/>
            <Line type="monotone" isAnimationActive={false} dataKey="E_data" stroke="#ffc658" dot={false}/>
          </LineChart>
        </ResponsiveContainer>
        
      </div>
    </div>
    
  );
};
export default RealtimeChart
