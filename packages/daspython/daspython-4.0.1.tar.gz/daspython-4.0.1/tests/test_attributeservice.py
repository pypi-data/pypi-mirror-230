from urllib3.exceptions import InsecureRequestWarning
import warnings
import os
from dotenv import load_dotenv
from daspython.services.attributes.attributeservice import AttributeService
import unittest
from daspython.auth.authenticate import DasAuth
from daspython.services.attributes.attributeservice import AttributeService

load_dotenv(dotenv_path='./.env')
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


class TestAttributeService(unittest.TestCase):

    def test_get_attribute_name(self):
        auth = DasAuth(os.getenv("DAS_URL"), os.getenv(
            "DAS_USERNAME"), os.getenv("DAS_PASSWORD"))
        auth.authenticate(bool(os.getenv("CHECK_HTTPS")))

        service = AttributeService(auth)
        result = service.get_attribute_name(55)

        self.assertEqual(
            result, 'Cores', f'Expected value is Core but got {result}')

    def test_get_attribute_id(self):
        auth = DasAuth(os.getenv("DAS_URL"), os.getenv(
            "DAS_USERNAME"), os.getenv("DAS_PASSWORD"))
        auth.authenticate(bool(os.getenv("CHECK_HTTPS")))

        service = AttributeService(auth)
        result = service.get_attribute_id('Cores')

        self.assertEqual(result, 55, f'Expected value is 55 but got {result}')


if __name__ == '__main__':
    unittest.main()
