import React,{useEffect, useState, useRef} from "react";
import "chartjs-plugin-streaming";
import '../App.css';
import Dropdown from "../components/Charts/dropdown";
import 'bootstrap/dist/css/bootstrap.min.css';
import Map from "../components/Map/Map2"
import Legend from "../components/Legend/Legend-Button";
import MyTime from "../components/Timer/time"
import Button from "react-bootstrap/Button";

const UserMap = (props) => {
  const [seed, setSeed] = useState('');
  const [mseedSelected, setMseedSelected] = useState(null);
  const [mseed, setMseed] = useState([]);
  const [jsonGMJI,setJsonGMJI] = useState([]);
  const [jsonPWJI,setJsonPWJI] = useState(null);
  const [jsonJAGI,setJsonJAGI] = useState(null);
  const [sockGMJI,setSockGMJI] = useState(null);
  const [sockPWJI,setSockPWJI] = useState(null);
  const [sockJAGI,setSockJAGI] = useState(null);
  const [magnitude,setMagnitude] = useState("-");
  const [asal,setAsal] = useState("-");
  const [kedalaman,setKedalaman] = useState("-");
  const [sumberLoc,setSumberLoc] = useState("-");
  const [recieverID,setRecieverID] = useState("-");
  const [countdown,setCountdown] = useState('-');
  const [found,setFound] = useState(false);
  const [start,setStart] = useState(false);
  const [reset,setReset] = useState(false);
  const [showTab,setShowTab] = useState(true);
  const [name,setName] = useState(null);
  const [test,setTest] = useState(false);

  const prevSeed = useRef("");
  const changeSeed = (i) => {
    setSeed(i);
    setReset(true);
    setTest(true);
    prevSeed.current = i;
    mseed.forEach(func => func(i.value));
    if(i!==prevSeed){
      sockGMJI.close();
      sockJAGI.close();
      sockPWJI.close();
    }
    
  }


  useEffect(()=>{
    if(seed!==null){
      const socketGMJI = new WebSocket("wss://"+props.url+"/get_gmji_data/"+seed.value+'/')
      socketGMJI.onmessage = function(e){
        setJsonGMJI(JSON.parse(e.data));
      }
      socketGMJI.onclose = console.log('GMJI User connection closed')
      setSockGMJI(socketGMJI);
      const socketJAGI = new WebSocket("wss://"+props.url+"/get_jagi_data/"+seed.value+'/') 
      socketJAGI.onmessage = function(e){
        setJsonJAGI(JSON.parse(e.data));
      }
      socketJAGI.onclose = console.log('JAGI User connection closed')
      setSockJAGI(socketJAGI);
      const socketPWJI = new WebSocket("wss://"+props.url+"/get_pwji_data/"+seed.value+'/') 
      socketPWJI.onmessage = function(e){
        setJsonPWJI(JSON.parse(e.data));
      }
      socketPWJI.onclose = console.log('PWJI User connection closed')
      setSockPWJI(socketPWJI);
    }
    
    
  },[seed])

  useEffect(()=>{
    if(jsonGMJI!==null && jsonPWJI!==null && jsonJAGI!==null){
      setName(jsonGMJI[99].mseed_name);
      if(jsonGMJI[99].p_Arrival==null){
        setFound(false);
        setSumberLoc('-');
        setKedalaman('-');
        setMagnitude('-');
        setRecieverID('-');
        setAsal('-');
        setStart(false);
        setCountdown('-');
      }
      if(jsonGMJI[99].data_prediction.lat!==null && jsonGMJI[99].data_prediction.lat!==null){
        setSource((jsonGMJI[99].data_prediction.lat).toString().slice(0,5),(jsonGMJI[99].data_prediction.long).toString().slice(0,5),jsonGMJI[99].data_prediction.magnitude,jsonGMJI[99].data_prediction.depth,'GMJI',jsonGMJI[99].time, 24)
      } 
      if(jsonPWJI[99].data_prediction.lat!==null && jsonPWJI[99].data_prediction.lat!==null){
        setSource((jsonPWJI[99].data_prediction.lat).toString().slice(0,5),(jsonPWJI[99].data_prediction.long).toString().slice(0,5),jsonPWJI[99].data_prediction.magnitude,jsonPWJI[99].data_prediction.depth,'PWJI',jsonGMJI[99].time, 24)
      } 
      if(jsonJAGI[99].data_prediction.lat!==null && jsonJAGI[99].data_prediction.lat!==null){
        setSource((jsonJAGI[99].data_prediction.lat).toString().slice(0,5),(jsonJAGI[99].data_prediction.long).toString().slice(0,5),jsonJAGI[99].data_prediction.magnitude,jsonJAGI[99].data_prediction.depth,'JAGI',jsonGMJI[99].time, 24)
      }
    }
    
    function setSource(lat,long, mag, depth, stasiun, time, count){
      if(found===false){
        setSumberLoc(lat+','+long);
        setKedalaman(depth);
        setMagnitude(mag);
        setRecieverID(stasiun);
        var tanggal = seed.value.slice(6,8);
        var bulan = seed.value.slice(4,6);
        var tahun = seed.value.slice(0,4);
        var jam = seed.value.slice(9,11);
        setAsal(jam+':'+time+' '+tanggal+'/'+bulan+'/'+tahun);
        setStart(true);
        setCountdown(24);
        setFound(true);
      }
    }
    
  },[jsonGMJI,jsonJAGI,jsonPWJI])

  useEffect(()=>{
    if(start){
      countdown > 0 && setTimeout(() => setCountdown(countdown - 1), 1000);
    }
  },[countdown])

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
            <div className="left-panel-user"> 
              <Dropdown stateChanger={changeSeed} setMseedSelected={setMseedSelected} mseedSelected={mseedSelected}/>
              <MyTime />
              <div className="head">Informasi Gempa Bumi</div>
              {test ? <div  data-testid = {name} ></div> : null}
              <div className="widget-container">
                <div className="grid-item">
                  <div className="grid-col">
                    <div className="grid-text">
                      <h6>Magnitude</h6>
                      <b>{(magnitude).toString().slice(0,3)}</b>
                    </div>
                    <img src={require('../assets/magnitude-35.png')}></img>
                  </div>
                </div>
                <div className="grid-item">
                  <div className="grid-col">
                    <div className="grid-text">
                      <h6>Waktu Asal</h6>
                      <b>{asal}</b>
                    </div>
                    <img src={require('../assets/location-history-time-icon.png')}></img>
                  </div>
                </div>
                <div className="grid-item">
                  <div className="grid-col">
                    <div className="grid-text">
                      <h6>Kedalaman</h6>
                      <b>{(kedalaman).toString().slice(0,5)} KM</b>
                    </div>
                    <img src={require('../assets/depth35.png')}></img>
                  </div>
                </div>
                <div className="grid-item">
                  <div className="grid-col">
                    <div className="grid-text">
                      <h6>Lokasi Sumber</h6>
                      <b>{sumberLoc}</b>
                    </div>
                    <img src={require('../assets/search.png')}></img>
                  </div>
                </div>
                <div className="grid-item">
                  <div className="grid-col">
                    <div className="grid-text">
                      <h6>Reciever</h6>
                      <b>{recieverID}</b>
                    </div>
                    <img src={require('../assets/stasiun.png')}></img>
                  </div>
                </div>
                <div className="grid-item">
                  <div className="grid-col">
                    <div className="grid-text">
                      <h6>Countdown</h6>
                      <b>{countdown}</b>
                    </div>
                    <img src={require('../assets/stopwatch.png')}></img>
                  </div>
                </div>
              </div>
              <div className="area-container">
                <div className="head">Area Terpengaruhi</div>
                <div className="grid-item-area">
                  <div className="area">
                    <img src={require('../assets/stasiun.png')}></img>
                    <div className="area-text">
                      <h6>Jawa Timur</h6>
                    </div>
                  </div>
                </div>
                <div className="grid-item-area">
                  <div className="area">
                    <img src={require('../assets/stasiun.png')}></img>
                    <div className="area-text">
                      <h6>Yogyakarta</h6>
                    </div>
                  </div>
                </div>
                <div className="grid-item-area">
                  <div className="area">
                    <img src={require('../assets/stasiun.png')}></img>
                    <div className="area-text">
                      <h6>Nusa Tenggara Barat</h6>
                    </div>
                  </div>
                </div>
              </div>
            </div> : null}
          </div>
        </div>
        );
};

export default UserMap;