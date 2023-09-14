import logging
import contextlib

from . import argparse

def basic_config(level='INFO', format='%(levelname)s: %(name)s: %(message)s', capture_warnings=True):
    logging.basicConfig(level=getattr(logging, level), format=format)
    logging.captureWarnings(capture_warnings)
    
def basic_parser(**kwargs):
    parser = argparse.default_parser(basic_config, configs={
        'level': dict(opt_str=['--ll', '--log-level'], choices=['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
        'format': dict(opt_str=['--lf', '--log-format']),
    }, **kwargs)
    return parser

def get_logger(name=None):
    return logging.getLogger(name)

@contextlib.contextmanager
def set_level(logger, level):
    current_level = logger.level
    try:
        logger.setLevel(level)
        yield
    finally:
        logger.setLevel(current_level)