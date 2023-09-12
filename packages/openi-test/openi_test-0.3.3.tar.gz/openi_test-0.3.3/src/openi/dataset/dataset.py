import os
import math
import requests
import hashlib
import time
import logging
from datetime import datetime
from tqdm import tqdm
from ..constants import *
from ..utils.logger import setup_logging
setup_logging()

class DatasetUploadFile:
    """
    Build APIs calls for uploading a file to openi platform.
    This class will start upload process immediatelly once being initialized. 
    """

    def __init__(self, file, username, repository, token, cluster, app_url):
        """
        Args:
            file:       必填，文件路径(包含文件名)
            username:   必填，数据集所属项目的owner用户名
            repository: 必填，数据集所属项目名
            token:      必填，用户启智上获取的令牌token，并对该项目数据集有权限
            
            cluster:    选填，可填入GPU或NPU，不填写后台默认为NPU
            app_url:    选填, 默认为平台地址，开发测试用
        """
        self.filepath = file
        self.username = username
        self.repo = repository
        self.token = token
        self.cluster = cluster
        self.app_url = app_url

        # preset variables
        if cluster == "NPU":
            self.upload_type = 1
        elif cluster == "GPU":
            self.upload_type = 0
        else:
            raise ValueError(
                f"❌ please enter a valid cluster name, 'GPU' or 'NPU'")

        if "\\" in self.filepath:
            self.filename = self.filepath.split("\\")[-1]
        else:
            self.filename = self.filepath.split("/")[-1]

        self.size = os.path.getsize(self.filepath)
        self.upload_url = dict()

    """
    APIs implementation
    """
    def getChunks(self):
        params = {
            "access_token": self.token,
            "dataset_id": self.dataset_id,
            "md5": self.md5,
            "file_name": self.filename,
            "type": self.upload_type,
        }
        x = requests.get('{}attachments/get_chunks'.format(self.app_url), params=params)

        if x.status_code == 200:
            logging.info(f'{x.url} {x} {x.reason} | params return: {x.json()}')
            self.upload_id = x.json()["uploadID"]
            self.uuid = x.json()["uuid"]
            self.uploaded_chunks = x.json()["chunks"]
            if x.json()["uploaded"] == '1':
                self.uploaded = True
            else:
                self.uploaded = False
            try:
                return [int(i.split('-')[0]) for i in x.json()["chunks"].split(',') if i != '']
            except:
                logging.error(f' {x.url} {x} {x.reason} | getChunks.["chunks"] not returned.')
                raise ValueError(
                    " f'❌ getChunks failed.")
        else:
            logging.error(f'{x.url} {x} {x.reason}')
            raise ConnectionRefusedError(
                f'❌ <{x.status_code} {x.reason}>')

    def getDatasetID(self):
        params = {"access_token": self.token}
        x = requests.get('{}datasets/{}/{}/'.format(self.app_url, self.username, self.repo), params=params)
        if x.status_code == 200:
            try:
                logging.info(f'{x.url} {x} {x.reason} | params return: {x.json()}')
                self.dataset_id = x.json()["data"][0]["id"]
            except Exception as e:
                logging.error(f'{x.url} {x} {x.reason} | dataset does not exist, please create dataset before uploading files.')
                raise ValueError(
                    f'❌ repo [{self.username}/{self.repo}]: dataset does not exist, please create dataset before uploading files.')
        else:
            logging.error(f'{x.url} {x} {x.reason}')
            raise ConnectionRefusedError(
                f'❌ <{x.status_code} {x.reason}>')

    def newMultipart(self):
        params = {
            "access_token": self.token,
            "dataset_id": self.dataset_id,
            "md5": self.md5,
            "file_name": self.filename,
            "type": self.upload_type,
            "totalChunkCounts": self.total_chunk_counts,
            "size": self.size
        }
        x = requests.get('{}attachments/new_multipart'.format(self.app_url), params=params)

        if x.json()["result_code"] == "0":
            logging.info(f'{x.url} {x} {x.reason} | params return: {x.json()}')
            self.upload_id = x.json()["uploadID"]
            self.uuid = x.json()["uuid"]
        else:
            logging.error(f'{x.url} {x} {x.reason} | {x.json()}')
            raise ConnectionRefusedError(
                f'❌ <{x.status_code} {x.reason}> {x.json()["msg"]}')

    def getMultipartURL(self, chunk_number, chunk_size):
        params = {
            "access_token": self.token,
            "dataset_id": self.dataset_id,
            "file_name": self.filename,
            "type": self.upload_type,
            "chunkNumber": chunk_number,
            "size": chunk_size,
            "uploadID": self.upload_id,
            "uuid": self.uuid
        }

        retry = 0
        while retry < 3:
            try:
                x = requests.get('{}attachments/get_multipart_url'.format(self.app_url), params=params)
                logging.info(f'{x.url} {x} {x.reason} | params return: {x.json()}')
                return x.json()["url"]
            except ConnectionError:
                logging.error(f'getMultiUrl chunk [{chunk_number}], retry={retry+1} ')
                print(f'getMultiUrl chunk [{chunk_number}], retry={retry+1}')
            except RuntimeError:
                logging.error(f'getMultiUrl chunk [{chunk_number}], retry={retry+1} ')
                print(f'getMultiUrl chunk [{chunk_number}], retry={retry+1}')
            retry += 1
            time.sleep(0.5)
        logging.error(f'reach max retry, getMultiUrl chunk [{chunk_number}] failed.')
        raise ConnectionRefusedError(
            f'❌ reach max retry {retry}, `getMultiUrl` chunk [{chunk_number}] failed. Checkpoint saved, please upload again.')

    def putUpload(self, url, chunk_number, file_chunk_data):
        headers = {"Content-Type": "text/plain"} if self.upload_type == 0 else {}

        retry = 0
        while retry < 3:
            try:
                x = requests.put(url, data=file_chunk_data, headers=headers)
                logging.info(f'{x} {x.reason} {x.url} | etag: {x.headers["ETag"]}')
                return x.headers["ETag"]
            except ConnectionError:
                logging.error(f'putUpload chunk [{chunk_number}], retry={retry+1}')
                print(f'putUpload chunk [{chunk_number}], retry={retry+1}')
            except RuntimeError:
                logging.error(f'putUpload chunk [{chunk_number}], retry={retry+1}')
                print(f'putUpload chunk [{chunk_number}], retry={retry+1}')
            retry += 1
            time.sleep(0.5)
        logging.error(f'reach max retry, putUpload chunk [{chunk_number}] failed.')
        raise ConnectionRefusedError(
            f'❌ reach max retry {retry}, `putUpload` chunk [{chunk_number}] failed. Checkpoint saved, please upload again.')

    def completeMultipart(self):
        params = {
            "access_token": self.token,
            "dataset_id": self.dataset_id,
            "file_name": self.filename,
            "type": self.upload_type,
            "size": self.size,
            "uploadID": self.upload_id,
            "uuid": self.uuid
        }
        x = requests.post('{}attachments/complete_multipart'.format(self.app_url), params=params)
        logging.info(f'{x.url} {x} {x.reason} | finished completeMultipart | Fileobject: {self.__dict__}')
        if x.status_code != 200:
            logging.error(f'{x.url} {x} {x.reason} | {x.text}')
            raise ConnectionRefusedError(
                f'❌ <{x.status_code} {x.reason}> {x.text}')
        if x.json()["result_code"] == "-1":
            logging.error(f'{x} {x.reason} | {x.json()}')
            raise ConnectionRefusedError(
                f'❌ <{x.status_code} {x.reason}> {x.json()["msg"]}')
    """
    utils functions
    """

    def get_time(self, message=""):
        return datetime.now().strftime("%H:%M:%S")

    def filePreprocess(self):
        self.getDatasetID()
        if self.size == 0:
            logging.error(f'[{self.filename}] File size is 0 | FileObject: {self.__dict__}')
            raise ValueError(
                f'❌ [{self.filename}] File size is 0')
        if self.size > MAX_FILE_SIZE:
            logging.error(f'[{self.filename}] File size exceeds 200GB | FileObject: {self.__dict__}')
            raise ValueError(
                f'❌ [{self.filename}] File size exceeds 200GB')

        self.chunk_size = SMALL_FILE_CHUNK_SIZE if self.size < SMALL_FILE_SIZE else LARGE_FILE_CHUNK_SIZE
        self.total_chunk_counts = math.ceil(self.size / self.chunk_size)
        #self.chunks = {n: (n - 1) * self.chunk_size for n in range(1, self.total_chunk_counts + 1)}
        self.calculateMD5()

    def calculateMD5(self):
        """
        计算文件的md5
        :param self.filepath:
        :return:
        """
        m = hashlib.md5()  # 创建md5对象
        with open(self.filepath, 'rb') as fobj:
            while True:
                data = fobj.read(4096)
                if not data:
                    break
                m.update(data)  # 更新md5对象

        self.md5 = m.hexdigest()  # 返回md5对象

    """
    Main functions
    uploadProgressBar(): upload file with progress bar.
    uploadMain(): control flow function.
    """

    def uploadProgressBar(self, chunks):
        _progress = self.chunk_size * (self.total_chunk_counts - len(chunks))
        bar_format = '{desc}{percentage:3.0f}%|{bar}{r_bar}'
        desc = f'{self.get_time()} - Uploading: '
        with tqdm(total=self.size, leave=True, unit='B', unit_scale=True, unit_divisor=1000, desc=desc,
                  bar_format=bar_format, initial=_progress) as pbar:
            for n in chunks:
                start_position = (n - 1) * self.chunk_size
                chunk_size = min(self.size, self.chunk_size, self.size - start_position)
                with open(self.filepath, 'rb') as file:
                    file.seek(start_position)  # Move the file pointer to the desired start position
                    data = file.read(chunk_size)  # Read the specified chunk size from the current position
                url = self.getMultipartURL(n, chunk_size)
                etag = self.putUpload(url, n, data)
                if etag is None:
                    raise RuntimeError(
                        f'❌ Upload failed: {self.filename}({self.cluster}) '
                        f'chunk {n} failed to upload.')
                pbar.update(chunk_size)
                logging.info(f'chunk {n} uploaded. | FileObject: {self.__dict__}')


    def uploadMain(self):

        print(f'{self.get_time()} - `{self.filename}({self.cluster})` dataset file processing & checking...')
        # preprocess
        self.filePreprocess()
        logging.info(f'file check finished. | FileObject: {self.__dict__}')

        # checking upload status
        uploaded_chunks = self.getChunks()


        #upload starts
        if self.uuid != '':
            if self.uploaded:
                logging.error(f'Upload failed: `{self.filename}({self.cluster})` already exists, cannot be uploaded again. | FileObject: {self.__dict__}')
                raise ValueError(
                    f'❌ Upload failed: `{self.filename}({self.cluster})` already exists, cannot be uploaded again. ')
            else:
                uploaded_chunks = sorted(uploaded_chunks)[:-1]
                continue_chunks = [i for i in range(1, self.total_chunk_counts+1) if i not in uploaded_chunks]
                continue_chunks = sorted(continue_chunks)
                self.uploadProgressBar(continue_chunks)

        else:
        #if not self.uploaded:
            self.newMultipart()
            chunks = [i for i in range(1, self.total_chunk_counts + 1)]
            self.uploadProgressBar(chunks)

        self.completeMultipart()
        url = f"{self.app_url.split('api')[0]}{self.username}/{self.repo}/datasets"
        print(f'{self.get_time()} - 🎉 Successfully uploaded, view on link: {url}')
        logging.info(f'successfully uploaded. | FileObject: {self.__dict__}')

def upload_file(file, username, repository, token, cluster="NPU", app_url=APP_URL):
    d = DatasetUploadFile(
        file=file,
        username=username,
        repository=repository,
        token=token,
        cluster=cluster,
        app_url=app_url)
    d.uploadMain()
