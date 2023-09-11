from .common import *

def dfs1(n, leaf_only=True):
    '''
    example:
    list(dfs1([1,[2,3],4,[5],6])) == [1, 2, 3, 4, 5, 6]
    '''
    if(not is_iterable(n)):
        yield n
    else:
        if not leaf_only:
            yield n
        for n_ in n:
            yield from dfs1(n_, leaf_only)


def dfs2(n, is_leaf, leaf_only=True):
    '''
    exmaple:
    list(dfs2(['01', ['02','03'], '04', ['05'], '06'], lambda n: type(n) == str)) 
    == ['01', '02', '03', '04', '05', '06']
    '''
    if is_leaf(n):
        yield n
    else:
        if not leaf_only:
            yield n
        for n_ in n:
            yield from dfs2(n_, is_leaf, leaf_only)

def dfs3(n, get_sons, leaf_only=True):
    '''
    example:
    dfs([1, [2, 3], 4, [5], 6], reversed)) == [6, 5, 4, 3, 2, 1]
    '''
    if(not is_iterable(n)):
        yield n
    else:
        if not leaf_only:
            yield n
        for n_ in get_sons(n):
            yield from dfs3(n_, get_sons, leaf_only)


def dfs4(n, get_sons, is_leaf, leaf_only=True):
    '''
    example:
    (list(dfs(['01', ['02', '03'], '04', ['05'], '06'], reversed, lambda n: type(n) == str)) 
    == ['06', '05', '04', '03', '02', '01']
    '''
    if(is_leaf(n)):
        yield n
    else:
        if not leaf_only:
            yield n
        for n_ in get_sons(n):
            yield from dfs4(n_, get_sons, is_leaf, leaf_only)

def dfs(n, get_sons = None, is_leaf = None, leaf_only=True):
    '''
    depth first search by preorder
    example:
    (list(dfs(['01', ['02', '03'], '04', ['05'], '06'], reversed, lambda n: type(n) == str)) 
    == ['06', '05', '04', '03', '02', '01']
    '''
    if get_sons is None and is_leaf is None:
        yield from dfs1(n,leaf_only)
    elif get_sons is None:
        yield from dfs2(n, is_leaf,leaf_only)
    elif is_leaf is None:
        yield from dfs3(n, get_sons,leaf_only)
    else:
        yield from dfs4(n, get_sons, is_leaf,leaf_only)



