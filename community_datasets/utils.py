import os
import zipfile
from io import BytesIO
from shutil import copy, rmtree


def add_user(username, password, repo_path):
    path = repo_path + "/" + username
    if not os.path.isdir(path):
        os.mkdir(path)
        with open(f"{path}/.auth", "w") as f:
            f.write(password)
        return [f"New username registered: {username}", 200]
    else:
        return [f"username {username} is already in use.", 500]


def extract_dataset(dataset, path):
    with zipfile.ZipFile(dataset) as zip_ref:
        zip_ref.extractall(path + "/")


def add_dataset(data_path, repo_path, configs, mode):

    if os.path.isdir(repo_path + "/" + configs["username"]):
        user = repo_path + "/" + configs["username"]
        if open(user + "/" + ".auth").read() != configs["password"]:
            return ["Authentication failed due to wrong password.", 500]

        dataset_path = user + "/" + configs["dataset_name"]
        if not os.path.isdir(dataset_path):
            if mode == "update":
                return [
                    f"Dataset {configs['username']}:{configs['dataset_name']} does not exist.",
                    500,
                ]
            else:
                os.mkdir(dataset_path)
                copy(data_path + "/" + configs["dataset_name"] + ".py", dataset_path)
                return [
                    f"The tests ran successfully (no tests are running as part of the demo, this line is just to show that there will be tests running as a prerequisite to dataset deployment).\nNew dataset added: {configs['username']}:{configs['dataset_name']}",
                    200,
                ]
        else:
            if mode == "update":
                remove_dir(dataset_path)
                os.mkdir(dataset_path)
                copy(data_path + "/" + configs["dataset_name"] + ".py", dataset_path)
                return [
                    f"The tests ran successfully (no tests are running as part of the demo, this line is just to show that there will be tests running as a prerequisite to dataset deployment).\nDataset {configs['username']}:{configs['dataset_name']} has been updated.",
                    200,
                ]
            else:
                return [
                    f"Dataset {configs['username']}:{configs['dataset_name']} already exists, Run `community_datasets update` to update it.",
                    500,
                ]
    else:
        return [f"Namespace {configs['username']} does not exist.", 500]


def get_dataset_path(repo_path, configs):
    if os.path.isdir(repo_path + "/" + configs["username"]):
        user = repo_path + "/" + configs["username"]
        if os.path.isdir(user + "/" + configs["dataset_name"]):
            return [
                f"{user}/{configs['dataset_name']}/{configs['dataset_name']}.py",
                200,
            ]
        else:
            return [
                f"dataset {configs['username']}:{configs['dataset_name']} does not exist.",
                500,
            ]
    else:
        return [f"Namespace {configs['username']} does not exist.", 500]


def remove_dir(path):
    if os.path.isdir(path):
        rmtree(path)


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def zip_upload_remove(drive, repo_path, tmp):
    cur_dir = os.getcwd()
    os.chdir(repo_path)
    zipf = zipfile.ZipFile(f"{tmp}/community_datasets.zip", "w", zipfile.ZIP_DEFLATED)
    zipdir("./.", zipf)
    zipf.close()
    os.chdir(cur_dir)
    drive.update_file("community_datasets.zip", tmp)
    remove_dir(repo_path)
