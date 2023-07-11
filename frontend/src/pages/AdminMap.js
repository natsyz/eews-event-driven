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


const AdminMap = (props) => {
  const [seed, setSeed] = useState('');
  const [stations, setStations] = useState([]);
  const [optionSelected, setOptionSelected] = useState(null);
  const [mseedSelected, setMseedSelected] = useState(null);
  const [showTable, setShowTable] = useState(false);
  const [checklistDisabled, setChecklistDisabled] = useState(true);
  const [mseed, setMseed] = useState([]);
  const [jsonGMJI,setJsonGMJI] = useState([]);
  const [jsonPWJI,setJsonPWJI] = useState(null);
  const [jsonJAGI,setJsonJAGI] = useState(null);
  const [sockGMJI,setSockGMJI] = useState(null);
  const [sockPWJI,setSockPWJI] = useState(null);
  const [sockJAGI,setSockJAGI] = useState(null);
  const [showGMJI,setShowGMJI] = useState(false);
  const [showJAGI,setShowJAGI] = useState(false);
  const [showPWJI,setShowPWJI] = useState(false);
  const [reset,setReset] = useState(false);
  const [showTab,setShowTab] = useState(true);
  const [showLegend, setShowLegend] = useState(false);
  const prevSeed = useRef("");

  const changeSeed = (i) => {
      setSeed(i);
      setReset(true);
      prevSeed.current = i;
      mseed.forEach(func => func(i.value));
      if(i!==prevSeed){
        sockGMJI.close();
        sockJAGI.close();
        sockPWJI.close();
    }
  }

  const handleClick = () => setShowTable(!showTable);

  useEffect(()=>{
    if(seed!==null){
      const socketGMJI = new WebSocket("ws://"+props.url+"/get_gmji_data/"+seed.value+'/') 
      socketGMJI.onmessage = function(e){
        setJsonGMJI(JSON.parse(e.data));
      }
      socketGMJI.onclose = console.log('GMJI connection closed')
      setSockGMJI(socketGMJI);
      const socketJAGI = new WebSocket("ws://"+props.url+"/get_jagi_data/"+seed.value+'/'); 
      socketJAGI.onmessage = function(e){
        setJsonJAGI(JSON.parse(e.data));
      }
      socketJAGI.onclose = console.log('JAGI connection closed')
      setSockJAGI(socketJAGI);
      const socketPWJI = new WebSocket("ws://"+props.url+"/get_pwji_data/"+seed.value+'/') 
      socketPWJI.onmessage = function(e){
        setJsonPWJI(JSON.parse(e.data));
      }
      socketPWJI.onclose = console.log('PWJI connection closed')
      setSockPWJI(socketPWJI);
    }
    
  },[seed])

  useEffect(() => {
    if(stations.includes("GMJI")){
            setShowGMJI(true);
            setShowLegend(true);
     }
    else{
      setShowGMJI(false);
    }
    if(stations.includes("PWJI")){
            setShowPWJI(true);
            setShowLegend(true);
    }
    else{
      setShowPWJI(false);
    }
    if(stations.includes("JAGI")){
            setShowJAGI(true);
            setShowLegend(true);
    }
    else{
      setShowJAGI(false);
    }

    if(stations.length==0) setShowLegend(false);

   }, [stations]);

        return (
        <div>
          <div>
            <Map jsonGMJI={jsonGMJI} jsonJAGI={jsonJAGI} jsonPWJI={jsonPWJI} reset={reset} setReset={setReset}/>
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
              <Dropdown stateChanger={changeSeed} setMseedSelected={setMseedSelected} mseedSelected={mseedSelected}/>
              <Checklist stateChanger={setStations} setOptionSelected={setOptionSelected} optionSelected={optionSelected} on_off={checklistDisabled}/>
              <MyTime />
              <div className="chart-container">
                { showGMJI ? <RealtimeChart testid="GMJI" key={0} url={seed.value} json={jsonGMJI} stasiun={"GMJI"} mseed={mseed} setMseed={setMseed}/> : null }
                { showJAGI ? <RealtimeChart testid="JAGI" key={1} url={seed.value} json={jsonJAGI} stasiun={"JAGI"} mseed={mseed} setMseed={setMseed}/> : null }
                { showPWJI ? <RealtimeChart testid="PWJI" key={2} url={seed.value} json={jsonPWJI} stasiun={"PWJI"} mseed={mseed} setMseed={setMseed}/> : null }
                { showLegend ? <div className="chart-legend"><span className="bhn">-o- BHN</span><span className="bhz">-o- BHZ</span><span className="bhe">-o- BHE</span><span className="parrival">| P-Arrival</span></div> : null}
              </div> 
              { showTable ? <Ptable seed={seed.value} jsonGMJI={jsonGMJI} jsonJAGI={jsonJAGI} jsonPWJI={jsonPWJI} reset={reset} setReset={setReset}/> : null}
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