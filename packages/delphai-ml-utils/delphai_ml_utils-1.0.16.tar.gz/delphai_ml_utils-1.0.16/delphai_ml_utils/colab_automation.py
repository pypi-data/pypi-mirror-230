import requests
import json
import shutil
import mlflow
from git import Repo
from pathlib import Path
from dotenv import load_dotenv


GITHUB_CLIENT_ID = "Iv1.e2763b06061ce07c"
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
DEVICE_AUTH_URL = "https://github.com/login/device"
GITHUB_USER_URL = "https://api.github.com/user"
MLFLOW_SERVER_URL = "https://mlflow-server.delphai.com"
CREDENTIALS_FILE_PATH = "/content/drive/MyDrive/.env"


def set_credentials():
    from google.colab import auth, drive

    auth.authenticate_user()
    drive.mount("/content/drive")
    mlflow.set_tracking_uri(MLFLOW_SERVER_URL)
    load_dotenv("/content/drive/MyDrive/.env")
    user_device_response = requests.post(
        DEVICE_CODE_URL,
        params={"client_id": GITHUB_CLIENT_ID},
        headers={"Accept": "application/json"},
    )
    user_device_response.raise_for_status()
    user_code = user_device_response.json().get("user_code")
    global device_code
    device_code = user_device_response.json().get("device_code")
    print(
        f"Your user code is: {user_code}. Enter it at {DEVICE_AUTH_URL} and continue the authentication flow."
    )


def get_path_in_drive(file_id):
    from googleapiclient.discovery import build

    drive_service = build("drive", "v3").files()
    file_metadata = drive_service.get(fileId=file_id, fields="name, parents").execute()
    name = file_metadata.get("name")
    if file_metadata.get("parents"):
        parent_id = file_metadata.get("parents")[0]
        return get_path_in_drive(parent_id) / name
    else:
        return Path(name)


def get_path_in_colab():
    session_data = requests.get("http://172.28.0.12:9000/api/sessions").json()[0]
    file_id = session_data["path"].split("=")[1]
    path_in_drive = get_path_in_drive(file_id)
    return "/content/drive" / path_in_drive


def get_access_token():
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    response = requests.post(
        ACCESS_TOKEN_URL,
        params=params,
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    global access_token
    access_token = json.loads(response.text).get("access_token")


def get_current_username():
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(GITHUB_USER_URL, headers=headers)
    response.raise_for_status()
    return response.json().get("login")


def clone_ml_projects():
    username = get_current_username()
    repo_url = f"https://{username}:{access_token}@github.com/delphai/ml-projects.git"
    repo = Repo.clone_from(repo_url, "/content/ml-projects")
    repo.config_writer().set_value("user", "name", username)
    return repo


def push_to_ml_projects(repo, filepath, commit_message):
    repo.index.add([filepath])
    commit = repo.index.commit(commit_message)
    branch_name = repo.active_branch.name
    origin = repo.remote("origin")
    origin.push(f"{branch_name}:{branch_name}")
    return commit


def push_and_track_commit(repo, path_in_ml_projects, experiment_id, run_id):
    notebook_path = get_path_in_colab()
    shutil.copy(notebook_path, path_in_ml_projects)
    commit = push_to_ml_projects(
        repo, path_in_ml_projects, f"Add changes that produced {experiment_id}/{run_id}"
    )
    return commit
