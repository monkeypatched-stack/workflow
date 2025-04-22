from neomodel import StructuredNode,JSONProperty

class DocumentNode(StructuredNode):
    page_content = JSONProperty()
    metadata = JSONProperty()