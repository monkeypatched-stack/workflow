#!/usr/bin/env python
import pika
import time
from  src.helpers.helpers import send_create_ontology_event
import asyncio

params = pika.ConnectionParameters(
    host='localhost',
    port=5672,
    virtual_host='/',
    credentials=pika.PlainCredentials('guest', 'guest'),
    heartbeat=120,  # Lower heartbeat interval
    blocked_connection_timeout=100
)
connection = pika.BlockingConnection(params)

channel = connection.channel()
channel.queue_declare(queue='create_ontology_task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')

async def callback(ch, method, properties, body):
    message = body.decode()
    print(message)
    await send_create_ontology_event(message)
    await asyncio.sleep(body.count(b'.'))  # Non-blocking sleep
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='create_ontology_task_queue', on_message_callback=lambda ch, method, properties, body: asyncio.run(callback(ch, method, properties, body)), auto_ack=False)

channel.start_consuming()