#!/usr/bin/env python
import asyncio
import pika
import time
from kafka import KafkaProducer

params = pika.ConnectionParameters(
    host='localhost',
    port=5672,
    virtual_host='/',
    credentials=pika.PlainCredentials('guest', 'guest'),
    heartbeat=120,
    blocked_connection_timeout=100 
)
connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue='index_document_task_queue', durable=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Kafka setup
producer = KafkaProducer(bootstrap_servers='localhost:9092')

async def callback(ch, method, properties, body):
    message = body.decode()
    print(message)
    producer.send('indexing_topic', message.encode('utf-8'))
    time.sleep(body.count(b'.'))

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='index_document_task_queue', on_message_callback=lambda ch, method, properties, body: asyncio.run(callback(ch, method, properties, body)), auto_ack=True)

channel.start_consuming()
