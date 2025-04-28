# -----------------------------
#  Create Ontology Message Handler
# -----------------------------
import asyncio
import io
import logging
import os

import boto3
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import fitz
import pika
import requests

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

logging.basicConfig(level=logging.INFO)

# S3 Client Setup
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION,
)

# add a owrker queue
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='task_exchange',exchange_type='direct')

async def publish_messages(pdf_text):
    """Publish messages to RabbitMQ."""
    try:
        # Split large messages into smaller chunks
        chunks = [pdf_text[i:i+1000] for i in range(0, len(pdf_text), 1000)]
        for chunk in chunks:
            # Create a new channel for each publish
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost')
            )
            channel = connection.channel()
            channel.exchange_declare(exchange='task_exchange', exchange_type='direct')

            # Publish messages
            channel.basic_publish(
                exchange='task_exchange',
                routing_key='create_ontology',
                body=chunk,
                properties=pika.BasicProperties(
                    delivery_mode=2  # Make message persistent
                )
            )
            channel.basic_publish(
                exchange='task_exchange',
                routing_key='index_document',
                body=chunk,
                properties=pika.BasicProperties(
                    delivery_mode=2  # Make message persistent
                )
            )
            connection.close()
    except Exception as e:
        logging.error(f"Failed to publish messages: {e}")

# -----------------------------
# Create Ontology
# -----------------------------
def create_ontology(filename):
    """Download a PDF from S3 and extract ontology."""
    logging.info(f"Creating ontology for {filename}")
    PREFIX = "uploads/"
    filename = filename.replace('"', "")
    file_key = f"{PREFIX}{filename}"

    try:
        # Download PDF in a thread to avoid blocking
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=file_key)
        pdf_data = response["Body"].read()
        pdf_document = fitz.open(stream=io.BytesIO(pdf_data), filetype="pdf")

        # Extract text from each page
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pdf_text = page.get_text()
            pdf_text = pdf_text.replace("\n", " ")
            asyncio.run(publish_messages(pdf_text))

        pdf_document.close()
        logging.info(f"Ontology extraction completed for {filename}")

        return JSONResponse(
            content={"message": "Ontology extraction completed."},
            status_code=200,
        )
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return JSONResponse(
            content={"error": f"Request failed: {str(e)}"},
            status_code=500,
        )
    except boto3.exceptions.S3UploadFailedError as e:
        logging.error(f"S3 upload failed: {e}")
        return JSONResponse(
            content={"error": f"S3 upload failed: {str(e)}"},
            status_code=500,
        )
    except Exception as e:
        logging.error(f"Ontology extraction failed: {e}")
        return JSONResponse(
            content={"error": f"Ontology extraction failed: {str(e)}"},
            status_code=500,
        )

# -----------------------------
#  Create Ontology Message Handler
# -----------------------------
def create_ontology_message_handler(msg):
    """Handle messages to create ontology."""
    logging.info(f"Received message: {msg}")
    create_ontology(msg)
    logging.info(f"Ontology creation completed for {msg}")
