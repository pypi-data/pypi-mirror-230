import os
def get_code_path_minio():
    """
    获取源代码存储在minio,挂载到镜像后的代码路径
    """
    code_path = os.getenv("CODE_PATH")
    if code_path is None:
    	raise ValueError("Failed to get the environment variable, please ensure that the CODE_PATH environment variable has been set.")
    return code_path 

def get_dataset_path_minio():
    """
    获取源数据集存储在minio,挂载到镜像后的数据集路径
    """
    dataset_path = os.getenv("DATASET_PATH")
    if data_path is None:
    	raise ValueError("Failed to get the environment variable, please ensure that the DATASET_PATH environment variable has been set.")
    return data_path 

def get_pretrain_model_path_minio():
    """
    获取源预训练模型存储在minio,挂载到镜像后的预训练模型路径
    """
    pretrain_model_path = os.getenv("PRETRAIN_MODEL_PATH")
    if pretrain_model_path is None:
    	raise ValueError("Failed to get the environment variable, please make sure the PRETRAIN_MODEL_PATH environment variable has been set.")
    return pretrain_model_path 
    
def get_output_path_minio():
    """
    获取需要存储在minio的输出路径
    """    
    output_path = os.getenv("OUTPUT_PATH")
    if output_path is None:
    	raise ValueError("Failed to get the environment variable, please ensure that the OUTPUT_PATH environment variable has been set.")
    return output_path

def download_code_minio():
    code_path = os.getenv("CODE_PATH")
    if code_path is None:
    		raise ValueError("环境变量获取失败，请确保设置了CODE_PATH环境变量。")
    return code_path 

def download_dataset_minio():
    dataset_path = os.getenv("DATASET_PATH")
    if data_path is None:
    		raise ValueError("环境变量获取失败，请确保设置了DATASET_PATH环境变量。")
    return data_path 
    
def download_pretrain_model_minio():
    pretrain_model_path = os.getenv("PRETRAIN_MODEL_PATH")
    if pretrain_model_path is None:
    		raise ValueError("环境变量获取失败，请确保设置了PRETRAIN_MODEL_PATH环境变量。")
    return pretrain_model_path     

def upload_output_minio():
    output_path = os.getenv("OUTPUT_PATH")
    if output_url is None or output_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了OUTPUT_PATH环境变量。")
    return output_path     