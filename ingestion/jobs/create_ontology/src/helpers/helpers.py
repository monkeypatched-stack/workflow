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

BATCH_SIZE = 10
logging = logging.getLogger(__name__)


# -----------------------------
# Split Content
# -----------------------------
def split_content(content, batch_size):
    num_batches = math.ceil(len(content) / batch_size)
    return [content[i * batch_size : (i + 1) * batch_size] for i in range(num_batches)]


# -----------------------------
# Batch Add to Neo4j
# -----------------------------
async def batch_add_to_neo4j(batched_data):
    for batch in batched_data:
        try:
            await add_to_neo4j(batch["entities"], batch["relationships"])
        except Exception as e:
            print(f"Batch Insert Error: {e}")


# -----------------------------
# Extract Ontology
# -----------------------------
async def extract_ontology(pdf_text, thread_pool):
    response = post_to_llm(get_the_index_retrieval_prompt(pdf_text))
    print(response.json())
    content = response.json()["choices"][0]["message"]["content"]

    for attempt in range(3):
        try:
            response = post_to_llm(get_ontology_prompt(content))
            print(response.json())
            if response.status_code != 200:
                break
        except Exception as e:
            print(f"Retry {attempt + 1} failed: {e}")

    if not response or "error" in response.json():
        print("Error in LLM response.")
        return

    content = response.json()["choices"][0]["message"]["content"]
    print(f"Raw LLM response: {content}")

    if not content.strip():
        print("Empty content from LLM.")
        return

    loop = asyncio.get_running_loop()

    try:
        matches = await loop.run_in_executor(
            thread_pool, re.findall, r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", content, re.DOTALL
        )
        print(matches)
    except Exception as e:
        print(f"Error extracting JSON matches: {e}")
        return

    if not matches:
        print("No valid JSON data found.")
        return

    try:
        results = await asyncio.gather(
            *[loop.run_in_executor(thread_pool, json.loads, match.strip()) for match in matches]
        )
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return

    batched_data = [results[i : i + BATCH_SIZE] for i in range(0, len(results), BATCH_SIZE)]

    await asyncio.gather(*[batch_add_to_neo4j(batch) for batch in batched_data])

    print(f"Inserted {len(results)} items into Neo4j successfully.")


# -----------------------------
# Fetch Entity Details
# -----------------------------
async def fetch_entity_details(pdf_text, thread_pool):
    chunks = split_content(pdf_text, 500)
    for chunk in chunks:
        await extract_ontology(chunk, thread_pool)
    print(f"Processed {len(chunks)} chunks successfully.")



