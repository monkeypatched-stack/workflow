from neomodel import StructuredNode,StringProperty

class Entity(StructuredNode):
    name = StringProperty(unique=True)
    type = StringProperty()
