from enum import Enum


def calculate(enum: Enum):
    def decorate(ref):
        setattr(ref, 'enum', enum)
        return ref
    return decorate
