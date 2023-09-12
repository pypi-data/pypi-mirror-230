import logging
import os
from ..constants import *

def setup_logging():
    if not os.path.exists(OPENI_FOLDER):
        os.mkdir(OPENI_FOLDER)
    LOG_FORMAT = "%(asctime)s [%(levelname)s] - %(funcName)s() %(lineno)d: %(message)s" # %(filename)s
    DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
    logging.basicConfig(filename=os.path.join(OPENI_FOLDER, "openi.log"), level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)