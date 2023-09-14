from .obs import get_code_path_obs, get_data_path_obs, get_pretrain_model_path_obs, get_output_path_obs, push_output_to_openi_obs
from .minio import get_code_path_minio,get_data_path_minio,get_pretrain_model_path_minio,get_output_path_minio
def get_code_path():
    """
    获取代码路径
    """
    if os.getenv("STORAGE_LOCATION") is None:
    	raise ValueError("Failed to get the environment variable, please ensure that the STORAGE_LOCATION environment variable has been set.")
    if os.getenv("STORAGE_LOCATION") == "obs":
        return get_code_path_obs
    return get_code_path_minio
def get_data_path():
    """
    获取数据集路径
    """
    if os.getenv("STORAGE_LOCATION") is None:
    	raise ValueError("Failed to get the environment variable, please make sure the STORAGE_LOCATION environment variable has been set")
    if os.getenv("STORAGE_LOCATION") == "obs":
        return get_data_path_obs
    return get_data_path_minio
def get_pretrain_model_path():
    """
    获取预训练模型路径
    """
    if os.getenv("STORAGE_LOCATION") is None:
    	raise ValueError("Failed to get the environment variable, please make sure the STORAGE_LOCATION environment variable has been set.")
    if os.getenv("STORAGE_LOCATION") == "obs":
        return get_pretrain_model_path_obs
    return get_pretrain_model_path_minio
def get_output_path():
    """
    获取输出路径
    """
    if os.getenv("STORAGE_LOCATION") is None:
    	raise ValueError("Failed to get the environment variable, please make sure the STORAGE_LOCATION environment variable has been set.")
    if os.getenv("STORAGE_LOCATION") == "obs":
        return get_output_path_obs
    return get_output_path_minio
def push_output_to_openi():
    """
    推送输出结果到启智平台
    """
    if os.getenv("STORAGE_LOCATION") is None:
    	raise ValueError("Failed to get the environment variable, please make sure the STORAGE_LOCATION environment variable has been set.")
    if os.getenv("STORAGE_LOCATION") == "obs":
    		return push_output_to_openi_obs
    return