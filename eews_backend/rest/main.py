from datetime import timedelta
from math import ceil
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect,  status, UploadFile, BackgroundTasks
from fastapi.params import Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List
from influxdb_client import Point, WritePrecision
from obspy import read

from database.mongodb import *
from database.influxdb import *
from stream_processing.schema import *
from stream_processing.kafka import KafkaProducer, BOOTSTRAP_SERVER
from stream_processing.topics import PREPROCESSED_TOPIC
from utils import *
from .model import *
from .websocket import ConnectionManager

import faust
import haversine as hs
import time
import asyncio
import pandas as pd

MODULE_DIR = "./rest/"
STATIC_DIR = "static"

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory=f"{MODULE_DIR}{STATIC_DIR}"), name="static")

producer = KafkaProducer(PREPROCESSED_TOPIC)
manager = ConnectionManager()

HTML = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                if (window != undefined) {
                    window.console.log(JSON.parse(event.data))
                }
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(HTML)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        query_api = client.query_api()
        while True:
            await asyncio.sleep(1)
            now = datetime.now()
            now = datetime(2015,8,20,15,12,1)
            data: pd.DataFrame = query_api.query_data_frame(
                query=f'from(bucket: "eews") |> range(start: {(now - timedelta(seconds=1)).isoformat()}Z, stop: {now.isoformat()}Z) |> filter(fn: (r) => r["_measurement"] == "seismograf") |> pivot(rowKey: ["_time"], columnKey: ["channel", "station"], valueColumn: "_value")'
            )
            data = data.fillna(0)
            json_data = data.to_json()
            await manager.broadcast(json_data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/station", response_model=List[StationModel])
async def list_seismometer():
    list_data = await db["station"].find().to_list(1000000000)
    print(list_data)
    return list_data

@app.get("/station/{name}", response_model=StationModel)
async def get_seismometer(name: str):
    data = await db["station"].find_one({"name": name})
    if data is not None:
        return data
    raise HTTPException(status_code=404, detail=f"Seismometer with name {name} not found")

@app.put("/station/{name}", response_model=StationModel)
async def update_seismometer(name: str, background_task: BackgroundTasks, data: UpdateStationModel = Body(...)):
    data = data.model_dump()
    
    if len(data) >= 1:
        update_result = await db["station"].update_one({"name": name}, {"$set": data})

        if update_result.modified_count == 1:
            if (
                updated_data := await db["station"].find_one({"name": name})
            ) is not None:
                background_task.add_task(adjust_closest_stations)
                return updated_data

    if (existing_data := await db["station"].find_one({"name": name})) is not None:
        await adjust_closest_stations()
        return existing_data

    raise HTTPException(status_code=404, detail=f"Seismometer with name {name} not found")

@app.post("/station", response_model=StationModel, status_code=status.HTTP_201_CREATED)
async def create_seismometer(background_task: BackgroundTasks, data: UpdateStationModel = Body(...)):
    data = data.model_dump()
    if (existing_data := await db["station"].find_one({"name": data["name"]})) is not None:
        raise HTTPException(status_code=400, detail=f"Seismometer with name {data['name']} already exists")
    
    all_stations = await db["station"].find().to_list(1000000000)
    calculated = dict()
    
    data["closest_stations"] = calculate_closest_station(data, all_stations, calculated)
    
    new_data = await db["station"].insert_one(data)
    if (existing_data := await db["station"].find_one({"_id": new_data.inserted_id})) is not None:
        await adjust_closest_stations()
        return existing_data

@app.delete("/station/{name}")
async def delete_seismometer(name: str, background_task: BackgroundTasks):
    delete_result = await db["station"].delete_one({"name": name})

    if delete_result.deleted_count == 1:
        await adjust_closest_stations()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Seismometer with name {name} not found")

@app.post("/mseed", status_code=status.HTTP_201_CREATED)
async def upload_mseed(file: UploadFile, background_tasks: BackgroundTasks):
    filename = file.filename
    contents = await file.read()
    background_tasks.add_task(save_mseed, contents, filename)
    return {"file_size": file.size, "filename": filename}

@measure_execution_time
async def adjust_closest_stations(all_stations = None):
    print("adjusting closest stations")
    if not all_stations:
        all_stations = await db["station"].find().to_list(1000000000)

    calculated = dict()
    
    for station in all_stations:
        station["closest_stations"] = calculate_closest_station(station, all_stations, calculated)
        await db["station"].update_one({"name": station["name"]}, {"$set": station})
        
def calculate_closest_station(curr_station, all_stations, calculated = None):
    distances = []
    
    for other_station in all_stations:
        if other_station['name'] == curr_station["name"]:
            continue
        distance = float("inf")
        if f"{other_station['name']}-{curr_station['name']}" in calculated:
            distance = calculated[f"{other_station['name']}-{curr_station['name']}"]
        else:
            distance = hs.haversine((curr_station['x'], curr_station['y']), (other_station['x'], other_station['y']))
            calculated[f"{curr_station['name']}-{other_station['name']}"] = distance
        distances.append((other_station['name'], distance))
    
    distances.sort(key=lambda x: x[1])
    return [i[0] for i in distances[:3]]

@measure_execution_time
def save_mseed(contents: bytes, filename: str):
    print(f"{time.time_ns()} | saving mseed to db")
    filepath = f"{STATIC_DIR}{filename}"
    with open(filepath, "wb") as f:
        f.write(contents)
        
    records = []
    events = []
    traces = process_data(filepath)
    for mseed_data in traces:
        starttime = UTCDateTime(mseed_data['starttime']).datetime
        endtime = UTCDateTime(mseed_data['endtime']).datetime
        delta = float(mseed_data['delta'])
        channel = mseed_data["channel"]
        station = mseed_data["station"]
        start = time.monotonic_ns()
        
        for data_point in mseed_data['data_interpolated']:
            point = Point("seismograf").time(starttime, write_precision=WritePrecision.MS).tag("channel", channel).tag("station", station).field("data", data_point)
            records.append(point)      
            event = {
                "station": station,
                "channel": channel,
                "time": str(starttime),
                "data": data_point
            }
            events.append(event)
            starttime += timedelta(seconds=delta)
    
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        with client.write_api() as writer:
            writer.write(bucket="eews", record=records)
    
    for i in range(len(events)):    
        producer.produce_message(events[i])
    
    print(f"finished process mseed with {len(records)} data for {(time.monotonic_ns() - start) / 10**9}s with rate of {len(records)/((time.monotonic_ns() - start) / 10**9)}")

@measure_execution_time
def process_data(mseed_filename):
    mseed_data = read(mseed_filename)
    traces = []
    for detail in mseed_data:
        preprocessed = {}
        fs = detail.stats.sampling_rate
        lowcut = 1.0
        highcut = 5.0
        order = 5
        preprocessed['network'] = detail.stats.network
        preprocessed['station'] = detail.stats.station
        preprocessed['channel'] = detail.stats.channel
        preprocessed['location'] = detail.stats.location
        preprocessed['starttime'] = str(detail.stats.starttime)
        preprocessed['endtime'] = str(detail.stats.endtime)
        preprocessed['delta'] = detail.stats.delta
        preprocessed['npts'] = detail.stats.npts
        preprocessed['calib'] = detail.stats.calib
        preprocessed['data'] = detail.data
        data_before = detail.data
        data_processed = butter_bandpass_filter(data_before, lowcut, highcut, fs, order)
        data_to = list(data_processed)
        data_to = letInterpolate(data_to, int(ceil(len(data_to)*25/detail.stats.sampling_rate)))
        preprocessed['sampling_rate'] = 25.0
        preprocessed['data_interpolated'] = data_to
        traces.append(preprocessed)
    return traces
 