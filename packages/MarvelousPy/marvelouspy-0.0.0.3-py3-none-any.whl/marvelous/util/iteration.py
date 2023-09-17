import sys
from collections.abc import Iterable



class Literable(Iterable):
    """Expose list casting from iterator instance."""
    def __init__(self, it):
        super(self, it)

    def as_list(self):
        return [item for item in self]

def nloop(it1, it2, op):
    while it1 and it2:
        yield op(it1, it2)

# for x in c1, y in c2




def itslice(iterator, *args):
    slice_indices = slice(args)
    start, stop, step = slice_indices.start or 0, slice_indices.stop or sys.maxsize, slice_indices.step or 1
    num_items = 3
    return [item for i, item in zip(range(num_items), iterator)]


