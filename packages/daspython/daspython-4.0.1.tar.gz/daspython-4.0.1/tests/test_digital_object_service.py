from urllib3.exceptions import InsecureRequestWarning
import warnings
from daspython.services.digitalobjects.digitalobjectservice import DigitalObjectService, DownloadRequestInput, UploadDigitalObjectRequest
from daspython.auth.authenticate import DasAuth
from daspython.common.api import Token
from dotenv import load_dotenv
import os
import unittest
import sys
sys.path.insert(0, "C:\Workspace\das-python\daspython")

load_dotenv(dotenv_path='./.env')
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


class TestDigitalObjectService(unittest.TestCase):

    def _get_token(self) -> Token:
        auth = DasAuth(
            os.getenv("DAS_URL"),
            os.getenv("DAS_USERNAME"), os.getenv("DAS_PASSWORD"))
        auth.authenticate(bool(os.getenv("CHECK_HTTPS")))
        return auth

    def test_upload_digital_object(self):

        digital_object_service = DigitalObjectService(self._get_token())

        # Check if file exists
        if not os.path.exists('C:\\Temp\\TEST-01.txt'):
            with open('C:\\Temp\\TEST-01.txt', 'w') as f:
                f.write('Hello World')

        request = UploadDigitalObjectRequest()
        request.entryCode = 'zb.b.9w'
        request.filePath = 'C:\\Temp\\TEST-01.txt'
        request.description = 'Uploaded from Python'
        digital_object_service.upload(request)

        # Delete file
        os.remove('C:\\Temp\\TEST-01.txt')

    def test_simplified_upload_digital_object(self):

        # Check if file exists
        if not os.path.exists('C:\\Temp\\TEST-01.txt'):
            with open('C:\\Temp\\TEST-01.txt', 'w') as f:
                f.write('Hello World')

        if not os.path.exists('C:\\Temp\\TEST-02.txt'):
            with open('C:\\Temp\\TEST-02.txt', 'w') as f:
                f.write('Hello World')

        digital_object_service = DigitalObjectService(self._get_token())
        digital_object_service.upload_to_entry(
            'zb.b.9w', 'C:\\Temp\\TEST-01.txt', 'Uploaded from Python')
        digital_object_service.upload_to_entry(
            'zb.b.9w', 'C:\\Temp\\TEST-02.txt', 'Uploaded from Python')

        # Delete file
        os.remove('C:\\Temp\\TEST-01.txt')
        os.remove('C:\\Temp\\TEST-02.txt')

    def test_link_existing(self):
        digital_object_service = DigitalObjectService(self._get_token())
        digital_object_service.link_existing('zb.b.b', 'h.b.wq3c')

    def test_create_download_requests(self):
        token = self._get_token()
        digital_object_service = DigitalObjectService(token)
        download_inputs = [
            DownloadRequestInput(entry_code='zb.b.tw', digital_object_codes=[
                                 'h.b.q9bh', 'h.b.u9bh']),
            DownloadRequestInput(entry_code='zb.b.zw', digital_object_codes=[
                                 'h.b.z9bh', 'h.b.89bh'])
        ]
        response = digital_object_service.create_download_request(
            download_inputs)
        self.assertFalse(response is None,
                         f'Not able to create a download request.')

    def test_get_my_requests(self):
        digital_object_service = DigitalObjectService(self._get_token())
        download_resquests = digital_object_service.get_my_requests()
        self.assertGreater(download_resquests.total_count, 0,
                           f'Download requests must be greater than 0.')

    def test_get_my_files(self):
        digital_object_service = DigitalObjectService(self._get_token())
        success = digital_object_service.get_files_from_download_request()
        self.assertTrue(success, f'Files must be downloaded.')


if __name__ == '__main__':
    unittest.main()
