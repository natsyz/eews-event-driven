from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, BackgroundTasks, status
from obspy import read
from typing import List, Optional
from motor import motor_asyncio
from pprint import pprint
from functools import wraps
import timeit
import logging
import numpy as np
import faust
import os
import time
# from schema import *

load_dotenv()

RAW_TOPIC = 'raw'
RAW_MSEED_TOPIC = 'raw-mseed'
PREPROCESSED_TOPIC = 'preprocessed'
PREDICTION_TOPIC = 'prediction'
STATIC_DIR = "./static/"

DEFAULT_MONGO_DATABASE = "db"
RAW_MONGO_URL = os.getenv("RAW_MONGO_URL")
RAW_MONGO_DATABASE = os.getenv("RAW_MONGO_DATABASE") if os.getenv("RAW_MONGO_DATABASE") else DEFAULT_MONGO_DATABASE
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DATABASE = os.getenv("MONGO_DATABASE") if os.getenv("MONGO_DATABASE") else DEFAULT_MONGO_DATABASE

raw_client = motor_asyncio.AsyncIOMotorClient(RAW_MONGO_URL)
raw_db = raw_client[RAW_MONGO_DATABASE]

client = motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DATABASE]

BOOTSTRAP_SERVER = os.getenv("BOOTSTRAP_SERVER")
if not BOOTSTRAP_SERVER:
    raise Exception("BOOTSTRAP_SERVER is required")

class RawValue(faust.Record, serializer="json"):
    mseed_name: str
    filename: str
    
def array_to_str_limit_dec(array):
    lst = ""
    for i in array:
      if i == None:
            i = "None"
            lst += i + " "
      else:
            lst += '{:.10f}'.format(np.round_(i, 10)) + " "
    return lst

def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = timeit.default_timer()
        result = func(*args, **kwargs)
        end_time = timeit.default_timer()

        execution_time = end_time - start_time
        print(f"Execution Time of {func.__name__}: {execution_time} seconds")
        return result

    return wrapper

@measure_execution_time
def process_data(mseed_filename):
    mseed_data = read(mseed_filename)
    traces = []
    # l_diff, first_starttime = add_null_station(gmji, jagi, pwji)
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
        # data_before = detail.data
        # data_processed = butter_bandpass_filter(data_before, lowcut, highcut, fs,order)
        # data_processed = normalizations(data_processed)
        # data_to = list(data_processed)
        preprocessed['data'] = array_to_str_limit_dec(detail.data)
        # data_to = letInterpolate(data_to, int(ceil(len(data_to)*25/detail.stats.sampling_rate)))
        # if detail.stats.station == "GMJI":
        #     print(l_diff[0][2])
        #     if detail.stats.channel == l_diff[0][2]:
        #         print('masuk')
        #         if l_diff[0][1] != 0:
        #             for i in range(l_diff[0][1]):
        #                 data_to.insert(0, None)
        #             print(data_processed[0:100])
        # elif detail.stats.station == "JAGI":
        #     if detail.stats.channel == l_diff[1][2]:
        #         if l_diff[1][1] != 0:
        #             for i in range(l_diff[1][1]):
        #                 data_to.insert(0, None)
        # elif detail.stats.station == "PWJI":
        #     if detail.stats.channel == l_diff[2][2]:
        #         if l_diff[2][1] != 0:
        #             for i in range(l_diff[2][1]):
        #                 data_to.insert(0, None)
        # preprocessed['sampling_rate'] = 25.0
        # preprocessed['data_interpolated'] = array_to_str_limit_dec(data_to)
        # preprocessed['starttime_station'] = str(first_starttime)
        # datas['first_npts'] = first_npts
        # print(data_processed)
        # serializer.validated_data['traces'].append(preprocessed)
        traces.append(preprocessed)
    return traces
    

app = FastAPI()
@app.post("/mseed", status_code=status.HTTP_201_CREATED)
async def upload_mseed(file: UploadFile, background_tasks: BackgroundTasks):
    filename = file.filename
    # background_tasks.add_task(_save_mseed, file, filename)
    background_tasks.add_task(_send_mseed, file, filename)
    return {"file_size": file.size, "filename": filename}

async def _save_mseed(file: UploadFile, filename: str):
    print(f"{time.time_ns()} | saving mseed to db")
    contents = await file.read()
    with open(f"{STATIC_DIR}{filename}", "wb") as f:
        f.write(contents)
    traces = process_data(f"{STATIC_DIR}{filename}")
    # pprint(traces)
    await raw_db["mseed"].insert_one({"name": filename, "traces": traces})
    await raw_topic.send(value=RawValue(mseed_id = filename, filename = filename))
        
async def _send_mseed(file: UploadFile, filename: str):
    print(f"{time.time_ns()} | sending mseed to kafka")
    contents = await file.read()
    await raw_mseed_topic.send(key=filename, value=contents, value_serializer="raw")

# Stream Processing
APP_NAME = "sandbox"
stream = faust.App(APP_NAME, broker=BOOTSTRAP_SERVER, producer_max_request_size=5242880, consumer_max_fetch_size=5242880)
raw_topic = stream.topic(RAW_TOPIC, value_type=RawValue)
raw_mseed_topic = stream.topic(RAW_MSEED_TOPIC, key_serializer="str", value_serializer='raw')

@stream.agent(raw_topic)
async def process_raw_topic(data):
    async for key, value in data.items():
        mseed = await db["mseed"].find_one({"name": value.mseed_name})
        print("found mseed on db", mseed.traces) 
        

@stream.agent(raw_mseed_topic)
async def process_raw_mseed_topic(data):
    async for key, value in data.items():
        print(f"{time.time_ns()} | received mseed from kafka")
        with open(f"{key}", "wb") as f:
            f.write(value)
        traces = process_data(f"{key}")
        print(f"{time.time_ns()} | finished processing data")
        # pprint(traces)
        await raw_db["mseed"].insert_one({"name": key, "traces": traces})
        print("processed raw bytes", traces)
            

# test_topic = stream.topic("test", partitions=8)
# @stream.agent(test_topic)
# async def test_listen(data):
#     async for key, value in data.items():
#         print("RECEIVED MESSAGE", key, value)

# # Generator app
# generator = faust.App("generator", broker=BOOTSTRAP_SERVER)

# @generator.timer(interval=1)
# async def data_generator():
#     for i in range(1):
#         data = {"name": None, "timestamp": str(time.time())}
#         await test_topic.send(value=data)