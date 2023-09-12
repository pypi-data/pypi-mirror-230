import abc
from abc import ABC
from lxml import etree

from pyodm.io.writer import Writer
from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum
from pyodm.xml_definitions.tags.Attribute import Attribute


class Element(ABC):
    def __init__(self):
        self.attributes = {}
        self.child_elements: list[Element] = []
        self._parent_element = None
        self._xml_element = etree.Element(self.element_name().value)
        self._text = None

    @property
    def parent_element(self):
        return self._parent_element

    def has_parent(self):
        return self._parent_element is not None

    def has_child(self):
        return self.child_elements is not None and len(self.child_elements) != 0

    def has_attribute(self, attr: Attribute):
        if attr.name in self.attributes.keys(): return True
        return False

    @parent_element.setter
    def parent_element(self, value):
        self._parent_element = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def has_text(self):
        return self._text is not None and len(self._text) > 0

    @property
    def xml_element(self):
        return self._xml_element

    @abc.abstractmethod
    def element_name(self) -> OdmV2Enum:
        ...

    @abc.abstractmethod
    def support_attribute(self) -> list[OdmV2Enum]:
        ...

    @abc.abstractmethod
    def support_children(self) -> list[OdmV2Enum]:
        ...

    # @abc.abstractmethod
    # def required_children(self) -> list[OdmV2]:
    #     ...

    def add_attribute(self, attribute: Attribute):
        if attribute.name not in self.support_attribute():
            raise Exception(f'{self.element_name().value} do not support {attribute.name.value}')
        if self.has_attribute(attribute): raise Exception(f'Attribute {attribute.name.value} is exist')
        self.attributes[attribute.name.value] = attribute

    def add_child(self, element):
        if element.element_name() not in self.support_children():
            raise Exception(f'{self.element_name().value} do not support {element.element_name().value}')
        element.parent_element = self
        self.child_elements.append(element)

    def xml(self, parent_xml_element=None):
        if self.has_parent():
            element = etree.SubElement(parent_xml_element, self.element_name().value)
        else:
            element = etree.Element(self.element_name().value)

        for attribute in self.attributes.values():
            element.attrib[attribute.name.value] = attribute.value

        if self.has_text():
            element.text = self.text

        for child_element in self.child_elements:
            child_element.xml(parent_xml_element=element)
        return element
        # child.text = "Hello, XML!"
        # tree = etree.ElementTree(root)
        # tree.write("output.xml", pretty_print=True, encoding="utf-8")

    def export(self, writer: Writer):
        writer.write(self)

