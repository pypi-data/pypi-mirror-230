import os
from tqdm import tqdm
import requests as req
import filetype
import time

ADDRESS = "https://protector-api-1.zetane.com"

class NetworkError(Exception):
    def __init__(self, result, message=""):
        self.result = result
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message + ': ' + self.result.reason + ' ' + str(self.result.status_code) + ' at ' + \
               self.result.url + ' -> ' + self.result.text


def create_entry(token, organization, project, type, file_path):
    filename = os.path.basename(file_path)
    headers = {"Authorization": "Token " + token}
    URL = ADDRESS + "/api/" + organization + "/" + project
    absolute_file_path = os.path.abspath(file_path)
    file_size = os.path.getsize(absolute_file_path)
    file_type = filetype.guess_mime(absolute_file_path)
    body = {"filename": filename, "file_type": file_type, "file_size": file_size, "source": "API", "metadata":{}}
    if type == "models":
        res = req.post(URL + "/model", json=body, headers=headers)
    elif type == "datasets":
        res = req.post(URL + "/dataset", json=body, headers=headers)
    else:
        raise Exception("Unknown type: " + type)

    return res


def confirm_upload(token, organization, project, type, id, file_path):
    filename = os.path.basename(file_path)
    headers = {"Authorization": "Token " + token}
    URL = ADDRESS + "/api/" + organization + "/" + project
    if type == "models":
        res = req.put(URL + "/models/" + str(id) + "/", json={"name": filename, "upload_status": {"status": "Ready"}},
                      headers=headers)
    elif type == "datasets":
        res = req.put(URL + "/datasets/" + str(id) + "/", json={"name": filename, "upload_status": {"status": "Ready"}},
                      headers=headers)
    else:
        raise Exception("Unknown type: " + type)

    return res


def upload(token, organization, project, type, id, file_path):
    FILE_CHUNK_SIZE = 10000000  # 10MB
    absolute_file_path = os.path.abspath(file_path)
    file_size = os.path.getsize(absolute_file_path)
    NUM_CHUNKS = (file_size - 1) // FILE_CHUNK_SIZE + 1
    file_type = filetype.guess_mime(absolute_file_path)

    URL = ADDRESS + "/api/" + organization + "/" + project + "/" + type + "/" + str(id)
    headers = {"Authorization": "Token " + token}
    # Initialize multi-part
    res = req.post(URL + "/upload", json={"fileType": file_type}, headers=headers)
    upload_id = res.json()["uploadId"]

    # Upload multi-part
    parts = []
    with open(absolute_file_path, "rb") as file:
        for index in tqdm(range(NUM_CHUNKS)):
            offset = index * FILE_CHUNK_SIZE
            file.seek(offset, 0)

            res = req.post(URL + "/upload_part",
                           json={"part": index + 1, "uploadId": upload_id},
                           headers=headers)
            presigned_url = res.json()["presignedUrl"]
            res = req.put(presigned_url, data=file.read(FILE_CHUNK_SIZE), headers={"Content-Type": file_type})
            parts.append({"ETag": res.headers["etag"][1:-1], "PartNumber": index + 1})

    # Finalize multi-part
    res = req.post(URL + "/upload_complete",
                   json={"parts": parts, "uploadId": upload_id},
                   headers=headers)
    return res


def build_image(token, organization, project, id):
    URL = ADDRESS + "/api/" + organization + "/" + project
    headers = {"Authorization": "Token " + token}
    res = req.post(URL + "/" + str(id) + "/image", headers=headers)
    if res.status_code == 201:
        name = res.json()["name"]
        i = 0
        while True:
            time.sleep(10)
            i += 1
            res = req.get(URL + "/" + name + "/image/status", headers=headers)
            if res.status_code == 200:
                print("Building... " + str(10 * i) + " seconds")
                if res.json()["status"] != "running":
                    break
            else:
                break
    return res


def upload_dataset(token, organization, project, file_path):
    print('starting')
    res = create_entry(token, organization, project, "datasets", file_path)
    if res.status_code != 201:
        raise NetworkError(res, "Failed Creation")
    dataset_id = res.json()["id"]
    res = upload(token, organization, project, "datasets", dataset_id, file_path)
    if res.status_code != 200:
        raise NetworkError(res, "Failed Upload")
    res = confirm_upload(token, organization, project, "datasets", dataset_id, file_path)
    if res.status_code != 202:
        raise NetworkError(res, "Failed Confirmation")
    print("Completed")
    return res


def upload_model(token, organization, project, file_path):
    print('starting')
    res = create_entry(token, organization, project, "models", file_path)
    if res.status_code != 201:
        raise NetworkError(res, "Failed Creation")
    model_id = res.json()["id"]
    res = upload(token, organization, project, "models", model_id, file_path)
    if res.status_code != 200:
        raise NetworkError(res, "Failed Upload")
    res = confirm_upload(token, organization, project, "models", model_id, file_path)
    if res.status_code != 202:
        raise NetworkError(res, "Failed Confirmation")
    res = build_image(token, organization, project, model_id)
    if res.status_code != 200:
        raise NetworkError(res, "Failed Image Building")
    print("Completed")
    return res

def get_entries(token, organization, project, type):
    headers = {"Authorization": "Token " + token}
    URL = ADDRESS + "/api/" + organization + "/" + project + '/' + type
    res = req.get(URL, headers=headers)

    if res.status_code == 200:
        return res.json()
    return


def report(token, organization, project, model, dataset):
    URL = ADDRESS + "/api/" + organization + "/" + project
    headers = {"Authorization": "Token " + token}
    res = req.post(URL + "/run",
                   json={"model": {"name": model}, "dataset": {"name": dataset}, "setup": {"s3_key": "setup.zip"}},
                   headers=headers)
    name = None
    print("Starting")
    if res.status_code == 201:
        name = res.json()["name"]
        i = 0
        while True:
            time.sleep(10)
            i += 1
            res = req.get(URL + "/" + name + "/status", headers=headers)
            if res.status_code == 200:
                print("Running... " + str(10 * i) + " seconds")
                if res.json()["status"] != "running":
                    break
            else:
                break

    if res.status_code == 200:
        res = req.get(URL + "/" + name + "/report", headers=headers)
    else:
        raise NetworkError(res, "Failed Execution")

    if res.status_code != 200:
        raise NetworkError(res, "Failed Report")
    print("Completed")
    return res



