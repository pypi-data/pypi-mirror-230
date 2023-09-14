import abc
from abc import ABC


class Writer(ABC):
    def __init__(self, file_path: str):
        self.file_path = file_path

    @abc.abstractmethod
    def write(self, element) -> None:
        """
        把 Element 写入文件的抽象方法
        :param element:
        :type element: pyodm.xml_definitions.tags.Element import Element
        :return:
        :rtype:
        """
        ...
