# -----------------------------
# Generate Question-Answer Pairs
# -----------------------------
import asyncio
import json
import logging
import os

from dotenv import load_dotenv
import requests

from src.tools.requests import post

load_dotenv()

logging.basicConfig(level=logging.INFO)
BASE_URL = os.getenv("API_BASE_URL")

async def generate_question_answer_pairs(payload):
    """Generate question-answer pairs for extracted content."""
    try: 
        # Check if payload is a string and convert to JSON
        if not payload or "content" not in payload:
            logging.error("Invalid payload format.")
            return {
                "error": "Failed to generate question-answer pairs: Invalid payload format.",
            }

        # Send the content to the agent
        response = post(f"{BASE_URL}/v1/pdf/add", data=payload)
        logging.info(f"Response status code: {response.status_code}")

        # Retry logic for the post request
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = post(f"{BASE_URL}/v1/pdf/add", data=payload)
                if response.status_code == 200 and response.text.strip():
                    break
                else:
                    logging.warning(f"Attempt {attempt + 1}: Empty response or non-200 status code.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Attempt {attempt + 1} failed: {e}")
            
        if attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        else:
            logging.error("Max retries reached. Failed to get a valid response.")
            return {
            "error": "Failed to generate question-answer pairs: Max retries reached.",
            }
        return payload
 
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON format: {e}")
        return {
            "error": f"Failed to generate question-answer pairs: {str(e)}",
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {
            "error": f"Failed to generate question-answer pairs: {str(e)}",
        }
    except Exception as e:
        logging.error(f"Error generating question-answer pairs: {e}")
        return {
            "error": f"Failed to generate question-answer pairs: {str(e)}",
        }

async def send_index_document_event(message):  
    try:
        await generate_question_answer_pairs({"content": message})
    except Exception as e:
        logging.error(f"Error in send_index_document_event: {e}")