from .common import *

class TreeIter:
    '''
    search with record of path
    '''
    def __init__(self, root, get_sons = iter, is_leaf = lambda x: not is_iterable(x)):
        self.path = [root]
        self.get_sons = get_sons
        self.is_leaf = is_leaf

    @property
    def root(self):
        '''firt node of path'''
        return self.path[0]

    @root.setter
    def root(self,x):
        self.path[0] = x

    @property
    def cur(self):
        '''last node of path'''
        return self.path[-1]

    @cur.setter
    def cur(self,x):
        self.path[-1] = x

    @property
    def deepth(self):
        '''deepth of current path'''
        return len(self.path) -1


    def dfs(self):
        '''dfs preorder'''
        cur = self.cur
        is_leaf = self.is_leaf
        yield cur
        if is_leaf(cur):
            return

        path = self.path
        get_sons = self.get_sons
        path.append(None)
        for n in get_sons(cur):
            path[-1] = n
            yield from self.dfs()
        path.pop()

    def bfs(self):
        cur = self.cur
        is_leaf = self.is_leaf
        get_sons = self.get_sons
        path = self.path
        yield cur
        if is_leaf(cur):
            return

        q = deque()
        q.append(cur)
        prnt_num = 1
        sons_num = 0
        path.append(None)
        while len(q):
            for n_ in get_sons(q.popleft()):
                sons_num+=1
                cur = n_
                yield n_
                if is_leaf(n_):
                    continue
                else:
                    q.append(n_)
            prnt_num-=1
            if prnt_num == 0:
                # next level
                prnt_num = sons_num
                sons_num = 0
                path.append(None)
        self.path = path[0:]

