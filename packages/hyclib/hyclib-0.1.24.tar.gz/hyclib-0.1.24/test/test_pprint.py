import torch
import numpy as np

import hyclib as lib

def test_pformat():
    d = {'a': torch.Tensor([[1.0,2.0],[3.0,4.0]]), 'b': {'c': np.array([[1.0,2.0],[3.0,4.0]]), 'd': 10.0}}
    expected = "'a':\n    tensor([[1., 2.],\n            [3., 4.]])\n'b':\n    'c':\n        [[1. 2.]\n         [3. 4.]]\n    'd':\n        10.0"
    assert lib.pprint.pformat(d, verbose=True) == expected