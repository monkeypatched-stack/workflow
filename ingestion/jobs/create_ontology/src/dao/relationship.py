from neomodel import StructuredNode,RelationshipTo

class Relationship(StructuredNode):
    from_node = RelationshipTo('Entity', 'RELATES_TO')
    to_node = RelationshipTo('Entity', 'RELATES_TO')