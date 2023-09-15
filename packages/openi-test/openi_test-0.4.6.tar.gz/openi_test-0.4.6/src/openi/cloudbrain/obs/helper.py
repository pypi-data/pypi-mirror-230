import os
import json
import moxing as mox
# from mindspore.train.callback import Callback

def openi_dataset_to_env(data_url, data_dir):
    """
    openi copy single dataset to training image 
    """
    try:     
        mox.file.copy_parallel(data_url, data_dir)
        print("Successfully Download {} to {}".format(data_url, data_dir))
    except Exception as e:
        print('moxing download {} to {} failed: '.format(data_url, data_dir) + str(e))
    return 

def openi_multidataset_to_env(multi_data_url, data_dir):
    """
    copy single or multi dataset to training image 
    """
    multi_data_json = json.loads(multi_data_url)  
    for i in range(len(multi_data_json)):
        path = data_dir + "/" + multi_data_json[i]["dataset_name"]
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            mox.file.copy_parallel(multi_data_json[i]["dataset_url"], path) 
            print("Successfully Download {} to {}".format(multi_data_json[i]["dataset_url"],path))
        except Exception as e:
            print('moxing download {} to {} failed: '.format(
                multi_data_json[i]["dataset_url"], path) + str(e))
    print("dataset process finished!")
    return   

def pretrain_to_env(pretrain_url, pretrain_dir):
    """
    copy pretrain to training image
    """
    pretrain_url_json = json.loads(pretrain_url)  
    print("pretrain_url_json:",pretrain_url_json)
    for i in range(len(pretrain_url_json)):
        modelfile_path = pretrain_dir + "/" + pretrain_url_json[i]["model_name"]
        try:
            mox.file.copy(pretrain_url_json[i]["model_url"], modelfile_path) 
            print("Successfully Download {} to {}".format(pretrain_url_json[i]["model_url"],modelfile_path))
        except Exception as e:
            print('moxing download {} to {} failed: '.format(pretrain_url_json[i]["model_url"], modelfile_path) + str(e))
    print("pretrain process finished!")
    return          

def obs_copy_file(obs_file_url, file_url):
    """
    cope file from obs to obs, or cope file from obs to env, or cope file from env to obs
    """
    try:
        mox.file.copy(obs_file_url, file_url)
        print("Successfully Download {} to {}".format(obs_file_url,file_url))
    except Exception as e:
        print('moxing download {} to {} failed: '.format(obs_file_url, file_url) + str(e)) 
    return    
    
def obs_copy_folder(folder_dir, obs_folder_url):
    """
    copy folder from obs to obs, or copy folder from obs to env, or copy folder from env to obs
    """
    try:
        mox.file.copy_parallel(folder_dir, obs_folder_url)
        print("Successfully download {} to {}".format(folder_dir,obs_folder_url))
    except Exception as e:
        print('moxing download {} to {} failed: '.format(folder_dir,obs_folder_url) + str(e))
    return     

def c2net_multidataset_to_env(multi_data_url, data_dir):
    """
    c2net copy single or multi dataset to training image 
    """
    multi_data_json = json.loads(multi_data_url)  
    for i in range(len(multi_data_json)):
        zipfile_path = data_dir + "/" + multi_data_json[i]["dataset_name"]
        try:
            mox.file.copy(multi_data_json[i]["dataset_url"], zipfile_path) 
            print("Successfully Download {} to {}".format(multi_data_json[i]["dataset_url"],zipfile_path))
            #get filename and unzip the dataset
            filename = os.path.splitext(multi_data_json[i]["dataset_name"])[0]
            filePath = data_dir + "/" + filename
            if not os.path.exists(filePath):
                os.makedirs(filePath)
            if zipfile_path.endswith(".tar.gz"):
                os.system("tar -zxvf {} -C {}".format(zipfile_path, filePath))
            elif zipfile_path.endswith(".zip"):
                os.system("unzip {} -d {}".format(zipfile_path, filePath))
            else:
                print("The dataset is not in tar.gz or zip format!")

        except Exception as e:
            print('moxing download {} to {} failed: '.format(
                multi_data_json[i]["dataset_url"], zipfile_path) + str(e))
    return       