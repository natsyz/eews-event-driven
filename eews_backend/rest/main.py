from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect,  status, UploadFile, BackgroundTasks
from dotenv import load_dotenv
from fastapi.params import Body
from fastapi.responses import HTMLResponse
from model import *
from database import *
from typing import List
from websocket import ConnectionManager
# from stream import *
from obspy import read
# from schema import *
# from eews_backend.stream_processing.schema import *
import os
import pathlib
import time
import faust

STATIC_DIR = "./static/"

load_dotenv()

app = FastAPI()
manager = ConnectionManager()

html = """
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

RAW_TOPIC = 'raw'
PREPROCESSED_TOPIC = 'preprocessed'
PREDICTION_TOPIC = 'prediction'

BOOTSTRAP_SERVER = os.getenv("BOOTSTRAP_SERVER")
if not BOOTSTRAP_SERVER:
    raise Exception("BOOTSTRAP_SERVER is required")

APP_NAME = "rest-stream"
stream = faust.App(APP_NAME, broker=BOOTSTRAP_SERVER)
# raw_topic = stream.topic(topics.RAW_TOPIC, value_type=schema.RawValue)

test_topic = stream.topic("test", partitions=8)

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Received websocket message says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/seismometer", response_model=List[SeismometerModel])
async def list_seismometer():
    list_data = await db["seismometer"].find().to_list(1000000000)
    return list_data

@stream.agent(test_topic)
async def test_listen(data):
    async for key, value in data.items():
        print("RECEIVED MESSAGE", key, value)
        print(manager.active_connections)
        await manager.broadcast(f"Received message from kafka: {value}")

@app.get("/seismometer/{name}", response_model=SeismometerModel)
async def get_seismometer(name: str):
    data = await db["seismometer"].find_one({"name": name})
    if data is not None:
        return data
    raise HTTPException(status_code=404, detail=f"Seismometer with name {name} not found")

@app.put("/seismometer/{name}", response_model=SeismometerModel)
async def update_seismometer(name: str, data: SeismometerModel = Body(...)):
    data = data.model_dump()
    
    if len(data) >= 1:
        update_result = await db["seismometer"].update_one({"name": name}, {"$set": data})

        if update_result.modified_count == 1:
            if (
                updated_data := await db["seismometer"].find_one({"name": name})
            ) is not None:
                return updated_data

    if (existing_data := await db["seismometer"].find_one({"name": name})) is not None:
        return existing_data

    raise HTTPException(status_code=404, detail=f"Seismometer with name {name} not found")

@app.post("/seismometer", response_model=SeismometerModel, status_code=status.HTTP_201_CREATED)
async def create_seismometer(data: SeismometerModel = Body(...)):
    data = data.model_dump()
    if (existing_data := await db["seismometer"].find_one({"name": data["name"]})) is not None:
        raise HTTPException(status_code=400, detail=f"Seismometer with name {data['name']} already exists")
    
    new_data = await db["seismometer"].insert_one(data)
    if (existing_data := await db["seismometer"].find_one({"_id": new_data.inserted_id})) is not None:
        return existing_data

@app.delete("/seismometer/{name}")
async def delete_seismometer(name: str):
    delete_result = await db["seismometer"].delete_one({"name": name})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Seismometer with name {name} not found")


# @app.post("/mseed", response_model=MSeed, status_code=status.HTTP_201_CREATED)
# async def upload_mseed(file: UploadFile, background_tasks: BackgroundTasks):
#     filename = file.filename
#     background_tasks.add_task(_save_mseed, file, filename)
#     return {"file_size": len(file)}

# async def _save_mseed(file: UploadFile, filename: str):
#     contents = await file.read()
#     with open(STATIC_DIR + file.filename, "w") as f:
#         f.write(contents)
#     mseed = read(contents)
#     raw_db["mseed"].insert_one()
#     await raw_topic.send(value=RawValue(mseed_id = filename, filename = filename))
