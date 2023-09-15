import emoji

def env_check():
    try:
        import moxing as mox
        print(f'{emoji.emojize(":thumbs_up:")} enviornment check pass: Modelarts enviornment checked')
        return True
    except:
        print(f'{emoji.emojize(":cross_mark:")} enviornment check failed: 请在启智平台NPU集群上运行该代码')
        return False

def openi_dataset_to_env(data_url, data_dir):
    if env_check():
        from .helper import openi_dataset_to_env as func
        func(data_url, data_dir)

def openi_multidataset_to_env(multi_data_url, data_dir):
    if env_check():
        from .helper import openi_multidataset_to_env as func
        func(multi_data_url, data_dir)

def pretrain_to_env(pretrain_url, pretrain_dir):
    if env_check():
        from .helper import pretrain_to_env as func
        func(pretrain_url, pretrain_dir)

def obs_copy_file(obs_file_url, file_url):
    if env_check():
        from .helper import obs_copy_file as func
        func(obs_file_url, file_url)
    
def obs_copy_folder(folder_dir, obs_folder_url):
    if env_check():
        from .helper import obs_copy_folder as func
        func(folder_dir, obs_folder_url)

def c2net_multidataset_to_env(multi_data_url, data_dir):
    if env_check():
        from .helper import c2net_multidataset_to_env as func
        func(multi_data_url, data_dir)

      