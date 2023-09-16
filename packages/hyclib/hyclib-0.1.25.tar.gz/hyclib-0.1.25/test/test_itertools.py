import pytest

import hyclib as lib

def bad_iterable():
    yield from [1/0,2,2]

@pytest.mark.parametrize('iterable, expected', [
    (range(0), True),
    (range(1), True),
    (range(2), False),
    ([1,2,1], False),
    ([2,2,2], True),
    (bad_iterable(), ZeroDivisionError),
])
def test_isconst(iterable, expected):
    if not isinstance(expected, bool):
        with pytest.raises(expected):
            lib.itertools.isconst(iterable)
    else:
        assert lib.itertools.isconst(iterable) == expected
        
@pytest.mark.parametrize('iterable, expected', [
    (range(0), True),
    (range(1), False),
    (range(2), False),
    ([], True),
    ([1,2,1], False),
    (bad_iterable(), ZeroDivisionError),
])
def test_isempty(iterable, expected):
    if not isinstance(expected, bool):
        with pytest.raises(expected):
            lib.itertools.isempty(iterable)
    else:
        assert lib.itertools.isempty(iterable) == expected

@pytest.mark.parametrize('s, depth, expected', [
    ([[1,2,[3]],[],(4,5),6], 1, [1,2,[3],4,5,6]),
    ([[1,2,[3]],[],(4,5),6], -1, [1,2,3,4,5,6]),
    (tuple([[1,2,[3]],[],(4,5),6]), -1, (1,2,3,4,5,6)),
])
def test_flatten_seq(s, depth, expected):
    assert str(lib.itertools.flatten_seq(s, depth=depth)) == str(expected)
    
@pytest.fixture
def iterable():
    return [[1,2,[3]],[],(4,5),6]
    
@pytest.mark.parametrize('depth, types, exclude, expected', [
    (0, None, None, [[1,2,[3]],[],(4,5),6]),
    (1, None, None, [1,2,[3],4,5,6]),
    (-1, None, None, [1,2,3,4,5,6]),
    (0, [], None, [[1,2,[3]],[],(4,5),6]),
    (1, [], None, [[1,2,[3]],[],(4,5),6]),
    (-1, [], None, [[1,2,[3]],[],(4,5),6]),
    (0, [list], None, [[1,2,[3]],[],(4,5),6]),
    (1, [list], None, [1,2,[3],(4,5),6]),
    (-1, [list], None, [1,2,3,(4,5),6]),
    (0, None, [list], [[1,2,[3]],[],(4,5),6]),
    (1, None, [list], [[1,2,[3]],[],4,5,6]),
    (-1, None, [list], [[1,2,[3]],[],4,5,6]),
    (0, [], [list], [[1,2,[3]],[],(4,5),6]),
    (1, [], [list], [[1,2,[3]],[],(4,5),6]),
    (-1, [], [list], [[1,2,[3]],[],(4,5),6]),
    (0, [list], [list], [[1,2,[3]],[],(4,5),6]),
    (1, [list], [list], [[1,2,[3]],[],(4,5),6]),
    (-1, [list], [list], [[1,2,[3]],[],(4,5),6]),
    (0, None, [tuple], [[1,2,[3]],[],(4,5),6]),
    (1, None, [tuple], [1,2,[3],(4,5),6]),
    (-1, None, [tuple], [1,2,3,(4,5),6]),
])
def test_deep_iter(iterable, depth, types, exclude, expected):
    for x, y in zip(lib.itertools.deep_iter(iterable, depth=depth, types=types, exclude=exclude), expected):
        assert x == y

@pytest.fixture()
def self_referential():
    out = []

    out.append({
        'iterable': 'abcd',
        'depth': -1,
        'expected': ['a', 'b', 'c', 'd']
    })

    l = [6]
    iterable = [1, 2, 3, [4, 5, l]]
    l.append(iterable) # [1, 2, 3, [4, 5, [6, [...]]]]

    out.append({
        'iterable': iterable,
        'depth': -1,
        'expected': [1, 2, 3, 4, 5, 6, iterable]
    })

    out.append({
        'iterable': iterable,
        'depth': 1,
        'expected': [1, 2, 3, 4, 5, [6, iterable]]
    })

    return out

@pytest.mark.parametrize('idx', list(range(3)))
def test_deep_iter_self_referential(idx, self_referential):
    d = self_referential[idx]
    for x, y in zip(lib.itertools.deep_iter(d['iterable'], depth=d['depth']), d['expected']):
        assert x == y
    
@pytest.mark.parametrize('d, depth, expected', [
    ({'a': {'b': {'c': 'd'}}}, 1, {'a.b': {'c': 'd'}}),
    ({'a': {'b': {'c': 'd'}}}, -1, {'a.b.c': 'd'}),
    ({'abc': {'bcd': {'cde': 'def'}}}, -1, {'abc.bcd.cde': 'def'}),
])
def test_flatten_dict(d, depth, expected):
    assert str(lib.itertools.flatten_dict(d, depth=depth)) == str(expected)
    
@pytest.fixture
def d():
    return {
        'a': 'hi',
        'b': {
            'c': 1,
            'd': 1.0,
            'e': {}
        },
        'f': 'hii'
    }
    
@pytest.mark.parametrize('delimiter, expected', [
    ('.', {'a': 'hi', 'b.c': 1, 'b.d': 1.0, 'f': 'hii'}),
    ('/', {'a': 'hi', 'b/c': 1, 'b/d': 1.0, 'f': 'hii'}),
])
def test_dict_iter(d, delimiter, expected):
    for x, y in zip(lib.itertools.dict_iter(d, delimiter=delimiter), expected.items()):
        assert x == y
    
@pytest.mark.parametrize('d, depth, expected', [
    ({'a.b': {'b': {'c': 'd'}}}, 1, pytest.raises(ValueError)),
    ({'a.b': {'b': {'c': 'd'}}}, -1, pytest.raises(ValueError)),
])
def test_flatten_dict_exceptions(d, depth, expected):
    with expected:
        lib.itertools.flatten_dict(d, depth=depth)
    
@pytest.mark.parametrize('d, keys, value, expected', [
    ({}, ['a', 'b'], 'c', {'a': {'b': 'c'}}),
])
def test_assign_dict(d, keys, value, expected):
    lib.itertools.assign_dict(d, keys, value)
    assert str(d) == str(expected)
    
@pytest.mark.parametrize('enum', [
    False,
    True
])
def test_product(enum):
    l1 = [
        'hi',
        'bye',
    ]
    l2 = [
        3,
        7,
        9,
    ]
    expected_ndindices = [
        (0,0),
        (0,1),
        (0,2),
        (1,0),
        (1,1),
        (1,2),
    ]
    for i, elem in enumerate(lib.itertools.product(l1, l2, enum=enum)):
        if enum:
            ndidx, (e1, e2) = elem
            assert ndidx == expected_ndindices[i]
        else:
            e1, e2 = elem
        assert e1 == l1[expected_ndindices[i][0]]
        assert e2 == l2[expected_ndindices[i][1]]
        
@pytest.mark.parametrize('d1, d2, mode, fillvalue, expected', [
    ({'a': 1, 'b': 2}, {'b': 3, 'a': 4}, 'strict', None, {'a': (1,4), 'b': (2,3)}),
    ({'c': 5, 'a': 1, 'b': 2}, {'b': 3, 'a': 4, 'd': 6}, 'intersect', None, {'a': (1,4), 'b': (2,3)}),
    ({'c': 5, 'a': 1, 'b': 2}, {'d': 6, 'e': 7}, 'intersect', None, {}),
    ({'c': 5, 'a': 1, 'b': 2}, {'b': 3, 'a': 4, 'd': 6}, 'union', None, {'a': (1,4), 'b': (2,3), 'c': (5,None), 'd': (None,6)}),
    ({'c': 5, 'a': 1, 'b': 2}, {'b': 3, 'a': 4, 'd': 6}, 'union', 10, {'a': (1,4), 'b': (2,3), 'c': (5,10), 'd': (10,6)}),
])
def test_dict_zip(d1, d2, mode, fillvalue, expected):
    if mode != 'union':
        d = {k: (v1, v2) for k, v1, v2 in lib.itertools.dict_zip(d1, d2, mode=mode)}
    else:
        d = {k: (v1, v2) for k, v1, v2 in lib.itertools.dict_zip(d1, d2, mode=mode, fillvalue=fillvalue)}
    assert d == expected # no need for order of elemenets to be equal
    
@pytest.mark.parametrize('d1, d2, mode, expected', [
    ({'a': 1, 'b': 2, 'c': 3}, {'b': 3, 'a': 4}, 'strict', pytest.raises(ValueError)),
    ({'a': 1, 'c': 5}, {'b': 3, 'a': 4}, 'strict', pytest.raises(KeyError)),
    ({'a': 1, 'b': 2}, {'c': 5, 'b': 3, 'a': 4}, 'strict', pytest.raises(ValueError)),
    ({'a': 1, 'b': 2}, {'b': 3, 'a': 4}, 'whatever', pytest.raises(NotImplementedError)),
])
def test_dict_zip_exceptions(d1, d2, mode, expected):
    with expected:
        list(lib.itertools.dict_zip(d1, d2, mode=mode))

def test_dict_union():
    d = {
        'options': {
            'max_num_steps': 100,
        }
    }
    new_d = {
        'options': {
            'dtype': 'float32',
        }
    }
    expected = {
        'options': {
            'max_num_steps': 100,
            'dtype': 'float32',
        }
    }
    assert str(lib.itertools.dict_union(d, new_d)) == str(expected)