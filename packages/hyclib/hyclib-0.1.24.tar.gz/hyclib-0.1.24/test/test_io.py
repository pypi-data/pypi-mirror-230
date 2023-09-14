import pathlib

import hyclib as lib

def test_save_load(tmp_path):
    A = {'abc': 'bcd', 'abcde': {'cde': 'def'}}
    
    # data_path = pathlib.Path('/home/hc3190/lib/test/data')
    # lib.io.save_data(data_path, A)
    
    lib.io.save_data(tmp_path, A)
    new_A = lib.io.load_data(tmp_path)
    assert lib.itertools.flatten_dict(A) == lib.itertools.flatten_dict(new_A)
    
def test_save_load_2(tmp_path):
    A = {'abc': 'bcd', 'abcde': {'cde': 'def'}}
    
    # data_path = pathlib.Path('/home/hc3190/lib/test/data')
    # data_path = data_path / 'test_data.pkl'
    # lib.io.save_data(data_path, A)
    
    tmp_path = tmp_path / 'test_data.pkl'
    lib.io.save_data(tmp_path, A)
    new_A = lib.io.load_data(tmp_path)
    assert lib.itertools.flatten_dict(A) == lib.itertools.flatten_dict(new_A)