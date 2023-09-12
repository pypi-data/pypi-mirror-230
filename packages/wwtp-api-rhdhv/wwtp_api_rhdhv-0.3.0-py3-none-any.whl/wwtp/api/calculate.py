from enum import Enum


def calculate(enum: Enum):
    def decorate(ref):
        setattr(ref, 'calculation', enum)
        return ref
    return decorate
