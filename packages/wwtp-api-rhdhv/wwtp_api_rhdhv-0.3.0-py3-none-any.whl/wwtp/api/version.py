def version(*, major: int, minor: int, patch: int):
    def decorate(ref):
        setattr(ref, 'major', major)
        setattr(ref, 'minor', minor)
        setattr(ref, 'patch', patch)
        return ref
    return decorate
