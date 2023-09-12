from abc import ABC
from dataclasses import dataclass


@dataclass
class FlowType(ABC):
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
