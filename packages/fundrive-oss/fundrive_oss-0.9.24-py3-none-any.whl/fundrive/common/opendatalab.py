import os
from typing import Any

import requests
from fundrive.base import download_by_request
from fundrive.core import FileSystem
from funsecret import read_secret


class OpenDataLabDrive(FileSystem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = "https://openxlab.org.cn"
        self.cookies = {}
        self.headers = {}

    def login(self, ak=None, sk=None, opendatalab_session=None, ssouid=None, *args, **kwargs) -> bool:
        self.cookies.update(
            {
                "opendatalab_session": opendatalab_session
                or read_secret(cate1="fundrive", cate2="opendatalab", cate3="cookies", cate4="opendatalab_session"),
                "ssouid": ssouid or read_secret(cate1="fundrive", cate2="opendatalab", cate3="cookies", cate4="ssouid"),
            }
        )
        self.headers.update({"accept": "application/json"})
        return True

    def get_file_info(self, dataset_id, file_path, *args, **kwargs) -> dict[str, Any]:
        resp = requests.get(
            url=f"{self.host}/datasets/resolve/{dataset_id}/main/{file_path}",
            headers=self.headers,
            cookies=self.cookies,
            allow_redirects=False,
        )
        result = {
            "url": resp.headers["Location"],
            "dataset_id": dataset_id,
            "path": file_path[1:],
        }
        return result

    def get_file_list(self, dataset_name, payload=None, *args, **kwargs) -> list[dict[str, Any]]:
        dataset_name = dataset_name.replace("/", ",")
        data = {"recursive": True}
        if payload:
            data.update(payload)
        resp = requests.get(
            url=f"{self.host}/datasets/api/v2/datasets/{dataset_name}/r/main",
            params=data,
            headers=self.headers,
            cookies=self.cookies,
        )
        result_dict = resp.json()["data"]["list"]
        return result_dict

    def download_file(
        self, dir_path="./cache", dataset_id=None, file_path=None, overwrite=False, *args, **kwargs
    ) -> bool:
        try:
            file_info = self.get_file_info(dataset_id=dataset_id, file_path=file_path)
            return download_by_request(url=file_info["url"], file_path=os.path.join(dir_path, file_info["path"]))
        except Exception as e:
            return False

    def download_dir(self, dir_path="./cache", dataset_name=None, overwrite=False, *args, **kwargs) -> bool:
        if dataset_name is None:
            return False
        file_list = self.get_file_list(dataset_name=dataset_name)
        for file in file_list:
            try:
                self.download_file(dir_path=dir_path, dataset_id=file["dataset_id"], file_path=file["path"])
            except Exception as e:
                print(e)
        return True
