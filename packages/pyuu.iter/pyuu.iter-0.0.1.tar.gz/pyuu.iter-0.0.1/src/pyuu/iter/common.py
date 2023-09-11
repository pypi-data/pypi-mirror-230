from collections.abc import Iterable
from collections import deque

def is_iterable(x):
    attrs = ['__next__', '__iter__']
    if any(map(lambda a: hasattr(x,a), attrs)):
        return True



