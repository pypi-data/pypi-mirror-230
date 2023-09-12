import os
from ..obs.get_path_obs import  push_output_to_openi_obs
from ..minio.get_path_minio import push_output_to_openi_minio

def push_output_to_openi():
    """
    推送输出结果到启智平台
    """
    if os.getenv("STORAGE_LOCATION") is None:
    	raise ValueError("Failed to get the environment variable, please make sure the STORAGE_LOCATION environment variable has been set.")
    if os.getenv("STORAGE_LOCATION") == "obs":
    		return push_output_to_openi_obs()
    return push_output_to_openi_minio()