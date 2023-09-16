import zetane
import unittest
import mlflow
import pandas as pd
import numpy as np
import requests
import time

header = {"Authorization": 'Bearer eyJ1c2VyaWQiOiAiMiIsICJleHAiOiAiMDIvMDIvMjAyMywgMTg6NTI6MjUifQ==.3t82fdQBmKwBtkM3U71LWV7g0nAjRka2EHlpa0Ev0/JS1eAgbZ4tj0U9uGdP/m6Sv8o9/GwxMavXbWTa5Bc6Dg=='}
URL = 'http://localhost:8000/api/'

class API_Test(unittest.TestCase):



    def test_api(self):


        p = zetane.Protector(api_key=self.getAPIToken()['token'], org="roy@zetane.com", project="django proj")
        self.assertTrue(p.org == "roy@zetane.com")
        p.upload_model('test_data/jets_model_latest.zip')
        p.upload_dataset('test_data/jets_set.zip')
        p.report('../testActual.json', autoRun=True)



        s1,s2,s3 = self.reset(p.org, p.project, p)

        self.assertTrue(s1==s2)
        self.assertTrue(s2==s3)
        self.assertTrue(s1 == 200)
        self.assertTrue(s2 == 200)
        self.assertTrue(s3 == 200)
        self.assertTrue(s1 == s2 == s3 == 200, True)



    def reset(self, org, project, p):
        url = URL +  org + '/' + project

        models, datasets, run_names = self.getNames(p.org, p.project, p)
        print(models, datasets, run_names)
        req1 = requests.delete(url + '/datasets/delete/', headers=header, json={'ids': datasets})
        req2 = requests.delete(url + '/models/delete/', headers=header, json={'ids':models})
        req3 = requests.delete(url + '/runs/delete/', headers=header, json={'ids': run_names})
        print(req1.status_code, req2.status_code, req3.status_code)
        return req1.status_code, req2.status_code, req3.status_code

    def getNames(self, org, project, p):
        url = URL + org + '/' + project
        dataset_names = requests.get(url+'/datasets' , headers=header).json()
        model_names = requests.get(url+'/models' , headers=header).json()
        run_names = requests.get(url+'/runs' , headers=header).json()
        print(p.model)
        model_ids = [str(v['id']) for v in model_names]
        dataset_names = [str(v['id']) for v in dataset_names if v['name'] == p.dataset]
        run_names = [str(v['id']) for v in run_names]

        return model_ids, dataset_names, run_names

    def getAPIToken(self):
        token = requests.get(f'{URL}token', headers=header).json()
        return token

if __name__ == '__main__':
    unittest.main()



