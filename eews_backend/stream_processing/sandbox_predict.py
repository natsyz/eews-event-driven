### SPARK APP
#
## Command in terminal pc
# docker cp sandbox_predict.py [container-id]:/opt/bitnami/spark/sandbox_predict.py
# docker cp model.pkl [container-id]:/opt/bitnami/spark/model.pkl
# docker exec [container-name] ./bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 --master spark://[host]:[port] sandbox_predict.py
#
## Command in terminal docker (spark)
# pip install influxdb_client motor keras tensorflow
#
## Notes
# this code has not been run yet due to resource limitation on my end :(
#
###

from influxdb_client import InfluxDBClient
from motor import motor_asyncio

from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pyspark.sql.functions as f

import datetime
import pickle

BOOTSTAP_SERVERS = "$"
MONGO_URL = "$"
MONGO_DATABASE = "$"
INFLUXDB_ORG = "$"
INFLUXDB_URL = "$"
INFLUXDB_TOKEN = "$"

model = pickle.load(open('model.pkl', 'rb'))

def main():
    spark, sc = init_spark()
    model_broadcast = sc.broadcast(model)

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", BOOTSTAP_SERVERS) \
        .option("subscribe", "p-arrival") \
        .load()
    
    schema = StructType([StructField('station', StringType()), StructField('time', StringType())])
    schema_output = StructType([StructField('lat', StringType()), \
                                StructField('long', StringType()), \
                                StructField('depth', StringType()), \
                                StructField('magnitude', StringType()), \
                                StructField('time', StringType())])

    df_json = df.selectExpr("CAST(value AS STRING) as json") \
            .select(f.from_json('json', schema).alias('data')) \
            .select('data.*')
    
    def apply_prediction(station, time):
        import json
        import datetime

        # get data stasiun (mongo)
        stations = get_nearest_station(station, 200000)

        # get and preprocess data (influx)
        seis_data = []

        for station in stations:
            data = read_seis_influx(station, datetime.datetime.strptime(time,'%Y-%m-%dT%H:%M:%S.%fZ')) # [[e,...,e],[n,...,n],[z,...,z]]
            data_preprocessed = preprocess(data)
            seis_data.append(data_preprocessed)

        if len(stations) == 1:
            seis_data *= 3
        elif len(stations) == 2:
            seis_data.append(seis_data[0])
        
        # predict
        preds = model_broadcast.predict(seis_data)
        data_mtr = denormalization(preds.iloc[0])
        
        return data_mtr

    prediction_udf = f.udf(lambda data1, data2: apply_prediction(data1, data2), StringType())

    query = df_json.select(f.from_json(prediction_udf(df_json.station, df_json.time), schema_output).alias('response'))\
        .select('response.*') \
        .writeStream \
        .trigger(once=True) \
        .format("console") \
    
    query.awaitTermination()


def init_spark():
    spark = SparkSession.builder.getOrCreate()
    sc = spark.sparkContext
    return spark, sc

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
    for table in tables: #ENZ
        res = []
        for record in table.records:
            res.append(record.get_value())
        data.append(res)
    
    return data

def get_nearest_station(name, max_distance):
    client = motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DATABASE]
    coordinates = db['seismometer'].find_one({ 'name': name })['location']['coordinates']
    stations = db['seismometer'].find({ 'location': {'$nearSphere': {'$geometry': {'type': 'Point', 'coordinates': coordinates}, '$maxDistance': max_distance}}}, {'name': 1, '_id': 0})
    return names if len(names:=[station['name'] for station in stations]) <= 3 else names[:3]

def preprocess(data):
    data_interpolated = list(map(lambda x : letInterpolate(x, 2000), data)) # interpolate to 2000 data each channel
    
    data_interpolated_transformed = [] # transform to [[e,n,z], ..., [e,n,z]]
    
    for i in range(len(data_interpolated[0])):
        data_interpolated_transformed.append([data_interpolated[0][i], data_interpolated[1][i], data_interpolated[2][i]])
    return data_interpolated_transformed

def letInterpolate(inp, new_len):
    delta = (len(inp)-1) / (new_len-1)
    outp = [interpolate(inp, i*delta) for i in range(new_len)]
    return outp

def interpolate(lst, fi):
    i, f = int(fi // 1), fi % 1  # Split floating-point index into whole & fractional parts.
    j = i+1 if f > 0 else i  # Avoid index error.
    return (1-f) * lst[i] + f * lst[j]

def denormalization(data):
    max,min = {},{}
    max['lat'] = -6.64264
    min['lat'] = -11.5152
    max['long'] = 115.033
    min['long'] = 111.532
    max['depth'] = 588.426
    min['depth'] = 1.16
    max['magnitude'] = 6.5
    min['magnitude'] = 3.0
    max['time'] = 74.122
    min['time'] = 4.502

    dats = {}
    for col in data.index:
        dats[col] = data[col]*(max[col] - min[col])+min[col]
    return dats

if __name__ == "__main__":
    main()
