from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum
from pyodm.xml_definitions.tags.Element import Element


class ItemGroupData(Element):
    def support_attribute(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.ItemGroupOID, OdmV2Enum.ItemGroupRepeatKey, OdmV2Enum.TransactionType,
                OdmV2Enum.ItemGroupDataSeq]

    def support_children(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.ItemGroupData, OdmV2Enum.ItemData, OdmV2Enum.AuditRecord, OdmV2Enum.Signature,
                OdmV2Enum.Annotation, OdmV2Enum.Query]

    def element_name(self) -> OdmV2Enum:
        return OdmV2Enum.ItemGroupData
