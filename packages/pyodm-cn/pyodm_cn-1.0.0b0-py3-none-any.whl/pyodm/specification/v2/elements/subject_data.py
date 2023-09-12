from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum
from pyodm.xml_definitions.tags.Element import Element


class SubjectData(Element):

    def support_attribute(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.SubjectKey, OdmV2Enum.TransactionType]

    def support_children(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.InvestigatorRef, OdmV2Enum.SiteRef, OdmV2Enum.StudyEventData, OdmV2Enum.AuditRecord,
                OdmV2Enum.Signature, OdmV2Enum.Annotation, OdmV2Enum.Query]

    def element_name(self) -> OdmV2Enum:
        return OdmV2Enum.SubjectData
