#!/usr/bin/env python
import pika
from kafka import KafkaProducer
import asyncio

params = pika.ConnectionParameters(
    host='localhost',
    port=5672,
    virtual_host='/',
    credentials=pika.PlainCredentials('guest', 'guest'),
    heartbeat=120,  # Lower heartbeat interval
    blocked_connection_timeout=30
)
connection = pika.BlockingConnection(params)

channel = connection.channel()
channel.queue_declare(queue='create_ontology_task_queue', durable=True)

# Kafka setup
producer = KafkaProducer(bootstrap_servers='localhost:9092')

print(' [*] Waiting for messages. To exit press CTRL+C')

async def callback(ch, method, properties, body):
    message = body.decode()
    print(message)
    producer.send('create_ontology_topic', message.encode('utf-8'))
    await asyncio.sleep(body.count(b'.'))  # Non-blocking sleep

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='create_ontology_task_queue', on_message_callback=lambda ch, method, properties, body: asyncio.run(callback(ch, method, properties, body)), auto_ack=True)

channel.start_consuming()