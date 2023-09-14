from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum
from pyodm.xml_definitions.tags.Element import Element


class ODM(Element):
    def support_attribute(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.FileType, OdmV2Enum.Granularity, OdmV2Enum.Context, OdmV2Enum.FileOID, OdmV2Enum.CreationDateTime,
                OdmV2Enum.PriorFileOID, OdmV2Enum.AsOfDateTime, OdmV2Enum.ODMVersion, OdmV2Enum.Originator,
                OdmV2Enum.SourceSystem, OdmV2Enum.SourceSystemVersion]

    def support_children(self) -> list[OdmV2Enum]:
        return [OdmV2Enum.Description, OdmV2Enum.Study, OdmV2Enum.AdminData,
                OdmV2Enum.ReferenceData, OdmV2Enum.ClinicalData, OdmV2Enum.Association]

    def element_name(self) -> OdmV2Enum:
        return OdmV2Enum.ODM
