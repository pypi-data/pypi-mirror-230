import pickle

import hyclib as lib

class hi:
    def __call__(self, a, b, c, d, e, f):
        return f'{a=}, {b=}, {c=}, {d=}, {e=}, {f=}'
        
    def __repr__(self):
        return "HI"
    
def test_rpartial():
    rhi = lib.functools.rpartial(hi(), 1, d=4)

    assert repr(rhi) == 'rpartial(HI, 1, d=4)'
    assert rhi(2, 3, e=5, f=6) == 'a=2, b=3, c=1, d=4, e=5, f=6'

    rhi2 = pickle.loads(pickle.dumps(rhi))
    
    assert repr(rhi2) == 'rpartial(HI, 1, d=4)'
    assert rhi2(2, 3, e=5, f=6) == 'a=2, b=3, c=1, d=4, e=5, f=6'

    rrhi = lib.functools.rpartial(rhi, 2, e=5)

    assert repr(rrhi) == 'rpartial(HI, 2, 1, d=4, e=5)'
    assert rrhi(3, f=6) == 'a=3, b=2, c=1, d=4, e=5, f=6'