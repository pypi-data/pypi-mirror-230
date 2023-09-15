import os
import requests

from trail.libconfig import libconfig
from trail.userconfig import userconfig
from .auth import retrieve_jwt_token

cached_token = None


def _retrieve_token() -> str:
    global cached_token

    if cached_token is None:
        cached_token = retrieve_jwt_token(
            email=userconfig.username, password=userconfig.password
        )

    return cached_token


def _generate_presigned_url(file_path: str, expiration_seconds: int):
    current_working_dir = os.getcwd()
    relative_path = os.path.relpath(file_path, start=current_working_dir)
    project_id = userconfig.project().config["id"]
    destination_blob_name = os.path.join(project_id, relative_path)

    url = (
        f"{libconfig.PRESIGNED_URL_ENDPOINT}?"
        f"destination_blob_name={destination_blob_name}&"
        f"expiration_seconds={expiration_seconds}"
    )
    token = _retrieve_token()
    headers = {"authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.text
            return data
        else:
            return None
    except requests.exceptions.RequestException as e:
        raise e


def upload_file(
    local_file_path: str, expiration_seconds: int, is_absolute_path=False, abs_path=""
) -> bool:
    if not is_absolute_path:
        project_directory = os.path.dirname(abs_path)
        local_file_path = os.path.abspath(
            os.path.join(project_directory, local_file_path)
        )

    signed_url = _generate_presigned_url(local_file_path, expiration_seconds)

    if signed_url is None:
        print("You are not authorized to do this action.")
        return False

    with open(local_file_path, "rb") as local_file:
        response = requests.put(signed_url, data=local_file)

    if response.status_code == 200:
        print(f"File {local_file_path} uploaded successfully.")
        return True
    else:
        print(f"Error uploading file {local_file_path}.")
        return False


def upload_folder(local_folder: str, abs_path: str, expiration_seconds=300) -> bool:
    project_directory = os.path.dirname(abs_path)
    full_local_folder = os.path.abspath(os.path.join(project_directory, local_folder))
    uploaded_successfully = False
    for root, _, files in os.walk(full_local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            uploaded_successfully = (
                upload_file(
                    local_file_path,
                    is_absolute_path=True,
                    expiration_seconds=expiration_seconds,
                )
                or uploaded_successfully
            )
    return uploaded_successfully
