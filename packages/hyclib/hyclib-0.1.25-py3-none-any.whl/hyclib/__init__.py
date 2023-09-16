from .core import (
    pprint,
    config,
    exceptions,
    argparse,
    logging,
    warnings,
    timeit,
    clstools,
    functools,
    itertools,
    configurable,
    random,
    datetime,
)
    
import importlib
import logging as lg

logger = lg.getLogger(__name__)

modules = [
    '.np',
    '.pt',
    '.sp',
    '.io',
    '.npf',
    '.pd',
    '.plot',
]

for module in modules:
    try:
        importlib.import_module(module, package='hyclib')
    except ImportError as err:
        logger.info(f"Did not import {module=} due to ImportError {str(err)}.")
    
del importlib, modules, module, lg

cfg = config.load_package_config('hyclib')