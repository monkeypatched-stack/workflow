import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging
import math
import os
import re
from src.db.queries import add_to_neo4j
from src.prompts.prompts import get_ontology_prompt, get_the_index_retrieval_prompt
from src.tools.open_router import post_to_llm

# Thread Pool for parallel processing
num_threads = os.cpu_count() or 10
thread_pool = ThreadPoolExecutor(max_workers=num_threads)

BATCH_SIZE = 10


# -----------------------------
# Process Page with Semaphore
# -----------------------------
async def send_create_ontology_event(page_text):
    """Process page content with concurrency control."""
    logging.info(f"Processing page to create ontology: {page_text}")
    return await fetch_entity_details(page_text)


# -----------------------------
# Split Content
# -----------------------------
def split_content(content, batch_size):
    """Split content into manageable batches."""
    num_batches = math.ceil(len(content) / batch_size)
    return [content[i * batch_size : (i + 1) * batch_size] for i in range(num_batches)]


# -----------------------------
# Batch Add to Neo4j
# -----------------------------
async def batch_add_to_neo4j(batched_data):
    """Batch insert entities and relationships into Neo4j."""
    for batch in batched_data:
        try:
            await add_to_neo4j(batch["entities"], batch["relationships"])
        except Exception as e:
            logging.error(f"Batch Insert Error: {e}")
            
# -----------------------------
# Extract Ontology
# -----------------------------
async def extract_ontology(pdf_text):
    """Extract ontology using LLM and store in Neo4j."""
        # get the index for the content
    response = post_to_llm(get_the_index_retrieval_prompt(pdf_text))

    content = response.json()["choices"][0]["message"]["content"]

    logging.info(content)

    for attempt in range(3):
        try:
            response = post_to_llm(get_ontology_prompt(content))
            if response.status_code == 200:
                break
        except Exception as e:
            logging.error(f"Retry {attempt + 1} failed: {e}")

    if not response or "error" in response.json():
        logging.error("Error in LLM response.")
        return

    content = response.json()["choices"][0]["message"]["content"]
    logging.info(f"Raw LLM response: {content}")

    if not content.strip():
        logging.warning("Empty content from LLM.")
        return

    # Extract and parse JSON content
    loop = asyncio.get_running_loop()
    try:
        matches = await loop.run_in_executor(
            thread_pool, re.findall, r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", content, re.DOTALL
        )
    except Exception as e:
        logging.error(f"Error extracting JSON matches: {e}")
        return

    if not matches:
        logging.warning("No valid JSON data found.")
        return

    try:
        results = await asyncio.gather(
            *[loop.run_in_executor(thread_pool, json.loads, match.strip()) for match in matches]
        )
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
        return

    # Batch insert data to Neo4j
    batched_data = [
        results[i : i + BATCH_SIZE] for i in range(0, len(results), BATCH_SIZE)
    ]

    await asyncio.gather(
        *[batch_add_to_neo4j(batch) for batch in batched_data]
    )

    logging.info(f"Inserted {len(results)} items into Neo4j successfully.")
   

# -----------------------------
# Fetch Entity Details
# -----------------------------
async def fetch_entity_details(pdf_text):
    """Fetch and extract ontology details from text."""
    chunks = split_content(pdf_text, 2500)
    for chunk in chunks:
        await extract_ontology(chunk)
    logging.info(f"Processed {len(chunks)} chunks successfully.")
