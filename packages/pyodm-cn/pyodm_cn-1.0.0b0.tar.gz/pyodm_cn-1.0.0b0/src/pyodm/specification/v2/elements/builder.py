from pyodm.xml_definitions.tags import Attribute
from pyodm.xml_definitions.tags import Element


class Builder:
    def __init__(self):
        self._attributes = []
        self._text = None
        self._children = []

    def attributes(self, attributes: list[Attribute]):
        self._attributes = attributes + self._attributes
        return self

    def text(self, text):
        self._text = text
        return self

    def children(self, children: list):
        self._children = children + self._children
        return self

    def build(self, clazz: Element.__class__) -> Element:
        new_instance = clazz()
        for attribute in self._attributes:
            new_instance.add_attribute(attribute)
        for child in self._children:
            new_instance.add_child(child)
        if self._text is not None: new_instance.text = self._text
        return new_instance
