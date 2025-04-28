import asyncio
import json
import logging
import os
from dotenv import load_dotenv
from nats.aio.client import Client as NATS

from src.helpers.helpers import send_create_ontology_event

logging.basicConfig(level=logging.INFO)

load_dotenv()

NATS_SERVER_URL = os.getenv("NATS_SERVER_URL", "nats://localhost:4222")  # Default fallback

# NATS Connection Pool
nats_pool = None

# Initialize NATS Pool
# -----------------------------
async def init_nats_pool():
    """Initialize a NATS connection pool."""
    global nats_pool
    nats_pool = NATS()
    await nats_pool.connect(NATS_SERVER_URL,
            max_reconnect_attempts=10,
            reconnect_time_wait=2,
            verbose=True)
    logging.info("NATS connection pool initialized.")

# -----------------------------
# Publish Event to NATS
# -----------------------------
async def publish_event(subject, message):
    """Publish a message to a NATS subject."""
    try:
        if not nats_pool:
            await init_nats_pool()

        json_message = json.dumps(message)
        await nats_pool.publish(subject, json_message.encode())
        logging.info(f"Published message to subject '{subject}': {message}")
    except Exception as e:
        logging.error(f"Error publishing event: {e}")

async def handler(message):
    logging.info("in handler")
    logging.info(message.data)
    print('ho')

async def subscribe_event():
    """Subscribe to a NATS subject and listen for messages."""
    nc = NATS()
    try:
        await nc.connect(NATS_SERVER_URL,
            max_reconnect_attempts=10,
            reconnect_time_wait=2,
            verbose=True)

        await nc.subscribe("create_ontology", cb=handler)
        logging.info("Subscribed to 'create_ontology'. Waiting for messages...")

        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logging.error(f"Error subscribing to event: {e}")
    