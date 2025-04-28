from neo4j import GraphDatabase
from neomodel import StructuredNode, StringProperty, JSONProperty, db
from langchain.docstore.document import Document
from src.dao.document import DocumentNode
from src.utils.logger import logger

import re
from neo4j import GraphDatabase
from neomodel import config, StructuredNode,RelationshipTo,RelationshipFrom,db
from src.utils.logger import logger

def extract_ip(uri):
    match = re.search(r'//([a-zA-Z0-9._-]+)', uri)  # Matches both IP and hostnames
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Invalid URI: {uri}")

def extract_port(uri):
    match = re.search(r":(\d+)$", uri)
    if match:
        return match.group(1)
    return None

# Create a connection to the Neo4j database
class Neo4jGraphDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver( uri, auth=(user, password))
        ip_address = extract_ip(uri)
        port = extract_port(uri)
        config.DATABASE_URL = config.DATABASE_URL = f"bolt://{user}:{password}@{ip_address}:{port}"

    def close(self):
        self._driver.close()

    def query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return list(result)

    def create_node(self, node: StructuredNode):
        try:
            self.session = self._driver.session()
            node.save()
            self.session.close()
            return node
        except RuntimeError as e:
            logger.error(f"Cannot create node with name {node.name}")
            logger.error(e)

    def create_relationship_to(self, node: StructuredNode, relationship):
        try:
            self.session = self._driver.session()
            relationship = RelationshipTo(node, relationship)
            self.session.close()
            return relationship
        except RuntimeError as e:
            logger.error(f"Cannot create relationship {relationship} for node {node.name}")
            logger.error(e)

    def add(self, node: StructuredNode):
        try:
            # Ensure that a node with the same file_name does not exist
            existing_node = self._get_existing_node(node)
            if existing_node:
                # If node exists, update it (optional, based on your use case)
                for key, value in node.__dict__.items():
                    setattr(existing_node, key, value)
                existing_node.save()
                logger.info(f"Node with {node.file_name} updated.")
                return existing_node
            else:
                # If node doesn't exist, create a new one
                node.save()
                logger.info(f"Node with {node.file_name} created.")
                return node
        except RuntimeError as e:
            logger.error(f"Error adding data to node: {node.file_name}")
            logger.error(e)
            return None

    def _get_existing_node(self, node: StructuredNode):
        """Check for existing node by file_name to prevent duplicates"""
        try:
            # Ensure that the node with the same file_name does not exist
            return node.__class__.nodes.get(file_name=node.file_name)
        except node.__class__.DoesNotExist:
            return None

    def get(self, node: StructuredNode):
        try:
            self.session = self._driver.session()
            all_nodes = node.nodes.all()
            self.session.close()
            return all_nodes
        except RuntimeError as e:
            logger.error(f"Getting data from node")
            logger.error(e)

    def delete_orphan_nodes(self):
        try:
            query = """
            MATCH (n)
            WHERE NOT (n)-[]-()
            DELETE n
            """
            db.cypher_query(query, {})
            print("Orphan nodes deleted successfully.")
        except Exception as e:
            print(f"Error occurred: {e}")

    def add_graph_documents(self, graph_documents):
        ''' Add graph documents to the Neo4j database '''
        try:
            for graph_document in graph_documents:
                for node in graph_document.nodes:
                    self.add(node)
                for relationship in graph_document.relationships:
                    self.create_relationship_to(relationship.start_node, relationship.rel_type)
            logger.info("Graph documents added successfully.")
        except Exception as e:
            logger.error("Error adding graph documents")
            logger.error(e)

    # Function to add document to Neo4j
    def add_document_to_neo4j(self, doc):
        """Add a DocumentNode to Neo4j after checking for duplicates"""
        # Check if a DocumentNode with the same content already exists
        existing_node = self._get_existing_document_node(doc)
        if existing_node:
            logger.info(f"Document with similar content already exists: {existing_node}")
            return existing_node
        else:
            # If not, create a new DocumentNode
            document_node = DocumentNode(page_content=doc.page_content, metadata=doc.metadata).save()
            logger.info(f"DocumentNode created: {document_node}")
            return document_node

    def _get_existing_document_node(self, doc):
        """Check for existing DocumentNode based on content"""
        try:
            return DocumentNode.nodes.get(page_content=doc.page_content)
        except DocumentNode.DoesNotExist:
            return None

    def add_csv_row(self, rows,filenode):
        graph_documents = []
        if rows is not None:
            # Iterate over the list of documents
            for row in rows:
                # Ensure that the document is of the right type (Document from LangChain)
                if not isinstance(row, Document):
                    raise TypeError("Expected a LangChain Document object")
                
                # Add the document to the graph (ensuring no duplicates)
                if row is not None:
                   self.add_document_to_neo4j(row)
                   filenode.row.connect(row)

   
