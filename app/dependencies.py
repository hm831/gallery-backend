import requests

from fastapi import UploadFile

def upload_img_server_file(host: str, port: int, file: UploadFile):
    api_url = f"http://{host}:{port}/upload/"
    files = {
        "file": file
    }
    response = requests.post(url=api_url, files=files).json()
    return response["url"]

def upload_img_server(host: str, port: int, file_path: str):
    api_url = f"http://{host}:{port}/upload/"
    files = {
        "file": open("/Users/yoru/Pictures/" + file_path, "rb")
    }
    response = requests.post(url=api_url, files=files).json()
    return response["url"]

def get_server(host: str, port: int):
    return f"http://{host}:{port}"