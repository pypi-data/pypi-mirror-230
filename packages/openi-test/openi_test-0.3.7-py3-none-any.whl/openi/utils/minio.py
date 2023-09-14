import os
def get_code_path_minio():
    """
    获取源代码存储在minio,挂载到镜像后的代码路径
    """
    code_path = os.getenv("CODE_PATH")
    if code_path is None:
    	raise ValueError("Failed to get the environment variable, please ensure that the CODE_PATH environment variable has been set.")
    return code_path 
def get_data_path_minio():
    """
    获取源数据集存储在minio,挂载到镜像后的数据集路径
    """
    data_path = os.getenv("DATA_PATH")
    if data_path is None:
    	raise ValueError("Failed to get the environment variable, please ensure that the DATA_PATH environment variable has been set.")
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