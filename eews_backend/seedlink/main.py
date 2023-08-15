from typing import List
from .seedlink import Seedlink
import multiprocessing

global process_list
process_list: List[multiprocessing.Process] = []


def seedlink_process(station: str):
    client = Seedlink(station)
    client.start()


def main():
    stations = ["JAGI", "BNDI"]
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
