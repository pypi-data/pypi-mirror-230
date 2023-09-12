from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum
from pyodm.xml_definitions.tags.Element import Element


class ClinicalData(Element):
    # def required_children(self) -> list[OdmV2]:
    #     return [OdmV2.SubjectData, OdmV2.ItemGroupData,]

    def support_attribute(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.StudyOID, OdmV2Enum.MetaDataVersionOID]

    def support_children(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.SubjectData, OdmV2Enum.ItemGroupData, OdmV2Enum.AuditRecord,
                OdmV2Enum.Signature, OdmV2Enum.Annotation, OdmV2Enum.Query]

    def element_name(self) -> OdmV2Enum:
        return OdmV2Enum.ClinicalData

