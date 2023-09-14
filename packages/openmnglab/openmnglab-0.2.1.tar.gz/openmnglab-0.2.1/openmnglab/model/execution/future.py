from abc import ABC, abstractmethod

from openmnglab.model.execution.interface import IExecutor
from openmnglab.model.planning.interface import IDataReference


class IBoundData(IDataReference, ABC):

    @abstractmethod
    @property
    def executor(self) -> IExecutor:
        ...

    @abstractmethod
    def get(self):
        ...
