import React, {useRef,useEffect,useState} from "react";
import '../style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { divIcon } from 'leaflet';
import L from 'leaflet'


const Map = (props) => {
  const [found,setFound] = useState(false);
  const [coord,setCoord] = useState(new L.circle());
  const customMarkerIconPWJI = divIcon({
    html: '<div class="marker-container"><img class="my-div-img" src="https://i.ibb.co/Ms1qfS3/red-marker.png"/><span class="my-div-span">PWJI</span></div>',
    iconAnchor: [25, 41],
    popupAnchor: [-11, -40]
  }); 

  const customMarkerIconGMJI = divIcon({
    html: '<div class="marker-container"><img class="my-div-img" src="https://i.ibb.co/Ms1qfS3/red-marker.png"/><span class="my-div-span">GMJI</span></div>',
    iconAnchor: [25, 41],
    popupAnchor: [-11, -40]
  }); 
  // https://unpkg.com/leaflet@1.9.1/dist/images/marker-icon-2x.png
  const customMarkerIconJAGI = divIcon({
    html: '<div class="marker-container"><img class="my-div-img" src="https://i.ibb.co/Ms1qfS3/red-marker.png"/><span class="my-div-span">JAGI</span></div>',
    iconAnchor: [25, 41],
    popupAnchor: [-11, -40]
  }); 
  const map = useRef();
  const GMJIpos = [-8.0219, 111.8];
  const PWJIpos = [-8.2732, 113.4441];
  const JAGIpos = [-8.47, 114.15];
  const mapRef = useRef()
  let lst = useRef([]);
  useEffect(() =>{
    mapRef.current = L.map('map', {
      layers: [
       L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}")
      ],
      zoomControl: false
      
    })
    .setView(GMJIpos, 6.5)

    L.control.zoom({
      position: 'topright'
  }).addTo(mapRef.current);

  const popupContentGMJI = "GMJI <br />Station Gumukmas, Java <br />"
  const popupContentPWJI = "PWJI <br />Station Pagerwojo, Java <br />"
  const popupContentJAGI = "JAGI <br />Station Jajag, Java <br />"

  L.marker(GMJIpos, {icon: customMarkerIconGMJI}).addTo(mapRef.current).bindPopup(popupContentGMJI);
  L.marker(PWJIpos, {icon: customMarkerIconPWJI}).addTo(mapRef.current).bindPopup(popupContentPWJI);
  L.marker(JAGIpos, {icon: customMarkerIconJAGI}).addTo(mapRef.current).bindPopup(popupContentJAGI);

  
  }, []);

  useEffect(()=>{
    
    if(props.jsonGMJI!==null && props.jsonPWJI!==null && props.jsonJAGI!==null){
      if(props.jsonGMJI[99].data_prediction.lat===null && props.jsonJAGI[99].data_prediction.lat===null && props.jsonPWJI[99].data_prediction.lat===null){
        setFound(false);
        mapRef.current.removeLayer(coord);
      }
      else{
        if(props.jsonGMJI[99].data_prediction.lat!==null){
          setSource('GMJI',[props.jsonGMJI[99].data_prediction.lat,props.jsonGMJI[99].data_prediction.long],props.jsonGMJI[99].data_prediction.magnitude,props.jsonGMJI[99].data_prediction.depth)
        } 
        if(props.jsonPWJI[99].data_prediction.lat!==null){
          setSource('PWJI',[props.jsonPWJI[99].data_prediction.lat,props.jsonPWJI[99].data_prediction.long],props.jsonPWJI[99].data_prediction.magnitude,props.jsonPWJI[99].data_prediction.depth)
        }
        if(props.jsonJAGI[99].data_prediction.lat!==null){
          setSource('JAGI',[props.jsonJAGI[99].data_prediction.lat,props.jsonJAGI[99].data_prediction.long],props.jsonJAGI[99].data_prediction.magnitude,props.jsonJAGI[99].data_prediction.depth) 
        }
      }
    }
    
    
    
    function setSource(stasiun,koord, mag, depth){
      if(found===false){
        var magnitude = Math.round((mag + Number.EPSILON) * 100) / 100;
        var lat = Math.round((koord[0] + Number.EPSILON) * 100) / 100;
        var long= Math.round((koord[1] + Number.EPSILON) * 100) / 100;
        var depths = Math.round((depth + Number.EPSILON) * 100) / 100;
        let text = 'Koordinat: '+lat+','+long+' Magnitude; '+magnitude+' Kedalaman: '+depths+' KM'+' Stasiun Pendeteksi: '+stasiun;
        var circle = new L.circle (koord, 30000, {color: "red", opacity:.5}).bindPopup(text)
        setCoord(circle);
        mapRef.current.addLayer(circle);
        mapRef.current.setView(koord,7.5);
        setFound(true);
      }
    }
  },[props])
      return (
        <div id="map"></div>
      );
  }
export default Map;