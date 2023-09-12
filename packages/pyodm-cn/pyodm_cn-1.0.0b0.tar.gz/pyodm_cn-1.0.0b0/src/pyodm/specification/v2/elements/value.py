from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum
from pyodm.xml_definitions.tags.Element import Element


class Value(Element):
    def support_attribute(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.SeqNum]

    def support_children(self) -> list[OdmV2Enum]:
        return []

    def element_name(self) -> OdmV2Enum:
        return OdmV2Enum.Value
