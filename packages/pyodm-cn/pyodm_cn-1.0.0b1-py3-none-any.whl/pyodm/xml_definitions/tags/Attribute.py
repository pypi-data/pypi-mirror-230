from dataclasses import dataclass

from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum


@dataclass
class Attribute:
    name: OdmV2Enum
    value: str
