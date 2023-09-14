import traceback
import warnings
import sys
import contextlib

def _warn_with_traceback(message, category, filename, lineno, file=None, line=None):

    log = file if hasattr(file, 'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(message, category, filename, lineno, line))

@contextlib.contextmanager
def warn_with_traceback():
    showwarning = warnings.showwarning
    try:
        warnings.showwarning = _warn_with_traceback
        yield
    finally:
        warnings.showwarning = showwarning