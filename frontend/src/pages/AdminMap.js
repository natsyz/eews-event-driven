import React,{useEffect, useState, useRef} from "react";
import "chartjs-plugin-streaming";
import '../App.css';
import RealtimeChart from "../components/Charts/lineChart";
import Ptable from "../components/Tabel";
import MyTime from "../components/Timer/time"
import 'bootstrap/dist/css/bootstrap.min.css';
import Map from "../components/Map/Map2"
import Checklist from "../components/Checklist/checklist";
import Legend from "../components/Legend/Legend-Button";
// import Performance from "../components/Legend/Performance";
import Button from "react-bootstrap/Button";
import Dropdown from "../components/Charts/dropdown";

const RESERVED_FIELD = ["result", "table", "_field", "_measurement", "_start", "_stop", "_time"]

const AdminMap = (props) => {
  const [stations, setStations] = useState([]);
  const [optionSelected, setOptionSelected] = useState(null);
  const [showTable, setShowTable] = useState(false);
  const [checklistDisabled, setChecklistDisabled] = useState(true);
  const [mseed, setMseed] = useState([]);
  const [socket, setSocket] = useState(null);
  const [data, setData] = useState(null); 
  const [time, setTime] = useState(null); 
  const [reset,setReset] = useState(false);
  const [showTab,setShowTab] = useState(true);
  const [showLegend, setShowLegend] = useState(false);


  const handleClick = () => setShowTable(!showTable);

  useEffect(()=>{
      const socket = new WebSocket(`ws://${props.url}/ws`)
      console.log(props.url)
      socket.onmessage = function(e) {
        const jsonData = JSON.parse(e.data)
        let stations = {}
        Object.entries(jsonData).forEach(([key, value]) => {
          if (!RESERVED_FIELD.includes(key)) {
            const [channel, station] = key.split("_")
            let channels = stations[station] != undefined ? stations[station] : {} 
            channels[channel] = Object.values(value)
            stations[station] = channels
          }
        })
        setTime(jsonData["_time"])
        setData(stations);
      }
      socket.onclose = console.log('Socket connection closed')
      setSocket(socket)
  }, [])

  useEffect(() => {
    // if(stations.includes("GMJI")){
    //         setShowGMJI(true);
    //         setShowLegend(true);
    //  }

    if (stations.length == 0) setShowLegend(false);

   }, [stations]);

  return (
  <div>
    <div>
      <Map reset={reset} setReset={setReset} url={props.url}/>
      <div className="legend">
        <Legend />
      </div>
      <div className="performance">
        <Button variant="light" onClick={() => setShowTab(!showTab)}>
          <img src={require('../assets/list.png')}></img> 
        </Button>
      </div>
      {showTab ?
      <div className="left-panel"> 
        {/* <Checklist stateChanger={setStations} setOptionSelected={setOptionSelected} optionSelected={optionSelected} on_off={checklistDisabled}/> */}
        <MyTime />
        <div className="chart-container">
          {data != null && Object.entries(data).map(([key, value]) => {
            return (
              // <div>
                <RealtimeChart testid={key} key={key} url={props.url} json={value} time={time} stasiun={key} mseed={mseed} setMseed={setMseed}/>
                /* <div className="chart-legend">
                  <span className="bhn">-o- BHN</span><span className="bhz">-o- BHZ</span><span className="bhe">-o- BHE</span><span className="parrival">| P-Arrival</span>
                </div> */
              // </div>
          )})}
        </div> 
        {/* { showTable ? <Ptable seed={seed.value} jsonGMJI={jsonGMJI} jsonJAGI={jsonJAGI} jsonPWJI={jsonPWJI} reset={reset} setReset={setReset}/> : null} */}
        <div className="d-grid gap-2">
          <Button role='button' aria-label='parameter' variant="light" size="sm" onClick={handleClick}> 
            Show Earthquake Parameters
          </Button>
        </div>
      </div>: null}
    </div>
  </div>
  );
};
export default AdminMap;