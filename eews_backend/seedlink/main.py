from typing import List
from .seedlink import Seedlink
import multiprocessing
import os
from dotenv import load_dotenv

load_dotenv()

station_list = os.getenv("STATION_LIST")
if type(station_list) == str:
    station_list = station_list.split(",")

global process_list
process_list: List[multiprocessing.Process] = []


def seedlink_process(station: str):
    client = Seedlink(station)
    client.start()


def main():
    stations = station_list if station_list else ["JAGI", "BNDI"]
    for station in stations:
        process = multiprocessing.Process(target=seedlink_process, args=(station,))
        process.name = f"seedlink_{station}"
        process_list.append(process)
    for process in process_list:
        process.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        for process in process_list:
            process.join()
