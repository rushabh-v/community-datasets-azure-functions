import logging
import os
import tempfile
import traceback
from pathlib import Path
from shutil import copytree

import azure.functions as func

from .gdrive import MyDrive
from .utils import (add_dataset, add_user, extract_dataset, get_dataset_path,
                    remove_dir, zip_upload_remove)


def main(req: func.HttpRequest) -> func.HttpResponse:

    tmp = tempfile.gettempdir() + "/workspace"
    tmp_data = tmp + "/dataset"
    repo_path = str(Path.home()) + "/community_datasets"

    for dir_path in (tmp, tmp_data, repo_path):
        remove_dir(dir_path)
        os.mkdir(dir_path)

    drive = MyDrive()
    datasets = drive.download_file("community_datasets.zip")
    extract_dataset(datasets, repo_path)

    mode = req.params.get("mode")
    ret = [None, None]
    try:
        if mode == "register":
            username = req.params.get("username")
            password = req.params.get("password")
            ret = add_user(username, password, repo_path)
            if ret[1] == 200:
                zip_upload_remove(drive, repo_path, tmp)

        elif mode in ("add", "update"):
            configs = req.params
            dataset = list(req.files.values())[0]
            extract_dataset(dataset, tmp_data)
            ret = add_dataset(tmp_data, repo_path, configs, mode)
            if ret[1] == 200:
                zip_upload_remove(drive, repo_path, tmp)

        elif mode == "download":
            configs = req.params
            ret = get_dataset_path(repo_path, configs)
            if ret[1] == 200:
                ret[0] = open(ret[0], "r").read()
                remove_dir(repo_path)

        else:
            raise NotImplemented()

        remove_dir(tmp)
        return func.HttpResponse(ret[0], status_code=ret[1])

    except Exception as e:
        remove_dir(tmp)
        if mode == "register_user":
            remove_dir(repo_path + "/" + req.params.get("username"))
        elif mode == "register_dataset":
            remove_dir(
                f"{repo_path}/{req.params.get('username')}/{req.params.get('dataset_name')}"
            )
        return func.HttpResponse(traceback.format_exc(), status_code=500)
