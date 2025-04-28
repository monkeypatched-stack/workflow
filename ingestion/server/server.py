
import asyncio
import json
import logging
import os
import threading
from dotenv import load_dotenv
import websockets
import pika
import sys

try:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='task_queue', durable=True)
except pika.exceptions.AMQPConnectionError as e:
    logging.error(f"Failed to connect to RabbitMQ: {e}")
    sys.exit(1)




load_dotenv()

logging.basicConfig(level=logging.INFO)

HOST =  os.getenv("WEBSOCKET_HOST", "localhost")
PORT = os.getenv("WEBSOCKET_PORT", 6789)

async def handle_client(websocket):
    logging.info(f"New connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(message)
            if "customer_name" in message and "document_name" in message:
                # publish the event to rabbit mq
                channel.basic_publish(
                exchange='',
                routing_key='task_queue',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ))
                logging.info("Event published successfully")
            else:
                logging.info("Invalid message format. Expected keys: customer_name, document_name")
        logging.info("Client disconnected")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
    except websockets.exceptions.InvalidMessage as e:
        logging.error(f"Invalid message: {e}")
    except websockets.exceptions.ConnectionClosedOK as e:
        logging.error(f"Connection closed OK: {e}")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed with error: {e}")
    except websockets.exceptions.ConnectionClosedOK as e:
        logging.error(f"Connection closed OK: {e}")
    except websockets.exceptions.ConnectionClosedError as e:
        logging.error(f"Connection closed with error: {e}")
    finally:
        logging.info("Client disconnected")
        if 'connection' in locals() and connection.is_open:
            connection.close()


async def main():
    server = await websockets.serve(handle_client, HOST, PORT)
    logging.info(f"WebSocket server running on ws://{HOST}:{PORT}")
    await server.wait_closed()

# Run the server
if __name__ == "__main__":
    asyncio.run(main())