#!/usr/bin/env python
import logging
import pika
import time
import asyncio

# create the connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

# create the excahnge
channel = connection.channel()

# listen to the task queue 
channel.queue_declare(queue='task_queue', durable=True)

# declare the task exchange
channel.exchange_declare(exchange='task_exchange', exchange_type='direct')

# create the queue
result = channel.queue_declare(queue='index_document_task_queue', durable=True)
queue_name = result.method.queue

# bind the queue
channel.queue_bind(exchange='task_exchange', queue=queue_name, routing_key='index_document')




print(' [*] Waiting for messages. To exit press CTRL+C')

async def callback(ch, method, properties, body):
    time.sleep(body.count(b'.'))
    # must process the uploaded document 
    message = body.decode()
    channel.basic_publish(
        exchange='',
        routing_key='index_document_task',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2))
    print(message)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(
    queue=queue_name,
    on_message_callback=lambda ch, method, properties, body: asyncio.run(callback(ch, method, properties, body))
)

channel.start_consuming()