#!/usr/bin/env python
import asyncio
import pika
import time

from src.helpers.helpers import send_index_document_event

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

async def callback(ch, method, properties, body):
    message = body.decode()
    print(message)
    await send_index_document_event(message)
    time.sleep(body.count(b'.'))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='index_document_task_queue', on_message_callback=lambda ch, method, properties, body: asyncio.run(callback(ch, method, properties, body)), auto_ack=False)

channel.start_consuming()
