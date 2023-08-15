from datetime import timedelta, timezone
from math import ceil
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
    status,
    UploadFile,
    BackgroundTasks,
)
from fastapi.params import Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from influxdb_client.client.flux_table import TableList
from typing import Dict, List
from influxdb_client import Point, WritePrecision
from obspy import Stream, Trace, read
from logging.config import dictConfig

from database.mongodb import mongo_client
from database.influxdb import influx_client
from stream import KafkaProducer, PREPROCESSED_TOPIC
from utils import *
from .model import *
from .websocket import ConnectionManager
from log_config import logging_config

import logging
import haversine as hs
import time
import asyncio
import pandas as pd
import io
import os

load_dotenv()
dictConfig(logging_config)

MODULE_DIR = "./rest/"
STATIC_DIR = "static/"
SIMULATE_REALTIME = True if os.getenv("SIMULATE_REALTIME") == "True" else False
MSEED_RANGE_IN_SECONDS = 30

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI()
log = logging.getLogger("rest")
app.mount("/static", StaticFiles(directory=f"{MODULE_DIR}{STATIC_DIR}"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log.info(f"{SIMULATE_REALTIME=}")

producer = KafkaProducer(PREPROCESSED_TOPIC)
manager = ConnectionManager()
_, db = mongo_client()
client = influx_client()

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


@app.get("/test")
async def test():
    query_api = client.query_api()
    now = datetime(2015, 8, 20, 15, 11, 47, tzinfo=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    first_starttime = now
    query = f"""
    from(bucket: "eews") 
        |> range(start: {(now - timedelta(seconds=60)).isoformat()}, stop: {now.isoformat()}) 
        |> filter(fn: (r) => r["_measurement"] == "seismograf") 
        |> pivot(rowKey: ["_time"], columnKey: ["channel", "station"], valueColumn: "_value")"""
    start = time.monotonic_ns()
    data: pd.DataFrame = query_api.query_data_frame(query=query)
    data2: TableList = query_api.query(query=query)
    # TODO: Update result for easier handling in frontend
    result = {}
    # log.debug(data)
    # extended_data = fill_empty_timestamp((now - timedelta(seconds=1)), now, data)
    # print(extended_data)
    log.debug(f"{(time.monotonic_ns() - start)/10**9}s")
    return data2.to_json()
    # return extended_data.to_dict()


@app.get("/")
async def get():
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        query_api = client.query_api()
        now = datetime(2015, 8, 20, 15, 12, 1, tzinfo=timezone.utc)
        if SIMULATE_REALTIME:
            now = datetime.now(tz=timezone.utc) - timedelta(
                seconds=MSEED_RANGE_IN_SECONDS
            )
        while True:
            start = time.monotonic_ns()
            query = f"""
            from(bucket: "eews") 
                |> range(start: {(now - timedelta(seconds=1)).isoformat()}, stop: {now.isoformat()}) 
                |> filter(fn: (r) => r["_measurement"] == "seismograf") 
                |> pivot(rowKey: ["_time"], columnKey: ["channel", "station"], valueColumn: "_value")"""
            data: pd.DataFrame = query_api.query_data_frame(query=query)
            extended_data = fill_empty_timestamp(
                (now - timedelta(seconds=1)), now, data
            )
            # TODO: Update result for easier handling in frontend
            result = {}
            log.debug(now)
            log.debug(data)
            json_data = extended_data.to_json()
            now += timedelta(seconds=1)
            await manager.broadcast(json_data)
            diff = (time.monotonic_ns() - start) / 10**9
            await asyncio.sleep(1 - diff)
    except Exception:
        log.warning(f"Client {websocket} has been disconnected")
        manager.disconnect(websocket)


@app.get("/station", response_model=List[StationModel])
async def list_seismometer():
    list_data = await db["station"].find().to_list(1000000000)
    return list_data


@app.get("/station/{name}", response_model=StationModel)
async def get_seismometer(name: str):
    data = await db["station"].find_one({"name": name})
    if data is not None:
        return data
    raise HTTPException(
        status_code=404, detail=f"Seismometer with name {name} not found"
    )


@app.put("/station/{name}", response_model=StationModel)
async def update_seismometer(
    name: str, background_task: BackgroundTasks, data: UpdateStationModel = Body(...)
):
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

    raise HTTPException(
        status_code=404, detail=f"Seismometer with name {name} not found"
    )


@app.post("/station", response_model=StationModel, status_code=status.HTTP_201_CREATED)
async def create_seismometer(
    background_task: BackgroundTasks, data: UpdateStationModel = Body(...)
):
    data = data.model_dump()
    if (
        existing_data := await db["station"].find_one({"name": data["name"]})
    ) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Seismometer with name {data['name']} already exists",
        )

    all_stations = await db["station"].find().to_list(1000000000)
    calculated = dict()

    data["closest_stations"] = calculate_closest_station(data, all_stations, calculated)

    new_data = await db["station"].insert_one(data)
    if (
        existing_data := await db["station"].find_one({"_id": new_data.inserted_id})
    ) is not None:
        await adjust_closest_stations()
        return existing_data


@app.delete("/station/{name}")
async def delete_seismometer(name: str, background_task: BackgroundTasks):
    delete_result = await db["station"].delete_one({"name": name})

    if delete_result.deleted_count == 1:
        await adjust_closest_stations()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(
        status_code=404, detail=f"Seismometer with name {name} not found"
    )


@app.post("/mseed", status_code=status.HTTP_201_CREATED)
async def upload_mseed(file: UploadFile, background_tasks: BackgroundTasks):
    filename = file.filename
    log.debug(f"Received mseed with name {filename}")
    contents = await file.read()
    background_tasks.add_task(save_mseed, contents, filename)
    return {"file_size": file.size, "filename": filename}


@measure_execution_time
async def adjust_closest_stations(all_stations=None):
    log.info("Adjusting closest stations")
    if not all_stations:
        all_stations = await db["station"].find().to_list(1000000000)

    calculated = dict()

    for station in all_stations:
        station["closest_stations"] = calculate_closest_station(
            station, all_stations, calculated
        )
        await db["station"].update_one({"name": station["name"]}, {"$set": station})


def calculate_closest_station(
    curr_station: List[Dict], all_stations: List[Dict], calculated: Dict = None
):
    distances = []

    for other_station in all_stations:
        if other_station["name"] == curr_station["name"]:
            continue
        distance = float("inf")
        if f"{other_station['name']}-{curr_station['name']}" in calculated:
            distance = calculated[f"{other_station['name']}-{curr_station['name']}"]
        else:
            distance = hs.haversine(
                (curr_station["x"], curr_station["y"]),
                (other_station["x"], other_station["y"]),
            )
            calculated[f"{curr_station['name']}-{other_station['name']}"] = distance
        distances.append((other_station["name"], distance))

    distances.sort(key=lambda x: x[1])
    return [i[0] for i in distances[:3]]


@measure_execution_time
def save_mseed(contents: bytes, filename: str):
    log.info("Saving mseed on the background")
    st = read(io.BytesIO(contents))

    log.debug(f"Stream {st}")

    if len(st) > 0:
        first_starttime = min([trace.stats["starttime"] for trace in st])
        first_endtime = min([trace.stats["endtime"] for trace in st])

        processed = process_data(st)
        produce_windowed_data(processed, first_starttime, first_endtime)
        save_to_influx(st)


@measure_execution_time
def produce_windowed_data(stream: Stream, first_starttime, first_endtime):
    dt = UTCDateTime(first_starttime)

    while dt + 8 <= first_endtime:
        windowed_data = [None, None, None]
        trimmed = stream.slice(dt, dt + 8, keep_empty_traces=True)
        if len(trimmed) > 0:
            event = {
                "station": trimmed[0].stats["station"],
            }
            for detail in trimmed:
                if detail.stats["channel"] == "BHE":
                    windowed_data[0] = detail.data
                    event["BHE"] = {
                        "starttime": str(detail.stats.starttime),
                        "endtime": str(detail.stats.endtime),
                        "data": detail.data.tolist(),
                    }
                elif detail.stats["channel"] == "BHN":
                    windowed_data[1] = detail.data
                    event["BHN"] = {
                        "starttime": str(detail.stats.starttime),
                        "endtime": str(detail.stats.endtime),
                        "data": detail.data.tolist(),
                    }
                elif detail.stats["channel"] == "BHZ":
                    windowed_data[2] = detail.data
                    event["BHZ"] = {
                        "starttime": str(detail.stats.starttime),
                        "endtime": str(detail.stats.endtime),
                        "data": detail.data.tolist(),
                    }
            producer.produce_message(event, event["station"])
        dt += 0.04
    return dt


@measure_execution_time
def save_to_influx(stream: Stream):
    trace: Trace
    records = []
    for trace in stream:
        starttime: datetime = UTCDateTime(trace.stats.starttime).datetime
        delta = 1 / int(trace.stats.sampling_rate)
        channel = trace.stats.channel
        station = trace.stats.station

        for data_point in trace.data:
            point = (
                Point("seismograf")
                .time(starttime, write_precision=WritePrecision.MS)
                .tag("channel", channel)
                .tag("station", station)
                .field("data", data_point)
            )
            records.append(point)
            starttime += timedelta(seconds=delta)

    with client.write_api() as writer:
        log.info(f"Start batch save of {len(records)} data to InfluxDB")
        writer.write(bucket="eews", record=records)


@measure_execution_time
def process_data(stream: Stream):
    mseed_data = stream
    new_stream = Stream()
    detail: Trace
    for detail in mseed_data:
        trace = detail.copy()
        fs = detail.stats.sampling_rate
        lowcut = 1.0
        highcut = 5.0
        order = 5
        data_before = detail.data
        data_processed = butter_bandpass_filter(data_before, lowcut, highcut, fs, order)
        trace.data = data_processed
        trace.interpolate(25)
        trace.stats["delta"] = 1 / 25
        trace.stats["sampling_rate"] = 25
        new_stream.append(trace)
    return new_stream
