#!/usr/bin/env python
import json
import logging
import os
from dotenv import load_dotenv
import pika
import time

from src.helpers.helpers import create_ontology_message_handler

load_dotenv()  # Load variables from .env

logging.basicConfig(level=logging.INFO)

RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")  # Default fallback

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=str(RABBIT_HOST)))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        try:
            time.sleep(body.count(b'.'))
            # must process the uploaded document 
            message = body.decode()
            if "customer_name" in message and "document_name" in message:
                document_name = json.loads(message)["document_name"]
                create_ontology_message_handler(document_name)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    channel.start_consuming()
except pika.exceptions.AMQPConnectionError as e:
    logging.error(f"Connection error: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")