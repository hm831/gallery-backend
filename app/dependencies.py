import requests

from fastapi import UploadFile

def upload_img_server_file(
        host: str, 
        port: int, 
        server_file_path: str, 
        server_file_name: str, 
        local_file: UploadFile
):
    api_url = f"http://{host}:{port}/upload/"
    params = {
        "file_path": server_file_path,
        "file_name": server_file_name
    }
    files = {
        "file": local_file
    }
    response = requests.post(url=api_url, params=params, files=files).json()
    return response["url"]

def upload_img_server(
        host: str, 
        port: int, 
        server_file_path: str, 
        server_file_name: str, 
        local_file_path: str
):
    api_url = f"http://{host}:{port}/upload/"
    params = {
        "file_path": server_file_path,
        "file_name": server_file_name
    }
    files = {
        "file": open(local_file_path, "rb")
    }
    response = requests.post(url=api_url, params=params, files=files).json()
    return response["url"]

def get_server(host: str, port: int):
    return f"http://{host}:{port}"
