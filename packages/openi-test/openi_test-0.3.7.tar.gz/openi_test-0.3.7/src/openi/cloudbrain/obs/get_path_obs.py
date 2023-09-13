import os
from .env_check import openi_multidataset_to_env, c2net_multidataset_to_env, pretrain_to_env, env_to_openi, obs_copy_folder
#需要定义传给modelarts的两个参数data_url和train_url或是使用args, unknown = parser.parse_known_args()来规避超参数没定义的报错
def get_code_path_obs():
    cluster = os.getenv("CLUSTER")
    code_url = os.getenv("CODE_URL")
    code_path = os.getenv("CODE_PATH")
    if cluster is None or code_url is None or code_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 CLUSTER、CODE_URL 和 CODE_PATH 环境变量。")
    return code_path    

def get_dataset_path_obs():
    cluster = os.getenv("CLUSTER")
    dataset_url = os.getenv("DATASET_URL")
    dataset_path = os.getenv("DATASET_PATH")
    if cluster is None or dataset_url is None or dataset_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 DATASET_URL 和 DATASET_PATH 环境变量。")
    return dataset_path

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


def download_code_obs():
    cluster = os.getenv("CLUSTER")
    code_url = os.getenv("CODE_URL")
    code_path = os.getenv("CODE_PATH")
    if cluster is None or code_url is None or code_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 CODE_URL 和 CODE_PATH 环境变量。")
    if cluster == "c2net":
		    obs_copy_folder(code_url, code_path)
    else:
		    obs_copy_folder(code_url, code_path)
    return code_path 

def download_dataset_obs():
    cluster = os.getenv("CLUSTER")
    dataset_url = os.getenv("DATASET_URL")
    dataset_path = os.getenv("DATASET_PATH")
    if cluster is None or dataset_url is None or dataset_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 DATASET_URL 和 DATASET_PATH 环境变量。")
    if cluster == "c2net":
		    c2net_multidataset_to_env(dataset_url, dataset_path)
    else:
		    openi_multidataset_to_env(dataset_url, dataset_path)
    return dataset_path 

def download_pretrain_model_obs():
    pretrain_model_url = os.getenv("PRETRAIN_MODEL_URL")
    pretrain_model_path= os.getenv("PRETRAIN_MODEL_PATH")
    if pretrain_model_url is None or pretrain_model_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 PRETRAIN_MODEL_URL、PRETRAIN_MODEL_PATH环境变量。")
    pretrain_to_env(pretrain_model_url, pretrain_model_path)
    
def upload_output_obs():
    output_path = os.getenv("OUTPUT_PATH")
    output_url = os.getenv("OUTPUT_URL")
    if output_url is None or output_path is None:
    		raise ValueError("环境变量设置失败，请确保设置了 OUTPUT_URL、OUTPUT_PATH环境变量。")
    env_to_openi(output_path, output_url)
    return output_path

     