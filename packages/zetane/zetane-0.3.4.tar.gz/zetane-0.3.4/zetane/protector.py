import os, filetype, time, json
from tqdm import tqdm
import requests as req
from pathlib import Path
from zetane.utils import validate_test_json, validate_file_type


def get_default_org(json):
    if len(json['organizations']) > 0:
        return json['organizations'][0]['name']

    raise ValueError("No default organization for this user!")

def file_helper(file_path, metadata, name=None):
    filename = os.path.basename(file_path)
    absolute_file_path = os.path.abspath(file_path)
    file_size = os.path.getsize(absolute_file_path)
    file_type = filetype.guess_mime(absolute_file_path)
    if not name:
        name = filename
    body = {"name": name, "filename": filename, "file_type": file_type, "file_size": file_size, "source": "API", "metadata": json.dumps(metadata)}
    newObj = {
            'upload_status': { 'status': "Pending" },
            'dataset_type': 'classification',
        }

    body = {**body, **newObj}
    return body


class NetworkError(Exception):
    def __init__(self, result, message=""):
        self.result = result
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.result.reason + ' ' + str(self.result.status_code) + ' at ' + self.result.url + ' -> ' + self.result.text

class Connection:
    def __init__(self, api_key, address="https://protector-api-1.zetane.com"):
        self.api_key = api_key
        self.address = address if address.endswith('/') else f'{address}/'
        self.user = None
        self.org = None
        self.project = None

    def confirm_upload(self, client, datatype, id):
        # PUT /org/project/datatype/id
        body = {"upload_status": {"status": "Ready"}}
        confirm_url = self.api_url_builder(client.org(), client.project(), datatype, f"{str(id)}")
        return self.req_handle(confirm_url, "put", body, json_bool=True)

    def multipart_upload(self, datatype, id, file):
        FILE_CHUNK_SIZE = 10000000  # 10MB
        if isinstance(file, str):
            absolute_file_path = os.path.abspath(file)
            file_size = os.path.getsize(absolute_file_path)
            file_path = Path(absolute_file_path)
            file_type = file_path.suffix
            file_obj = open(absolute_file_path, "rb")
        else:
            file_size = file.getbuffer().nbytes
            file_type = "application/zip"
            file_obj = file

        NUM_CHUNKS = (file_size - 1) // FILE_CHUNK_SIZE + 1

        base_url = self.api_url_builder(self.org, self.project, datatype, f"{str(id)}")
        res = self.req_handle(base_url + '/upload', "post", {"fileType": file_type})

        # Initialize multi-part
        upload_id = res.json()["uploadId"]

        # Upload multi-part
        parts = []
        for index in tqdm(range(NUM_CHUNKS)):
            offset = index * FILE_CHUNK_SIZE
            file_obj.seek(offset, 0)

            res = self.req_handle(base_url + "/upload_part",
                            "post",
                        {"part": index + 1, "uploadId": upload_id})
            presigned_url = res.json()["presignedUrl"]
            res = req.put(presigned_url, data=file_obj.read(FILE_CHUNK_SIZE), headers={"Content-Type": file_type})
            parts.append({"ETag": res.headers["etag"][1:-1], "PartNumber": index + 1})

        if isinstance(file, str):
            file_obj.close()
        # Finalize multi-part
        fin_body = {"parts": parts, "uploadId": upload_id}
        res = self.req_handle(base_url + "/upload_complete", "post", fin_body, json_bool=True)
        return res

    def req_handle(self, url, method, body=None, json_bool=False):
        headers = {"Authorization": "Token " + self.api_key}
        res = None
        url = self.address + url
        if method == "get":
            res = req.get(url, headers=headers)
        if method == "post":
            if json_bool:
                res = req.post(url, json=body, headers=headers)
            else:
                res = req.post(url, data=body, headers=headers)
        if method == "put":
            if json_bool:
                res = req.put(url, json=body, headers=headers)
            else:
                res = req.put(url, data=body, headers=headers)
        if method == "delete":
            res = req.delete(url, data=body, headers=headers)

        #if res is not None and res.status_code != 200 and res.status_code != 201 and res.status_code != 202:
        #    print('STATUS CODE: ', res.status_code)
        #    raise NetworkError(res)

        return res

    def api_url_builder(self, *args):
        url = 'api'
        for arg in args:
            url = url + "/" + arg
        return url

    def refresh_user(self):
        try:
            res = self.req_handle("users/me", 'get')
            self.user = res.json()
        except:
            raise Exception("API KEY is invalid. You can retrieve your api key from: protector.zetane.com")

    def auth_check(self):
        if not hasattr(self, 'api_key') or not self.api_key:
            raise SystemExit('Failed to authenticate API key')

    def check_org_in_user(self, org):
        user = self.user
        for org_temp in user['organizations']:
            if org_temp['name'] == org:
                return True
        print('Organization name is invalid')
        return False

    def check_project_in_org(self, org, project_to_check):
        user = self.user
        org_check = None
        for org_tmp in user['organizations']:
            if org_tmp['name'] == org:
                org_check = org_tmp
        for project in org_check['projects']:
            if project['name'] == project_to_check:
                return True
        print('Project name is invalid')
        return False

    def config(self, api_key=None, address=None, org=None, project=None):
        self.refresh_user()

        if org and self.check_org_in_user(org.lower()):
            self.org = org.lower()
            print('Organization configuration successful')
        else:
            self.org = get_default_org(self.user)
        if self.org and project and self.check_project_in_org(self.org, project):
            self.project = project
            print('Project configuration successful')

class Protector():
    def __init__(self, connection):
        self.connection = connection
        print('Successfully authenticated: ')
        self.get_orgs_and_projects()
        self.model_filename = None
        self.dataset_filename = None

    def api_key(self):
        return self.connection.api_key

    def auth_check(self):
        return self.connection.auth_check()

    def config(self, *args, **kwargs):
        return self.connection.config(*args, **kwargs)

    def org(self):
        return self.connection.org

    def project(self):
        return self.connection.project

    def address(self):
        return self.connection.address

    def api_url_builder(self, *args, **kwargs):
        return self.connection.api_url_builder(*args, **kwargs)

    def req_handle(self, *args, **kwargs):
        return self.connection.req_handle(*args, **kwargs)

    def get_orgs_and_projects(self):
        self.auth_check()
        res = self.req_handle('users/me', 'get')
        user = res.json()
        for org in user['organizations']:
            print("Organization: ", org['name'])
            for project in org['projects']:
                print('\t' + "Project: ",  project['name'])

    def create_project(self, name):
        self.auth_check()
        print("Creating project")
        body = {"name": name}
        create_url = self.api_url_builder(self.org(), "project")
        res = self.req_handle(create_url, "post", body)
        if (res.status_code != 201):
            raise RuntimeError("Project was not created : ", res.json())
        return res

    def delete_project(self, name):
        self.auth_check()
        delete_url = self.api_url_builder(self.org(), name, "delete")
        return self.req_handle(delete_url, "delete")

    def upload_dataset(self, file_path='', name=None, org=None, project=None):
        # POST /org/project/dataset
        self.auth_check()
        print('Starting dataset upload..')
        self.config(project=project, org=org)
        # metadata = construct_metadata_obj(file_path)
        # if not metadata:
        #     print('Please select a zipped file to upload')
        #     return
        # return
        body = file_helper(file_path, {}, name)
        post_url = self.api_url_builder(self.org(), self.project(), "dataset")
        res = self.req_handle(post_url, "post", body, True)
        if res.status_code == 201:
            dataset_id = res.json()["id"]
            dataset_filename = res.json()['filename']
            res = self.connection.multipart_upload("datasets", dataset_id, file_path)
            res = self.connection.confirm_upload(self, "datasets", dataset_id)
            self.dataset_filename = dataset_filename
            print("Completed")
        else:
            raise RuntimeError(f"Dataset did not successfully upload. Error: {res.json()}")
        return res

    def upload_model(self, file_path, name=None, org=None, project=None):
        self.auth_check()
        print('Starting model upload...')
        print("Upload to: ", project)
        self.config(project=project, org=org)
        # metadata = construct_metadata_obj(file_path)
        # if not metadata:
        #     print('Please select a zipped file to upload')
        #     return
        body = file_helper(file_path, {}, name)
        print("Project: ", self.project())
        post_url = self.api_url_builder(self.org(), self.project(), "model")
        res = self.req_handle(post_url, "post", body, json_bool=True)
        if res.status_code == 201:
            model_id = res.json()["id"]
            model_filename = res.json()['filename']
            res = self.connection.multipart_upload("models", model_id, file_path)
            res = self.connection.confirm_upload(self, "models", model_id)
            self.model_filename = model_filename
            print("Completed")
        else:
            raise RuntimeError(f"Model did not successfully upload. Error: {res.json()}")
        return res

    def get_entries(self, datatype, org=None, project=None):
        # GET /org/project/datatype
        self.auth_check()
        print("Getting entries..")
        if datatype != 'models' and datatype != 'datasets':
            return print('Only available datatypes are "models" or "datasets"')
        self.config(project=project, org=org)
        if not self.project():
            return print('Please select a project')
        url = self.api_url_builder(self.org(), self.project(), datatype)
        res = self.req_handle(url, "get")

        if res.status_code == 200:
            for x in res.json():
                if not x['name']:
                    continue
                print(f'ID: {str(x["id"])} NAME: {x["name"]}')
        return res

    def get_report_status(self, name, org=None, project=None):
        # GET /org/project/report_name
        self.auth_check()
        self.config(project=project, org=org)
        url = self.api_url_builder(self.org(), self.project(), f"{name}", "status")
        res = self.req_handle(url, "get")
        if res:
            curr_status = res.json()["status"]
            print('Report Name: ' + name)
            print('Report Status: ' + curr_status)
        return res

    def report(self, test_profile_path=None, test_json=dict(), input_shape=list(), model_type=None, organization=None, project=None, model=None, dataset=None, autoRun=False):
        # POST /org/project/run
        self.auth_check()
        self.config(org=organization, project=project)
        model_filename = model if model else self.model_filename
        dataset_filename = dataset if dataset else self.dataset_filename

        validation_errors = list()
        if not input_shape:
           validation_errors.append('Please specify a model input_shape as a list in the format [B H W C]')
        if not model_type and model_type not in ['object_detection', 'image_classification']:
            validation_errors.append('Please specify a model input type: either "object_detection" or "image_classification"')
        if not model and not hasattr(self, 'model'):
            validation_errors.append('Please specify which model you wish to use')
        if not dataset and not hasattr(self, 'dataset'):
            validation_errors.append('Please specify which dataset you wish to use')
        if not project and not hasattr(self, 'project'):
            validation_errors.append('Please specify which project you wish to use')
        if not test_json and validate_file_type(test_profile_path):
            validation_errors.append('Please provide a json test spec or a path to a file containing a json test spec')

        if len(validation_errors) > 0:
            for error in validation_errors:
                print(error)
            return

        #get model ID
        try:
            url = self.api_url_builder(self.org(), self.project(), 'models')
            res = self.req_handle(url, "get")
            if not res.status_code == 200:
                print('Report creation failed - invalid model selection')
                print(res.json())
                return
            else:
                models_json = res.json()
                models_match = [v['id'] for v in models_json if v['filename'] == model_filename]
                model_id = max(models_match)
        except:
            print('Invalid model selection - please select from the following or upload a new model:')
            return self.get_entries('models')

        #get dataset ID
        try:
            url = self.api_url_builder(self.org(), self.project(), 'datasets')
            res = self.req_handle(url, "get")
            if not res.status_code == 200:
                print('Report creation failed - invalid dataset selection')
                print(res.json())
            else:
                dataset_json = res.json()
                datasets_match = [v['id'] for v in dataset_json if v['filename'] == dataset_filename]
                dataset_id = max(datasets_match)
        except:
            print("Invalid dataset selection - please select from the following or upload a new dataset:")
            return self.get_entries('datasets')

        test_series_name = "Test Report"
        if test_profile_path is not None:
            test_series_name = test_profile_path.split('/')[-1]
            with open(test_profile_path) as f:
                test_json = json.load(f)

        crafted_test_profile = validate_test_json(test_json, model_filename, model_id,input_shape, model_type, dataset_filename, dataset_id, test_series_name)

        url = self.api_url_builder(self.org(), self.project(), "run")
        body = {"save": False, "data": crafted_test_profile, "supValues": { "numPrimaryTests": '', "numComposedTests": '', "totalTestRuns": '', "totalXaiApplied": '' }}
        res = self.req_handle(url, "post", body, json_bool=True)
        name = None
        name = res.json()["name"]

        if res.status_code == 201:
            print("Starting report: " + name)
            print('When completed, your report can be found at the following url:')
            link_url = f"https://protector.zetane.com/{self.org()}/{self.project()}/runs/{name}"
            print(link_url)
            if (autoRun):
                i = 0
                sleep_time = 10
                status_url = self.api_url_builder(self.org(), self.project(), name, "status")
                while True:
                    time.sleep(sleep_time)
                    i += 1
                    res = self.req_handle(status_url, "get")
                    if res.status_code == 200:
                        print("Running... " + str(sleep_time * i) + " seconds")
                        status = res.json()["status"]
                        if status == "Ready":
                            print(f"Report completed! View the results {link_url}")
                            return True
                        elif status == "Error":
                            print(f"Error running report! View the error logs: {res.json()['error']}")
                            return False
        else:
            raise NetworkError(res, "Failed to schedule report")

        return res


    def build_image(self, model_id):
        # POST /org/project/id/image
        url = self.api_url_builder(self.org(), self.project(), f"{str(model_id)}", "image")
        res = self.req_handle(url, "post", json.dumps({id: id}))
        if res.status_code == 201:
            name = res.json()["name"]
            i = 0
            while True:
                time.sleep(10)
                i += 1
                url = self.api_url_builder(name, "image", "status")
                res = self.req_handle(url, "get")
                if res.status_code == 200:
                    print("Building... " + str(10 * i) + " seconds")
                    status = res.json()["status"]["status"]
                    if status != "Running" and status != "Pending":
                        break
                else:
                    print('Not building image...')
                    break
        return res



