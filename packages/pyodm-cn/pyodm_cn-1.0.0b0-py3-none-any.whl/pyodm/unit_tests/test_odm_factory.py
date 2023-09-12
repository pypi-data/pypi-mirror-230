from abc import ABC

from lxml import etree

from pyodm.io.xml_writer import XmlWriter
from pyodm.odm import odm_factory, ODM
from pyodm.data_source import DataSource
from pyodm.specification.v2.elements.clinical_data import ClinicalData
from pyodm.specification.v2.elements.study_event_data import StudyEventData
from pyodm.specification.v2.elements.subject_data import SubjectData
from pyodm.xml_definitions.enums.odm_v2_enum import OdmV2Enum
from pyodm.xml_definitions.tags.Attribute import Attribute
from pyodm.xml_definitions.tags.Element import Element


class TestSource(DataSource):
    def data(self) -> list[list[dict]]:
        return [
            [dict(id=1), dict(id=2), dict(id=5)],
            [dict(id=1), dict(id=3)],
            [dict(id=1), dict(id=4)]
        ]


class TestODM(ODM):
    def clinical(self) -> Element:
        return self.clinical_data

    def __init__(self):
        super().__init__()
        self.clinical_data = ClinicalData()

    def specification(self):
        for subject_name in self.odm.get_level_nodes(1):
            subject = SubjectData()
            subject.add_attribute(Attribute(OdmV2Enum.SubjectKey, value=str(subject_name.get("id"))))
            for visit in self.odm.get_level_nodes(2):
                study_event = StudyEventData()
                study_event.add_attribute(Attribute(OdmV2Enum.StudyEventOID, value=str(visit.get("id"))))
                subject.add_child(study_event)
            self.clinical_data.add_child(subject)


def test_odm_factory():
    test_data = odm_factory(TestODM, TestSource())
    test_data.specification()
    test_data.clinical().export(XmlWriter("TestODM.xml"))
    assert test_data.odm.degree == 3
