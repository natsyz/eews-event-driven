import React, { useEffect, useState } from "react";
import 'reactjs-popup/dist/index.css';
import "./style.css"
function Ptable(props) {
  const [magnitude,setMagnitude] = useState("-");
  const [asal,setAsal] = useState("-");
  const [kedalaman,setKedalaman] = useState("-");
  const [sumberLoc,setSumberLoc] = useState("-");
  const [recieverID,setRecieverID] = useState("-");
  const [found,setFound] = useState(false);

  useEffect(()=>{
    if(props.reset){
      props.setReset(false);
    }
    if(props.jsonGMJI!==null && props.jsonPWJI!==null && props.jsonJAGI!==null){
      if(props.jsonGMJI[99].p_Arrival==null){
        setFound(false);
        setSumberLoc('-');
        setKedalaman('-');
        setMagnitude('-');
        setRecieverID('-');
        setAsal('-');
      }
      if(props.jsonGMJI[99].data_prediction.lat!==null && props.jsonGMJI[99].data_prediction.lat!==null){
        setSource((props.jsonGMJI[99].data_prediction.lat).toString().slice(0,5),(props.jsonGMJI[99].data_prediction.long).toString().slice(0,5),props.jsonGMJI[99].data_prediction.magnitude,props.jsonGMJI[99].data_prediction.depth,'GMJI',props.jsonGMJI[99].time)
      } 
      if(props.jsonPWJI[99].data_prediction.lat!==null && props.jsonPWJI[99].data_prediction.lat!==null){
        setSource((props.jsonPWJI[99].data_prediction.lat).toString().slice(0,5),(props.jsonPWJI[99].data_prediction.long).toString().slice(0,5),props.jsonPWJI[99].data_prediction.magnitude,props.jsonPWJI[99].data_prediction.depth,'PWJI',props.jsonGMJI[99].time)
      } 
      if(props.jsonJAGI[99].data_prediction.lat!==null && props.jsonJAGI[99].data_prediction.lat!==null){
        setSource((props.jsonJAGI[99].data_prediction.lat).toString().slice(0,5),(props.jsonJAGI[99].data_prediction.long).toString().slice(0,5),props.jsonJAGI[99].data_prediction.magnitude,props.jsonJAGI[99].data_prediction.depth,'JAGI',props.jsonGMJI[99].time)
      }
    }
    
    function setSource(lat,long, mag, depth, stasiun, time){
      if(found===false){
        setSumberLoc(lat+','+long);
        setKedalaman(depth);
        setMagnitude(mag);
        setRecieverID(stasiun);
        var tanggal = props.seed.slice(6,8);
        var bulan = props.seed.slice(4,6);
        var tahun = props.seed.slice(0,4);
        var jam = props.seed.slice(9,11);
        setAsal(jam+':'+time+' '+tanggal+'/'+bulan+'/'+tahun);
        setFound(true);
      }
    }
  },[props])
    
  return (
    <div className='parameter-tab'>
      <div className="parameter-title">
        <h>Parameter Gempa Bumi</h>
      </div>
      <div className='parameter-container'>
        <div className="parameter">
          <div className="parameter-p">
            <p>P-Arrival Time</p>
          </div>
          <div className="parameter-box">
            <p>{asal}</p>
          </div>
        </div>
        <div className="parameter">
          <div className="parameter-p">
            <p>Magnitudo</p>
          </div>
          <div className="parameter-box">
            <p>{(magnitude).toString().slice(0,3)}</p>
          </div>
        </div>
        <div className="parameter">
          <div className="parameter-p">
            <p>Kedalaman</p>
          </div>
          <div className="parameter-box">
            <p>{(kedalaman).toString().slice(0,5)} KM</p>
          </div>
        </div>
        <div className="parameter">
          <div className="parameter-p">
            <p>Reciever ID</p>
          </div>
          <div className="parameter-box">
            <p>{recieverID}</p>
          </div>
        </div>
        <div className="parameter">
          <div className="parameter-p">
            <p>Source Location</p>
          </div>
          <div className="parameter-box">
            <p>{sumberLoc}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
export default Ptable;