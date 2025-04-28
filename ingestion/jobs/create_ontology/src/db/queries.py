import time
from src.utils.graph import connection
from neomodel import db

async def add_clause_to_agreement():
        query  = f""" 
                MATCH (a:Document)
                WHERE a.name IN ["Agreement", "Manufacturing Agreement"]
                MATCH (c:Clause)
                MERGE (a)-[:HAS_CLAUSE]->(c);
        """
        connection.query(query)

async def add_annextures_to_agreement():
        query = f"""
                MATCH (d:Document)
                WHERE d.name IN ["Agreement", "Manufacturing Agreement"]
                MATCH (a:Annex)
                MERGE (d)-[:HAS_ANNEX]->(a);
        """
        connection.query(query)


async def add_to_neo4j(entities, relationships):
    """Adds entities and relationships to Neo4j while preserving existing ones."""
    try:
        with db.transaction:
            for entity in entities:
                time.sleep(10)
                query = f"""
                MERGE (n:{entity['type'].replace(" ","_").lower().replace("/","_or_")} {{name: $name}})
                ON CREATE SET n.created_at = timestamp()
                ON MATCH SET n.updated_at = timestamp()
                """
                connection.query(query, {"name": entity["name"].replace(" ","_").lower()})
                print(f"Added entity: {entity}")
               

            for relationship in relationships:
                time.sleep(10)
                query = f"""
                MATCH (a {{name: $from}}), (b {{name: $to}})
                MERGE (a)-[r:{relationship['type'].replace(" ","_").lower()}]->(b)
                ON CREATE SET r.count = 1
                ON MATCH SET r.count = coalesce(r.count, 0) + 1
                """
                connection.query(query, {"from": relationship["from"].replace(" ","_").lower(), "to": relationship["to"].replace(" ","_").lower()})
                print(f"Added relashionship: {relationship}")

            await add_clause_to_agreement()
            await add_annextures_to_agreement()

    except Exception as e:
        print(f"Error adding to Neo4j: {e}")

async def create_and_link_question(question_text, clause_name):
        query = f"""
                MERGE (q:question {{question: $question_text}})
                WITH q
                MATCH (c:clause {{name: $clause_name}})
                MERGE (q)-[:BELONGS_TO]->(c)
        """
        connection.query(query, {"question_text": question_text, "clause_name": clause_name})
        print(f"""Added : {question_text} to  {clause_name}""")
       

async def get_list_of_clauses():
    query = f"""
               MATCH (n:clause) RETURN n
            """
    return {"clauses":connection.query(query)}

async def get_list_of_entities():
    query = f"""
        MATCH (n:entity) RETURN n
        """
    return {"clauses":connection.query(query)}

async def get_clauses_linked_to_question(question_text: str):
    """Find Clause nodes connected to a given Question."""
    query = f"""
    MATCH (q:question)-[:BELONGS_TO]->(c:clause)
        WHERE q.question = "{question_text}"
        RETURN c;
    """
    return {"clauses": connection.query(query, {"question_text": question_text})}
