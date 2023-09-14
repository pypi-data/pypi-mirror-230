import abc
from abc import ABC

from lxml import etree

from pyodm.data_source import DataSource
from pyodm.utils.forest import Forest
from pyodm.xml_definitions.tags.Element import Element


class ODM(ABC):

    def __init__(self):
        self._odm = None

    @property
    def odm(self) -> Forest: return self._odm

    @odm.setter
    def odm(self, source: DataSource):
        self._odm = Forest.transform(source.data())

    @abc.abstractmethod
    def specification(self):
        """
        把 _odm 数据转为 ODM specification的结构
        :return:
        :rtype:
        """
        ...

    @abc.abstractmethod
    def clinical(self) -> Element: ...


def odm_factory(odm_clazz: ODM.__class__, source: DataSource) -> ODM:
    obj = odm_clazz()
    obj.odm = source
    return obj
