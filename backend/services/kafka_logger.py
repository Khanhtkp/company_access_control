from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import time
import datetime
import os
class KafkaLogger:
    def __init__(self, topic='access_logs'):
        broker = os.getenv("KAFKA_BROKER", "kafka:9092")
        retries = 10
        for i in range(retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=broker,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                print(f"Connected to Kafka at {broker}")
                break
            except NoBrokersAvailable:
                print(f"Kafka not ready, retrying {i+1}/{retries}...")
                time.sleep(2)
        else:
            raise RuntimeError("Kafka is not available after retries")

        self.topic = topic

    def log_access(self, user_id: str, status: str):
        log = {
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.producer.send(self.topic, log)
        self.producer.flush()