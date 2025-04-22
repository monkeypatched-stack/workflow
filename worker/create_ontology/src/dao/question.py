from neomodel import StructuredNode, StringProperty

# Define the FileNode model using neomodel
class Question(StructuredNode):
    question = StringProperty()
