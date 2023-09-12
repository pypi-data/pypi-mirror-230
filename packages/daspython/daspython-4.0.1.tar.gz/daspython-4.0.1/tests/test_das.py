import json
import os
import unittest
import pandas as pd
from dotenv import load_dotenv

from daspython.das import DasClient


class TestDasPython(unittest.TestCase):

    __das: DasClient
    __base_url: str
    __username: str
    __password: str
    __check_https: bool

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        load_dotenv()
        self.__base_url = str(os.getenv('DAS_URL'))
        self.__username = str(os.getenv('DAS_USERNAME'))
        self.__password = str(os.getenv('DAS_PASSWORD'))
        self.__check_https = False
        self.__das = DasClient(
            self.__username, self.__password, self.__base_url, self.__check_https)

    def test_get_attribute_name(self):
        unittest.TestCase.assertEqual(
            self, self.__das.get_attribute_name(55), 'Cores')

    def test_get_attribute_id(self):
        unittest.TestCase.assertEqual(
            self, self.__das.get_attribute_id('Cores'), 55)

    def test_get_entries(self):
        response = self.__das.get_entries('Cores')
        unittest.TestCase.assertEqual(self, len(response.items), 10)

    def test_download_template(self):
        self.__das.download_template('Cores', "c:\\temp\\template.xlsx")
        unittest.TestCase.assertTrue(
            self, os.path.exists("c:\\temp\\template.xlsx"))

    def test_insert_data_from_excel(self):

        df = pd.read_excel(
            'C:\\Workspace\\das-python\\core_test_template.xlsx')
        entries = df.to_dict("records")

        self.__das.create_entries_from_excel(
            attribute_name='Cores', entries=entries)
        # TODO: check if the entries were inserted

    def test_change_owner(self):
        self.__das.change_owner('zb.b.u8', 'flavio.francisco@nioz.nl')
        # TODO: check if the ownership was changed

    def test_create_entry(self):

        entry = {
            'Number': '1234',
            'Alias': None,
            'Latitude (decimal)': '54.3775',
            'Longitude (decimal)': '4.7452',
            'Water depth in meters': '46.83',
            'Date of arrival': '2022-06-06',
            'Date of departure': '2022-06-06',
            'Time of arrival': '06:06:58',
            'Time of departure': '07:17:21',
            'Project Name': 'DAS Python Test',
        }

        new_entry_id = self.__das.create_entry(
            attribute_name='cruise', entry=entry)

        self.assertTrue(
            new_entry_id is not None and new_entry_id != 'Unable to create entry')

    def test_update_entry(self):
        self.__das.update_entry(code='zb.b.68', entry={'Number': 1234})
        response = self.__das.get_by_code('zb.b.68')
        self.assertTrue(response.entry.get('number') == 1234)

    def test_delete_entry(self):
        result = self.__das.delete_entry('6.b.1s')
        self.assertTrue(result)

    def test_upload_digital_object(self):
        if not os.path.exists('C:\\Temp\\TEST-01.txt'):
            with open('C:\\Temp\\TEST-01.txt', 'w') as f:
                f.write('Hello World')
        self.__das.upload_digital_object(
            'zb.b.9w', 'C:\\Temp\\TEST-01.txt', 'Uploaded from Python')
        response = self.__das.get_by_code('zb.b.9w')
        digital_objects = json.loads(str(response.entry.get('6')))
        self.assertTrue(len(digital_objects) > 0 and any(
            obj.get('name') == "TEST-01.txt" for obj in digital_objects))

    def test_link_existing_digital_object(self):
        self.__das.link_digital_object('zb.b.9w', 'h.b.ql2h')
        response = self.__das.get_by_code('zb.b.9w')
        digital_objects = json.loads(str(response.entry.get('6')))
        self.assertTrue(len(digital_objects) > 0 and any(
            obj.get('code') == "h.b.ql2h" for obj in digital_objects))

    def test_get_my_requests(self):
        response = self.__das.get_my_download_requests_info()
        self.assertTrue(response is not None and response.total_count > 0)

    def test_get_files_from_request(self):
        self.__das.get_files_from_download_request()
        # Get files where name starts with digital-object- and ends with .zip
        files = [f for f in os.listdir('.') if os.path.isfile(
            f) and f.startswith('digital-objects-') and f.endswith('.zip')]
        self.assertTrue(len(files) > 0)
        # delete the files
        for f in files:
            os.remove(f)

    def test_search(self):
        response = self.__das.search(
            'cores', 'End Depth(0.75);Name(64PE407-03PC#08)')
        self.assertTrue(response is not None and len(
            response.items) > 0 and response.total > 0)

    def test_create_download_requests(self):

        download_request_input = [
            {
                'zb.b.gx': ['h.b.bkqh']
            },
            {
                'zb.b.9z': ['h.b.ygwh', 'h.b.1gwh']
            }
        ]

        response = self.__das.create_download_request(download_request_input)

        self.assertTrue(response)


if __name__ == '__main__':
    unittest.main()
