import asyncio
import websockets

from src.tools.nats import publish_event

async def test_client():
 #  await publish_event("generate_question_answers","Riedhammer.pdf")
  await publish_event("create_ontology","AI EO Report Section 5.2g(i)_043024.pdf")

asyncio.run(test_client())
