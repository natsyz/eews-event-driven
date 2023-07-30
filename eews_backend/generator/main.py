from ast import List
import requests
from obspy import read, Stream, UTCDateTime, Trace
import time
import os
import shutil
import threading

MSEED_FOLDER = "eews_backend/mseed/"
SOURCE_MSEED = "eews_backend/generator/20150920_151412.mseed"
REST_URL = "http://127.0.0.1:8000"
MSEED_RANGE_IN_SECONDS = 10


def main():
    split_mseed()

    print("Start sending file to", REST_URL)
    threads = []
    for station in os.listdir(MSEED_FOLDER):
        send_thread = threading.Thread(target=send, args=(station,))
        send_thread.name = station
        threads.append(send_thread)
    for thread in threads:
        thread.start()


def send(station: str):
    folder = f"{MSEED_FOLDER}/{station}/"
    BHE: List[str] = os.listdir(f"{folder}BHE/")
    BHN: List[str] = os.listdir(f"{folder}BHN/")
    BHZ: List[str] = os.listdir(f"{folder}BHZ/")

    for index in range(len(BHE)):
        bhe_mseed: bytes = open(f"{MSEED_FOLDER}/{station}/BHE/{BHE[index]}", "rb")
        bhn_mseed: bytes = open(f"{MSEED_FOLDER}/{station}/BHN/{BHN[index]}", "rb")
        bhz_mseed: bytes = open(f"{MSEED_FOLDER}/{station}/BHZ/{BHZ[index]}", "rb")

        threading.Thread(
            target=post, args=(f"{REST_URL}/mseed", {"file": bhe_mseed})
        ).start()
        threading.Thread(
            target=post, args=(f"{REST_URL}/mseed", {"file": bhn_mseed})
        ).start()
        threading.Thread(
            target=post, args=(f"{REST_URL}/mseed", {"file": bhz_mseed})
        ).start()

        time.sleep(10)


def post(url, files):
    requests.post(url, files=files)


def split_mseed():
    print("Mseed will be saved to folder", MSEED_FOLDER)
    print("Splitting mseed")
    st: Stream = read(SOURCE_MSEED)
    dt = UTCDateTime("2015-08-20T15:12:00")
    last_endtime = max([trace.stats["endtime"] for trace in st])
    trace: Trace
    shutil.rmtree(MSEED_FOLDER)
    while dt <= last_endtime:
        trimmed = st.slice(dt, dt + MSEED_RANGE_IN_SECONDS)
        for trace in trimmed:
            stats = trace.stats
            filename = f"{MSEED_FOLDER}{stats['station']}/{stats['channel']}/{dt.strftime('%Y%m%d')}_{stats['starttime'].strftime('%H%M%S')}.mseed"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            trace.write(filename=filename, format="MSEED")
        dt += MSEED_RANGE_IN_SECONDS
    print("Finished splitting mseed")


if __name__ == "__main__":
    main()
