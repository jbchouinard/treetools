from copy import deepcopy


def get_keys(struct):
    if isinstance(struct, list) or isinstance(struct, tuple):
        return range(len(struct))
    elif isinstance(struct, dict):
        return struct.keys()
    else:
        raise TypeError('get_keys not applicable to type %s' % type(struct))


def iterleaves(tree):
    _type = type(tree)

    def leaves_recur(node):
        for k in get_keys(node):
            v = node[k]
            if isinstance(v, _type):
                for v in leaves_recur(v):
                    yield v
            else:
                yield v

    for v in leaves_recur(tree):
        yield v


def leaves(tree):
    return list(iterleaves(tree))


def iterbranches(tree):
    _type = type(tree)

    def branches_recur(path, node):
        for k in get_keys(node):
            v = node[k]
            newpath = path + [k]
            if isinstance(v, _type):
                for p in branches_recur(newpath, v):
                    yield p
            else:
                yield tuple(newpath)

    for p in branches_recur([], tree):
        yield p


def branches(tree):
    return list(iterbranches(tree))


def map(func, tree):
    _type = type(tree)

    def map_recur(node):
        for k in get_keys(node):
            v = node[k]
            if isinstance(v, _type):
                map_recur(v)
            else:
                node[k] = func(v)

    map_recur(tree)


def mapped(func, tree):
    newtree = deepcopy(tree)
    map(func, newtree)
    return newtree


_GET_RAISE = []

def get(tree, keys, default=_GET_RAISE):
    ks = list(keys)
    while (ks):
        try:
            tree = tree[ks.pop(0)]
        except KeyError as e:
            if default is _GET_RAISE:
                raise e
            else:
                return default
    return tree


def put(tree, keys, val, force=False):
    _type = type(tree)
    ks = list(keys)
    while (len(ks) > 1):
        k = ks.pop(0)
        try:
            tree = tree[k]
        except KeyError:
            if force:
                tree[k] = _type()
                tree = tree[k]
            else:
                raise
        except IndexError:
            if force:
                n = k - len(tree) + 1
                tree += [[] for _ in range(n)]
                tree = tree[k]
            else:
                raise
    k = ks.pop()
    try:
        tree[k] = val
    except IndexError:
        if force:
            n = k - len(tree) + 1
            tree += [None for _ in range(n)]
            tree[k] = val
        else:
            raise


class nesteddict(dict):

    def __getitem__(self, k):
        if isinstance(k, tuple):
            if len(k) == 1:
                try:
                    return self.__getitem__(k[0])
                except KeyError:
                    raise KeyError(k)
            else:
                newd = False
                try:
                    d = self.__getitem__(k[0])
                except KeyError:
                    d = nesteddict()
                    newd = True
                    self.__setitem__(k[0], d)
                try:
                    return d.__getitem__(k[1:])
                except KeyError as e:
                    if newd:
                        del self[k[0]]
                        raise KeyError(k[:1])
                    else:
                        raise KeyError(k[:1] + e.args[0])
        else:
            return super(nesteddict, self).__getitem__(k)

    def __setitem__(self, k, v):
        if isinstance(k, tuple):
            if len(k) == 1:
                try:
                    return self.__setitem__(k[0], v)
                except KeyError:
                    raise KeyError(k)
            else:
                try:
                    d = self.__getitem__(k[0])
                except KeyError:
                    d = nesteddict()
                    self.__setitem__(k[0], d)
                return d.__setitem__(k[1:], v)
        else:
            return super(nesteddict, self).__setitem__(k, v)


if __name__ == '__main__':
    tree1 = {1: {'foo': 'bar'}, 2: {'baz': 'bang'}}
    assert set(iterleaves(tree1)) == {'bar', 'bang'}
    assert set(iterbranches(tree1)) == {(1, 'foo'), (2, 'baz')}
    assert set(iterleaves(mapped(lambda x: x[0], tree1))) == {'b'}

    tree2 = [[1, 2], [3, 4], [5]]
    assert leaves(tree2) == [1, 2, 3, 4, 5]
    assert branches(tree2) == [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
    assert mapped(lambda x: x*3, tree2) == [[3, 6], [9, 12], [15]]

    tree3 = {}
    put(tree3, ('foo', 'bar', 'baz'), 55, force=True)
    assert get(tree3, ('foo', 'bar', 'baz')) == 55
    assert get(tree3, ('foo', 'bang', 'boo'), default=12) == 12

    tree4 = ((), ('foo', 'bar'), (1, 2, 3))
    assert leaves(tree4) == ['foo', 'bar', 1, 2, 3]
