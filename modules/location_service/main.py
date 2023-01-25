import psycopg2
from kafka import KafkaConsumer
import os
import json
from schemas import LocationSchema
import logging
from typing import Dict

DB_USERNAME = os.environ["DB_USERNAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_NAME = os.environ["DB_NAME"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('udaconnect-location-service')

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USERNAME,
    password=DB_PASSWORD
)

consumer = KafkaConsumer(
    'location',
    bootstrap_servers='my-release-kafka.default.svc.cluster.local:9092'
)

cur = conn.cursor()

for message in consumer:
    data = message.value.decode('utf-8')
    data_dict = json.loads(data)

    #validation_result: Dict = LocationSchema.validate(data_dict)
    #if validation_result:
    #    logger.warning(f"Unexpected data format in payload: {location}, reason: {validation_result}")
    #    return

    person_id = int(data_dict['person_id'])

    query = "INSERT INTO location (person_id, coordinate) VALUES ({}, ST_Point({}, {}))".format(person_id, data_dict["latitude"], data_dict["longitude"])
    try:
        cur.execute(query)
        logger.info("Saved the location data to the database")
    except Exception as e:
        logger.error(f"Unable to save location data to the database. reason: {e}")

    #cur.close()
    #conn.close()