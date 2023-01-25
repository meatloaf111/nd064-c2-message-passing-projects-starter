import time
from concurrent import futures

import grpc
import location_pb2
import location_pb2_grpc
from kafka import KafkaProducer
import json
import logging


class LocationIngestServicer(location_pb2_grpc.LocationServiceServicer):
    def Create(self, request, context):

        request_value = {
            "person_id": int(request.person_id),
            "latitude": request.latitude,
            "longitude": request.longitude
        }
        print(request_value)

        # Send protobuf data to Kafka topic
        kafka_data = json.dumps(request_value).encode()
        producer.send('location',kafka_data)
        print(f"Data to be write to Kafka topic:{kafka_data}")
        producer.flush()

        logger.info(f"Published location data {kafka_data} to Kafka topic")

        return location_pb2.LocationMessage(**request_value)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('udaconnect-location-ingest')

# Initialize gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
location_pb2_grpc.add_LocationServiceServicer_to_server(LocationIngestServicer(), server)

# Create a kakfa producer
producer = KafkaProducer(bootstrap_servers='my-release-kafka.default.svc.cluster.local:9092')




print("Server starting on port 5005...")
server.add_insecure_port("[::]:5005")
server.start()
# Keep thread alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
