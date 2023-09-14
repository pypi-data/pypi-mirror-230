from .modelarts import openi_multidataset_to_env,c2net_multidataset_to_env,pretrain_to_env,env_to_openi
#需要定义传给modelarts的两个参数data_url和train_url或是使用args, unknown = parser.parse_known_args()来规避超参数没定义的报错
def get_code_path_obs():
    """
    获取源数据代码存储在obs,拷贝到镜像后的代码路径
    """
    return
def get_data_path_obs():
    """
    获取源数据集存储在obs,拷贝到镜像后的数据集路径
    """
    cluster = os.getenv("CLUSTER")
    data_url = os.getenv("DATA_URL")
    data_path = os.getenv("DATA_PATH")
    if cluster is None or data_url is None or data_path is None:
    	raise ValueError("Failed to get the environment variable, please make sure the CLUSTER, DATA_URL and DATA_PATH environment variables have been set")
    if cluster == "c2net":
        c2net_multidataset_to_env(data_url, data_path)
    else:
        openi_multidataset_to_env(data_url, data_path)
    return data_path
def get_pretrain_model_path_obs():
    """
    获取源数据预训练模型存储在obs,拷贝到镜像后的预训练模型路径
    """
    pretrain_model_url = os.getenv("PRETRAIN_MODEL_URL")
    pretrain_model_path= os.getenv("PRETRAIN_MODEL_PATH")
    if pretrain_model_url is None or pretrain_model_path is None:
    	raise ValueError("Failed to get environment variables, please make sure you have set PRETRAIN_MODEL_URL, PRETRAIN_MODEL_PATH environment variables.")
    pretrain_to_env(pretrain_model_url, pretrain_model_path)
    return pretrain_model_path
def get_output_path_obs():
    """
    获取需要存储在obs上的输出路径
    """
    output_path = os.getenv("OUTPUT_PATH")
    if output_path is None:
    	raise ValueError("Failed to get the environment variable, please ensure that the OUTPUT_PATH environment variable has been set.")
    return output_path 
def push_output_to_openi_obs():
    """
    将输出数据推送到openi的obs存储
    """
    output_url = os.getenv("OUTPUT_URL")
    output_path = os.getenv("OUTPUT_PATH")
    if output_url is None or output_path is None:
    	raise ValueError("Failed to get environment variables, please ensure that the OUTPUT_URL and OUTPUT_PATH environment variables have been set.")
    env_to_openi(OUTPUT_PATH, OUTPUT_URL)
    return 