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
    tree[ks.pop()] = val


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
