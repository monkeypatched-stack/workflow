from neomodel import StructuredNode, StringProperty, IntegerProperty, DateTimeProperty, JSONProperty, RelationshipTo
from datetime import datetime
from src.utils.graph import connection
from src.dao.document import DocumentNode

# Define the FileNode model using neomodel
class FileNode(StructuredNode):
    file_name = StringProperty()
    file_type = StringProperty()  # e.g., 'txt', 'pdf', 'csv'
    file_path = StringProperty()  # Full file path
    created_at = DateTimeProperty(default=datetime.now)  # When the file was created
    metadata = JSONProperty()  # Optional metadata, store as JSON
    # Relationship to DocumentNode (can connect to multiple DocumentNodes)
    row = connection.create_relationship_to('DocumentNode', 'BELONGS_TO')
    
    # You can also add other properties as needed
    def __str__(self):
        return f"FileNode(file_name={self.file_name}, file_type={self.file_type})"

# Example usage
def create_file_node(file_name,file_type, file_path, metadata=None):
    file_node = FileNode(
        file_name=file_name,
        file_type=file_type,
        file_path=file_path,
        metadata=metadata or {}
    ).save()
    print(f"FileNode created: {file_node}")
    return file_node