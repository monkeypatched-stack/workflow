import asyncio
import json
import logging
import os
from dotenv import load_dotenv
import websockets
import pika

load_dotenv()
logging.basicConfig(level=logging.INFO)

HOST = os.getenv("WEBSOCKET_HOST", "localhost")
PORT = int(os.getenv("WEBSOCKET_PORT", 6789))

load_dotenv()  # Load variables from .env

logging.basicConfig(level=logging.INFO)

RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")  # Default fallback


async def keep_alive(websocket, interval=30):
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(interval)
        except websockets.exceptions.ConnectionClosed:
            break


async def handle_client(websocket):
    logging.info(f"New connection from {websocket.remote_address}")

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_HOST)  # or 'localhost'
        )
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
        await websocket.close()
        return

    keepalive_task = asyncio.create_task(keep_alive(websocket))

    try:
        async for message in websocket:
            logging.info(f"Received message: {message}")
            try:
                data = json.loads(message)
                if "customer_name" in data and "document_name" in data:
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
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
    except websockets.exceptions.ConnectionClosed as e:
        logging.info(f"Connection closed: {e}")
    finally:
        keepalive_task.cancel()
        logging.info("Client disconnected")
        if connection and connection.is_open:
            connection.close()


async def main():
    server = await websockets.serve(handle_client, HOST, PORT)
    logging.info(f"WebSocket server running on ws://{HOST}:{PORT}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
