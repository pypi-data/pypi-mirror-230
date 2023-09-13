import os
from ..obs.get_path_obs import download_dataset_obs, download_pretrain_model_obs, download_code_obs
from ..minio.get_path_minio import download_dataset_minio, download_pretrain_model_minio, download_code_minio

def download_code():
    if os.getenv("STORAGE_LOCATION") is None:
    		raise ValueError("环境变量设置失败，请确保设置了STORAGE_LOCATION环境变量。")
    if os.getenv("STORAGE_LOCATION") == "obs":
		    return download_code_obs()
    return download_code_minio()

def download_dataset():
    if os.getenv("STORAGE_LOCATION") is None:
    		raise ValueError("环境变量设置失败，请确保设置了STORAGE_LOCATION环境变量。")
    if os.getenv("STORAGE_LOCATION") == "obs":
		    return download_dataset_obs()
    return download_dataset_minio()

def download_pretrain_model():
    if os.getenv("STORAGE_LOCATION") is None:
    		raise ValueError("环境变量设置失败，请确保设置了STORAGE_LOCATION环境变量。")
    if os.getenv("STORAGE_LOCATION") == "obs":
		    return download_pretrain_model_obs()
    return download_pretrain_model_minio()