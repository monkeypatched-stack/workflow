#!/usr/bin/env python
import pika
import time
import asyncio

# create the connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

# declare the channel 
channel = connection.channel()

# listen to the task queue
channel.queue_declare(queue='task_queue', durable=True)

# declare the exchange
channel.exchange_declare(exchange='task_exchange', exchange_type='direct')

# crate a queue
result = channel.queue_declare(queue='create_ontology_task_queue', durable=True)
queue_name = result.method.queue

# bind to exchange
channel.queue_bind(exchange='task_exchange', queue=queue_name, routing_key='create_ontology')

print(' [*] Waiting for messages. To exit press CTRL+C')

async def callback(ch, method, properties, body):
    time.sleep(body.count(b'.'))
    # must process the uploaded document 
    message = body.decode()
    channel.basic_publish(
        exchange='',
        routing_key='create_ontology_task',
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