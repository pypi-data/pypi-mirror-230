from portmod._cli.merge import CLIMerge
from portmod.merge import merge as generic_merge


def merge(*args, **kwargs):
    generic_merge(*args, io=CLIMerge(), **kwargs)
