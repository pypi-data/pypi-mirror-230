import random
import contextlib

@contextlib.contextmanager
def set_seed(seed):
    python_state = random.getstate()
    random.seed(seed)
    
    try:
        import numpy as np
    except ImportError:
        np_state = None
    else:
        np_state = np.random.get_state()
        np.random.seed(seed)
        
    try:
        import torch
    except ImportError:
        torch_state = None
    else:
        torch_state = torch.random.get_rng_state()
        torch.random.manual_seed(seed)
        
    try:
        yield
    finally:
        random.setstate(python_state)
        
        if np_state is not None:
            np.random.set_state(np_state)
            
        if torch_state is not None:
            torch.random.set_rng_state(torch_state)