import zetane
import unittest
from .test_base import BaseTestCase, SCRIPT_DIR

# For running tests, need to generate a protector API key
# set it with an env var `ZETANE_API_KEY`
# which you can do either from the command line before running tests
# or by adding a .env file in this directory with that env var

class API_Test(BaseTestCase):
    def test_auth(self):
        self.assertIsNotNone(zetane.default_connection.user)

    def test_default_org(self):
        self.assertIsNotNone(zetane.default_connection.org)

    def test_create_project(self):
        res = zetane.create_project("Test Project 1")
        self.assertEqual(res.status_code, 201)
        res = zetane.delete_project("Test Project 1")
        self.assertEqual(res.status_code, 200)

    def test_upload_dataset(self):
        print("Test upload dataset..")
        zetane.create_project("Birds")
        res = zetane.upload_dataset(SCRIPT_DIR + '/data/birds.zip', project="Birds", name="bird_dataset")
        json_res = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_res['name'], 'bird_dataset')
        self.assertEqual(json_res['upload_status'], {'status': 'Ready'})
        res = zetane.delete_project("Birds")
        self.assertEqual(res.status_code, 200)

    def test_upload_model(self):
        print("Test upload model..")
        zetane.create_project("Birds")
        res = zetane.upload_model(SCRIPT_DIR + '/data/model.pt', project="Birds", name="bird_model")
        json_res = res.json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json_res['name'], 'bird_model')
        self.assertEqual(json_res['upload_status'], {'status': 'Ready'})
        res = zetane.delete_project("Birds")
        self.assertEqual(res.status_code, 200)

    def test_report(self):
        print("Test report run")
        test = {
            "blur": {
                "intervals": "3",
                "max": "5",
                "min": "3"
            },
            "elastic transform": {
                "intervals": "3",
                "max": "4",
                "min": "2",
                "xai": []
            },
        }
        zetane.create_project("Birds-Report")
        model = zetane.upload_model(SCRIPT_DIR + '/data/model.pt', project="Birds-Report")
        dataset = zetane.upload_dataset(SCRIPT_DIR + '/data/birds.zip', project="Birds-Report")
        report = zetane.report(test_json=test, input_shape=[None, 256, 256, 3], model_type="image_classification", model="model.pt", dataset="birds.zip", project="Birds-Report", autoRun=True)
        res = zetane.delete_project("Birds-Report")

        self.assertTrue(report)


if __name__ == '__main__':
    unittest.main()
