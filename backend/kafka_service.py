from kafka import KafkaProducer, KafkaConsumer
import json
import os
import asyncio
from threading import Thread

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

class KafkaService:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self.running = False

    def start(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Kafka Producer started")
        except Exception as e:
            print(f"Failed to start Kafka Producer: {e}")

    async def send_message(self, topic, message):
        if self.producer:
            self.producer.send(topic, message)
            self.producer.flush()

    def consume_messages(self, topic, callback):
        self.running = True
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='latest'
            )
            print(f"Kafka Consumer started for topic: {topic}")
            for message in self.consumer:
                if not self.running:
                    break
                asyncio.run(callback(message.value))
        except Exception as e:
            print(f"Failed to start Kafka Consumer: {e}")

    def stop(self):
        self.running = False
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.close()

kafka_service = KafkaService()
