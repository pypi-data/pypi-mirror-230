from .common import *

def bfs1(n):
    q = deque()
    q.append(n)

    while len(q):
        for n_ in q.popleft():
            if is_iterable(n_):
                q.append(n_)
            else:
                yield n_

def bfs2(n, is_leaf):
    q = deque()
    q.append(n)

    while len(q):
        for n_ in q.popleft():
            if is_leaf(n_):
                yield n_
            else:
                q.append(n_)


def bfs3(n, get_sons):
    q = deque()
    q.append(n)

    while len(q):
        for n_ in get_sons(q.popleft()):
            if is_iterable(n_):
                q.append(n_)
            else:
                yield n_


def bfs4(n, get_sons, is_leaf):
    q = deque()
    q.append(n)

    while len(q):
        for n_ in get_sons(q.popleft()):
            if is_leaf(n_):
                yield n_
            else:
                q.append(n_)

def bfs(n, get_sons = None, is_leaf = None):
    if get_sons == None and is_leaf == None:
        yield from bfs1(n)
    elif get_sons == None:
        yield from bfs2(n, is_leaf)
    elif is_leaf == None:
        yield from bfs3(n, get_sons)
    else:
        yield from bfs4(n, get_sons, is_leaf)