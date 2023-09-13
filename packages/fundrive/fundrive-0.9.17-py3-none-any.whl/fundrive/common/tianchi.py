import json
import os.path

import requests
from fundrive.base import download_by_request
from fundrive.core import FileSystem


class TianChiDrive(FileSystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cookies = {}

        self.headers = {"content-type": "application/json"}

    def login(self, cookies=None, headers=None, *args, **kwargs) -> bool:
        self.cookies.update(cookies or {})
        self.headers.update(headers or {})
        return True

    def __get_dataset_url(self, fid=None):
        response = requests.get(
            url=f"https://tianchi.aliyun.com/api/dataset/getFileDownloadUrl?fileId={fid}", cookies=self.cookies
        )
        return response.json()["data"]

    def download_file(self, dir_path="./cache", fid=None, filename=None, overwrite=False, *args, **kwargs) -> bool:
        return download_by_request(url=self.__get_dataset_url(fid), file_path=os.path.join(dir_path, filename))

    def download_dir(self, dir_path="./cache", data_id=75730, overwrite=False, *args, **kwargs) -> bool:
        data = json.dumps({"dataId": data_id})

        response = requests.post(
            url="https://tianchi.aliyun.com/api/notebook/dataDetail",
            cookies=self.cookies,
            headers=self.headers,
            data=data,
        )
        data = response.json()["data"]["datalabFile"]

        for item in data:
            self.download_file(fid=item["id"], dir_path=dir_path, filename=item["filePath"])
        return True
