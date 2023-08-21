import React, {useRef,useEffect,useState} from "react";
import '../style.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { divIcon } from 'leaflet';
import L from 'leaflet'


const Map = (props) => {
  const [found,setFound] = useState(false);
  const [coord,setCoord] = useState(new L.circle());
  const [stations, setStations] = useState([])
  const map = useRef();
  const mapRef = useRef();
  let lst = useRef([]);

  function customMarkerIcon(station, iconAnchor = [25, 41], popupAnchor = [-11, -40]) {
    return divIcon({
      html: `<div class="marker-container"><img class="my-div-img" src="https://i.ibb.co/Ms1qfS3/red-marker.png"/><span class="my-div-span">${station}</span></div>`,
      iconAnchor: iconAnchor,
      popupAnchor: popupAnchor
    })
  }

  function popupContent(station, description) {
    return `${station} <br /> ${description} <br />`
  }
  
  useEffect(() =>{
  async function getStations() {
    const response = await fetch(`http://${props.url}/station`)
    const jsonData = await response.json()
    setStations(jsonData)
    jsonData.forEach(element => {
      L.marker([element["location"]["coordinates"]["1"], element["location"]["coordinates"]["0"]], {icon: customMarkerIcon(element["name"])}).addTo(mapRef.current).bindPopup(popupContent(element["name"], element["description"]));
    });
  }
  if (mapRef.current == undefined) {
    mapRef.current = L.map('map', {
      layers: [
       L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}")
      ],
      zoomControl: false
      
    })
    .setView([-8.0219, 111.8], 6.5)
  
    L.control.zoom({
        position: 'topright'
    }).addTo(mapRef.current);
  }
  getStations()
  
  }, []);

  useEffect(()=>{
    
    if(props.jsonGMJI !== undefined && props.jsonPWJI !== undefined && props.jsonJAGI !== undefined){
      if(props.jsonGMJI[99].data_prediction.lat===undefined && props.jsonJAGI[99].data_prediction.lat===undefined && props.jsonPWJI[99].data_prediction.lat===undefined){
        setFound(false);
        mapRef.current.removeLayer(coord);
      }
      else {
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
    
    function setSource(stasiun, koord, mag, depth){
      if(found===false){
        var magnitude = Math.round((mag + Number.EPSILON) * 100) / 100;
        var lat = Math.round((koord[0] + Number.EPSILON) * 100) / 100;
        var long= Math.round((koord[1] + Number.EPSILON) * 100) / 100;
        var depths = Math.round((depth + Number.EPSILON) * 100) / 100;
        let text = `Koordinat: ${lat},${long} Magnitude: ${magnitude} Kedalaman: ${depths} KM Stasiun Pendeteksi: ${stasiun}`;
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