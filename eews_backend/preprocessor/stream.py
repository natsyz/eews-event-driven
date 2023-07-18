from math import ceil
from typing import Any, Dict
from dotenv import load_dotenv
from obspy import read
from database import new_client
from eews_backend.stream_processing import schema, topics
from utils import *
import faust
import os

load_dotenv()

BOOTSTRAP_SERVER = os.getenv("BOOTSTRAP_SERVER")
if not BOOTSTRAP_SERVER:
    raise Exception("BOOTSTRAP_SERVER is required")

APP_NAME = "preprocessor"
stream = faust.App(APP_NAME, broker=BOOTSTRAP_SERVER)

# Kafka Topics
raw_topic = stream.topic(topics.RAW_TOPIC, value_type=schema.RawValue)
raw_mseed_topic = stream.topic(topics.RAW_MSEED_TOPIC, value_serializer="raw")

client, db = new_client()

@stream.agent(raw_topic)
async def process_raw_topic(data):
    async for key, value in data.items():
        mseed = await db["mseed"].find_one({"name": value.mseed_name})
        

@stream.agent(raw_mseed_topic)
async def process_raw_mseed_topic(data):
    async for key, value in data.items():
        with open("mseed.txt", "wb") as mseed:
            mseed_file = mseed.write(value)
            mseed_data = read(mseed_file)
            l_diff, first_starttime = add_null_station(gmji, jagi, pwji)
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
                data_before = detail.data
                data_processed = butter_bandpass_filter(data_before, lowcut, highcut, fs,order)
                data_processed = normalizations(data_processed)
                data_to = list(data_processed)
                preprocessed['data'] = array_to_str_limit_dec(data_to)
                data_to = letInterpolate(data_to, int(ceil(len(data_to)*25/detail.stats.sampling_rate)))
                if detail.stats.station == "GMJI":
                    print(l_diff[0][2])
                    if detail.stats.channel == l_diff[0][2]:
                        print('masuk')
                        if l_diff[0][1] != 0:
                            for i in range(l_diff[0][1]):
                                data_to.insert(0, None)
                            print(data_processed[0:100])
                elif detail.stats.station == "JAGI":
                    if detail.stats.channel == l_diff[1][2]:
                        if l_diff[1][1] != 0:
                            for i in range(l_diff[1][1]):
                                data_to.insert(0, None)
                elif detail.stats.station == "PWJI":
                    if detail.stats.channel == l_diff[2][2]:
                        if l_diff[2][1] != 0:
                            for i in range(l_diff[2][1]):
                                data_to.insert(0, None)
                preprocessed['sampling_rate'] = 25.0
                preprocessed['data_interpolated'] = array_to_str_limit_dec(data_to)
                preprocessed['starttime_station'] = str(first_starttime)
                # datas['first_npts'] = first_npts
                # print(data_processed)
                # serializer.validated_data['traces'].append(preprocessed)

            