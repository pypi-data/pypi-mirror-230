import pytest

import hyclib as lib

def test_logging():
    # just ensure there is no error, I don't know how to write tests for this
    parser = lib.logging.basic_parser()
    args = parser.parse_args([])
    lib.logging.basic_config(**vars(args))