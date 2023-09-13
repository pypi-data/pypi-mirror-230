import pathlib
import signal
import sys
import logging

logger = logging.getLogger(__name__)

#########################################################
### python script containing various context managers ###
#########################################################

class SimulFileHandler:
    """
    A context manager that ensures all the files asscoiated with filenames 
    must coexist. If any one file is missing upon exiting the with block
    (either because of an exception, a SIGTERM, or normal exiting),
    all the files will be deleted.
    """
    def __init__(self, *filenames):
        self.filenames = [pathlib.Path(filename) for filename in filenames]
        
    def cleanup(self):
        if all([filename.is_file() for filename in self.filenames]):
            logger.debug("All files exist. No cleanup needed.")
            return
        logger.debug("Cleaning up...")
        for filename in self.filenames:
            if filename.is_file():
                filename.unlink()
        logger.debug("Finished cleanup.")
        
    def handler(self, signum, frame):
        logger.info(f"Received signal {signal.strsignal(signum)}.")
        sys.exit(0) # This throws the exception SystemExit, which is then caught by __exit__ and triggers self.cleanup()
    
    def __enter__(self):
        self.old_sigterm = signal.signal(signal.SIGTERM, self.handler)
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.info(f"Caught exception {exc_type}: {exc_val}")
        self.cleanup()
        signal.signal(signal.SIGTERM, self.old_sigterm)
