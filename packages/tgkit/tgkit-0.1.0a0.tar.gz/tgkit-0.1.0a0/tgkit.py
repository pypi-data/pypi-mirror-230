from abc import abstractmethod
from typing import Optional, Union

# import networkx as nx
# from torch_geometric.data import Data

class TemporalGraphKit(object):

    @abstractmethod
    def __init__(self):
        """ Abstract method for "DIY" implementations. """

    @staticmethod
    def read_static(
        data,
    ) -> None:
        """ Returns a Static Graph (`G`). """
        raise NotImplementedError(
            "Missing `read_static` implementation. "
            "Please check back the project repository soon!"
        )

    @staticmethod
    def read_temporal(
        data,
    ) -> None:
        """ Returns a Temporal Graph (`TG`). """
        raise NotImplementedError(
            "Missing `read_temporal` implementation. "
            "Please check back the project repository soon!"
        )

    @staticmethod
    def to_discrete(
        data,
        time: Optional[Union[list, float, int]],
    ) -> None:
        """ Returns a Discrete Temporal Graph (`DTG`). """
        raise NotImplementedError(
            "Missing `to_discrete` implementation. "
            "Please check back the project repository soon!"
        )

    @staticmethod
    def to_continuous(
        data,
        time: Optional[Union[list, float, int]],
    ) -> None:
        """ Returns a Continuous Temporal Graph (`CTG`). """
        raise NotImplementedError(
            "Missing `to_continuous` implementation. "
            "Please check back the project repository soon!"
        )


tgkit = TemporalGraphKit
