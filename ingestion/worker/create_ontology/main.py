#!/usr/bin/env python
import os
import time
import pika
from kafka import KafkaProducer
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Read config from environment variables
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbit1')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'create_ontology_task_queue')

KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'broker:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'create_ontology_topic')

# RabbitMQ connection
params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=RABBITMQ_PORT,
    virtual_host='/',
    credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
    heartbeat=120,
    blocked_connection_timeout=30
)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

# Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
producer.flush()

print(' [*] Waiting for messages. To exit press CTRL+C')

async def callback(ch, method, properties, body):
    message = body.decode()
    print(f"Received: {message}")
    producer.send(KAFKA_TOPIC, message.encode('utf-8'))
    await asyncio.sleep(body.count(b'.'))
    await asyncio.sleep(10)

def start():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=RABBITMQ_QUEUE,
        on_message_callback=lambda ch, method, properties, body: asyncio.run(
            callback(ch, method, properties, body)),
        auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    start()
