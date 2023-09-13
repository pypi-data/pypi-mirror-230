import os
from ..obs.get_path_obs import  upload_output_obs
from ..minio.get_path_minio import upload_output_minio

def upload_output():
    """
    推送输出结果到启智平台
    """
    if os.getenv("STORAGE_LOCATION") is None:
    	raise ValueError("Failed to get the environment variable, please make sure the STORAGE_LOCATION environment variable has been set.")
    if os.getenv("STORAGE_LOCATION") == "obs":
    		return upload_output_obs()
    return upload_output_minio()