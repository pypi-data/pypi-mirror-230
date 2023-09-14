import itertools

from . import (
    functools,
    pprint,
)

@functools.parametrized
def attrs(cls, *args, **kwargs):
    keys = list(args) + list(kwargs.keys())
    
    if len(set(keys)) != len(keys):
        raise TypeError(f"Overlapping attributes not allowed, but {args=}, {kwargs=}.")
        
    for arg in args:
        if not arg.isidentifier():
            raise TypeError(f"all args must be a valid string identifier, but got {arg=}.")
    
    def __init__(self, *init_args, **init_kwargs):
        if hasattr(cls, "__pre_init__"):
            cls.__pre_init__(self)
        
        if len(init_args) > len(keys):
            raise TypeError(f"__init__ takes {len(args)} to {len(keys)} positional arguments but {len(init_args)} were given")
        
        kwargs.update(init_kwargs)
        
        missing_keys = []
        for key, value in itertools.zip_longest(keys, init_args): # keys is always longer or equal to init_args due to above check
            if value is None:
                if key in kwargs:
                    value = kwargs.pop(key)
                else:
                    missing_keys.append(key)
            else:
                if key in kwargs:
                    raise TypeError(f"__init__ got multiple values for argument '{key}'")
                
            self.__dict__[key] = value
            
        if (n := len(missing_keys)) > 0:
            missing_keys = pprint.pformat_english(*map(repr, missing_keys))
            raise TypeError(f"__init__ missing {n} positional argument{'' if n == 1 else 's'}: {missing_keys}")
        
        if len(kwargs) > 0:
            raise TypeError(f"__init__ got an unexpected keyword argument '{next(iter(kwargs))}'")
            
        if hasattr(cls, "__post_init__"):
            cls.__post_init__(self)

    cls.__init__ = __init__
    return cls

# def init_repr(cls):
#     cls__init__ = cls.__init__
    
#     def __init__(self, *args, **kwargs):
#         cls__init__(self, *args, **kwargs)
#         self.args = args
#         self.kwargs = kwargs
        
#     cls.__init__ = __init__
    
#     def __repr__(self):
#         args = ", ".join(map(repr, self.args))
#         kwargs = ", ".join(f'{k}={repr(v)}' for k, v in self.kwargs.items())
#         return f'{type(self).__name__}({", ".join(filter(None, [args, kwargs]))})'
    
#     cls.__repr__ = __repr__
#     return cls

def attr_repr(cls):
    def __repr__(self):
        attrs = (f'{k}={repr(v)}' for k, v in self.__dict__.items())
        return f'{type(self).__name__}({", ".join(attrs)})'
    
    cls.__repr__ = __repr__
    return cls

def attr_str(cls):
    def __str__(self):
        attrs = (f'{k}={str(v)}' for k, v in self.__dict__.items())
        return f'{type(self).__name__}({", ".join(attrs)})'
    
    cls.__str__ = __str__
    return cls