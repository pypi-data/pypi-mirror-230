import abc
from abc import ABC


class DataSource(ABC):

    @abc.abstractmethod
    def data(self) -> list[list[dict]]: ...
