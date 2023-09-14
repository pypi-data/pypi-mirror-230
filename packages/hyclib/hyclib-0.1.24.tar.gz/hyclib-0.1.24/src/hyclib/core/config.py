import json
import configparser
from importlib import resources
import pathlib
import logging
import os

import platformdirs
import tomli

from . import itertools

logger = logging.getLogger(__name__)

def load(filename):
    filename = str(filename)
    if filename.endswith('.toml'):
        with open(filename, "rb") as f:
            config = tomli.load(f)
    elif filename.endswith('.json'):
        with open(filename, 'r') as f:
            config = json.load(f)
    else:
        raise NotImplementedError()
    
    return config

def dump(config, filename):
    filename = str(filename)
    if filename.endswith('.json'):
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
    else:
        raise NotImplementedError()
        
def package_config_locs(package_name, package_author=None, package_version=None, default_config_path='config.toml'):
    default_config_filename = resources.files(package_name).joinpath(default_config_path)
    
    user_config_filenames = []

    user_config_filenames.append(pathlib.Path(f'{package_name}_config.toml'))
    try:
        path = pathlib.Path(os.environ[f'{package_name.upper()}_CONFIG'])
    except KeyError:
        pass
    else:
        user_config_filenames.append(path if path.is_file() else path / f'{package_name}_config.toml')
    user_config_filenames.append(pathlib.Path(
        platformdirs.user_config_dir(package_name, appauthor=package_author, version=package_version)
    ) / 'config.toml')
    
    return {'default_config': default_config_filename, 'user_configs': user_config_filenames}
        
def load_package_config(*args, **kwargs):
    """
    Loads configs from various config files to be imported and used anywhere in a package.
    This is meant to be used in the top-level __init__.py file in the package.
    
    It first loads default package configs at default_config_path 
    (relative to the top level directory of the package) if such a file exists.
    
    Next, it loads user-defined configs in the following priority, from highest to lowest:
        1. f'{package_name}_config.toml' in the directory in which the top level code is run
        2. f'${package_name.upper()}_CONIFG' if it is a file, f'${package_name.upper()}_CONIFG/{package_name}_config.toml' otherwise
        3. f'{platformdirs.user_config_dir(package_name, appauthor=package_author, version=package_version)}/config.toml'
        
    If there are overlapping configs, the configs from the config file with the higher priority will be used.
    
    Reminder: If you want to add a default config file to your package, remember to set include_package_data=True in setup.py
    to include it in your package distribution.
    """
    filenames = package_config_locs(*args, **kwargs)
    
    default_config_filename = filenames['default_config']
    if default_config_filename.is_file():
        with resources.as_file(default_config_filename) as default_config_file:
            config = load(default_config_file)
        
        logger.debug(f"Loaded default config file at {default_config_filename}.")
    else:
        config = {}

    user_config_filenames = [filename for filename in filenames['user_configs'] if filename.is_file()]
    for filename in reversed(user_config_filenames):
        itertools.dict_update(config, load(filename))

    if len(user_config_filenames) > 0:
        logger.debug(f"Loaded user config files at the following locations from highest to lowest priority: {user_config_filenames}")

    return config
        
# import numpy as np

# def _replace_range_by_list(d, exclude=None):
#     if exclude is None:
#         exclude = []
    
#     for k, v in d.items():
#         if isinstance(v, dict) and k not in exclude:
#             if any([vk not in ['start', 'stop', 'step'] for vk in v.keys()]):
#                 raise ValueError('configuration values cannot be dictionaries, unless it represents a range')
#             d[k] = np.arange(**v).tolist()

# def expand(d):
#     _replace_range_by_list(d, exclude=['zip', 'prod'])
    
#     configs = []
    
#     e = {k: v for k, v in d.items() if k not in ['zip', 'prod']}
#     if len(e) > 0:
#         configs.append(e)
    
#     if 'zip' in d:
#         l = d['zip']
#         if isinstance(l, dict):
#             l = [l]
#         assert isinstance(l, list)

#         for e in l:
#             assert isinstance(e, dict) and len(e) > 0
#             _replace_range_by_list(e)

#             Ns = [len(v) for v in e.values()]
#             N = Ns[0]
#             assert all([N == Ns[0] for N in Ns])

#             configs += [{k: v[i] for k, v in e.items()} for i in range(N)]
    
#     if 'prod' in d:
#         l = d['prod']
#         if isinstance(l, dict):
#             l = [l]
#         assert isinstance(l, list)

#         for e in l:
#             assert isinstance(e, dict)
#             _replace_range_by_list(e)
            
#             for k, v in e.items():
#                 if not isinstance(v, list):
#                     e[k] = [v]

#             ks, vs = zip(*list(e.items())) # gauranteed ks and vs are in same order
#             shape = tuple([len(v) for v in vs])
#             for indices in np.ndindex(shape):
#                 configs.append({k: v[i] for k, v, i in zip(ks, vs, indices)})
            
#     return configs