from database.influxdb import *
from stream_processing.kafka import KafkaConsumer
from stream_processing.topics import P_ARRIVAL_TOPIC
from utils.helper_functions import get_nearest_station, letInterpolate, denormalization
from predict.predictor import Predictor
from dotenv import load_dotenv
import datetime

load_dotenv()

consumer = KafkaConsumer(P_ARRIVAL_TOPIC, "eews", {})
predictor = Predictor()

def main(msg):
    stations = get_nearest_station(msg["station"], 200000)

    seis_data = []

    for station in stations:
        data = read_seis_influx(station, datetime.datetime.strptime(msg["time"],'%Y-%m-%dT%H:%M:%S.%fZ'))
        if data:
            data_preprocessed = preprocess(data)
            seis_data.append(data_preprocessed)

    if len(seis_data) == 1:
        seis_data *= 3
    elif len(seis_data) == 2:
        seis_data.append(seis_data[0])

    preds = predictor.predict(seis_data)
    data_mtr = denormalization(preds.iloc[0])

    print(f"{data_mtr =}")


def read_seis_influx(station: str, time: datetime.datetime):
    client = InfluxDBClient(
        url=INFLUXDB_URL,
        org=INFLUXDB_ORG,
        token=INFLUXDB_TOKEN
    )
    query_api = client.query_api()
    start_time = (time - datetime.timedelta(0,5)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    stop_time = (time + datetime.timedelta(0,5)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    data = []

    query = f"""from(bucket: "eews")
    |> range(start: {start_time}, stop: {stop_time})
    |> filter(fn: (r) => r._measurement == "seismograf" and r.station == "{station}")"""
    
    tables = query_api.query(query, org="eews")
    
    data = []
    for table in tables:
        res = []
        for record in table.records:
            res.append(record.get_value())
        data.append(res)
    
    return data

def preprocess(data):
    data_interpolated = list(map(lambda x : letInterpolate(x, 2000), data))
    
    data_interpolated_transformed = []
    
    assert len(data_interpolated[0]) == 2000
    assert len(data_interpolated[1]) == 2000
    assert len(data_interpolated[2]) == 2000

    for i in range(len(data_interpolated[0])):
        data_interpolated_transformed.append([data_interpolated[0][i], data_interpolated[1][i], data_interpolated[2][i]])
    return data_interpolated_transformed

if __name__ == "__main__":
    consumer.consume(on_message=main, on_error=None)
