from dotenv import load_dotenv
from eews_backend.stream_processing import schema, topics
import faust
import os

load_dotenv()

BOOTSTRAP_SERVER = os.getenv("BOOTSTRAP_SERVER")
if not BOOTSTRAP_SERVER:
    raise Exception("BOOTSTRAP_SERVER is required")

APP_NAME = "rest"
stream = faust.App(APP_NAME, broker=BOOTSTRAP_SERVER)
raw_topic = stream.topic(topics.RAW_TOPIC, value_type=schema.RawValue)
