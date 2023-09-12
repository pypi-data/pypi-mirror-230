import os
from .env_check import openi_multidataset_to_env, c2net_multidataset_to_env, pretrain_to_env, env_to_openi
#需要定义传给modelarts的两个参数data_url和train_url或是使用args, unknown = parser.parse_known_args()来规避超参数没定义的报错
def get_code_path_obs():
    cluster = os.getenv("CLUSTER")
    code_url = os.getenv("CODE_URL")
    code_path = os.getenv("CODE_PATH")
    if cluster is None or data_url is None or data_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 CLUSTER、CODE_URL 和 CODE_PATH 环境变量。")
    return code_path    

def get_data_path_obs():
    cluster = os.getenv("CLUSTER")
    data_url = os.getenv("DATA_URL")
    data_path = os.getenv("DATA_PATH")
    if cluster is None or data_url is None or data_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 CLUSTER、DATA_URL 和 DATA_PATH 环境变量。")
    return data_path

def get_pretrain_model_path_obs():
    pretrain_model_url = os.getenv("PRETRAIN_MODEL_URL")
    pretrain_model_path= os.getenv("PRETRAIN_MODEL_PATH")
    if pretrain_model_url is None or pretrain_model_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 PRETRAIN_MODEL_URL、PRETRAIN_MODEL_PATH环境变量。")
    return pretrain_model_path

def get_output_path_obs():
    output_path = os.getenv("OUTPUT_PATH")
    if output_path is None:
    		raise ValueError("环境变量获取失败，请确保设置了OUTPUT_PATH环境变量。")
    return output_path 

def download_dataset_obs():
    cluster = os.getenv("CLUSTER")
    data_url = os.getenv("DATA_URL")
    data_path = os.getenv("DATA_PATH")
    if cluster is None or data_url is None or data_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 CLUSTER、DATA_URL 和 DATA_PATH 环境变量。")
    if cluster == "c2net":
		    c2net_multidataset_to_env(data_url, data_path)
    else:
		    openi_multidataset_to_env(data_url, data_path)
    return data_path 

def download_pretrain_model_obs():
    pretrain_model_url = os.getenv("PRETRAIN_MODEL_URL")
    pretrain_model_path= os.getenv("PRETRAIN_MODEL_PATH")
    if pretrain_model_url is None or pretrain_model_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 PRETRAIN_MODEL_URL、PRETRAIN_MODEL_PATH环境变量。")
    pretrain_to_env(pretrain_model_url, pretrain_model_path)
    
def push_output_to_openi_obs():
    output_url = os.getenv("OUTPUT_URL")
    output_path = os.getenv("OUTPUT_PATH")
    if output_url is None or output_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 OUTPUT_URL、OUTPUT_PATH环境变量。")
    env_to_openi(OUTPUT_PATH, OUTPUT_URL)
    return  

     