from lxml import etree

from pyodm.io.writer import Writer
from pyodm.xml_definitions.tags.Element import Element


class XmlWriter(Writer):
    def write(self, element: Element):
        dump_tree = etree.ElementTree(element=element.xml())
        dump_tree.write(self.file_path, pretty_print=True, encoding="utf-8")
