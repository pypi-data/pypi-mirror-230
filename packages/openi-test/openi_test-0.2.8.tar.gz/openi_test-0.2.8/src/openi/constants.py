import os

OPENI_FOLDER = os.path.join(os.getcwd() + "/.openi")

"""
MAX_CHUNK_CNT = 10000
small file size < 78GiB = 10000 * 1024 * 1024 * 8
"""

SMALL_FILE_SIZE = 1024 * 1024 * 64 * 100
SMALL_FILE_CHUNK_SIZE = 1024 * 1024 * 8
LARGE_FILE_CHUNK_SIZE = 1024 * 1024 * 64
MAX_FILE_SIZE = 1024 * 1024 * 1024 * 200


APP_URL = "https://openi.pcl.ac.cn/api/v1/"

