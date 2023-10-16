
from bnipython.lib.util import constants
import unittest
from bnipython.lib.bniClient import BNIClient


class TestUtil(unittest.TestCase):
    def testBaseUrl(self):
        print('\n==============================================')
        clientDev = BNIClient(
            {'env': 'sandbox', 'clientId': '', 'clientSecret': '', 'apiKey': ''})
        self.assertEqual(clientDev.getBaseUrl(), constants.DEV_BASE_URL)
        print(f'should return {constants.DEV_BASE_URL}')
        clientDev = BNIClient(
            {'env': 'sandbox', 'clientId': '', 'clientSecret': '', 'apiKey': ''})
        self.assertEqual(clientDev.getBaseUrl(), constants.SANDBOX_DEV_BASE_URL)
        print(f'should return {constants.SANDBOX_DEV_BASE_URL}')
        clientSandbox = BNIClient(
            {'env': 'sandbox', 'clientId': '', 'clientSecret': '', 'apiKey': ''})
        self.assertEqual(clientSandbox.getBaseUrl(), constants.SANDBOX_BASE_URL)
        print(f'should return {constants.SANDBOX_BASE_URL}')
        clientProd = BNIClient(
            {'env': 'prod', 'clientId': '', 'clientSecret': '', 'apiKey': ''})
        self.assertEqual(clientProd.getBaseUrl(), constants.PRODUCTION_BASE_URL)
        print(f'should return {constants.PRODUCTION_BASE_URL}')

    def testConfig(self):
        print('\n==============================================')
        client = BNIClient({'env': 'sandbox', 'appName': constants.APP_NAME, 'clientId': constants.CLIENT_ID,
                           'clientSecret': constants.CLIENT_SECRET, 'apiKey': constants.API_KEY})
        self.assertEqual(client.getConfig(), {'env': 'sandbox', 'appName': constants.APP_NAME,
                         'clientId': constants.CLIENT_ID, 'clientSecret': constants.CLIENT_SECRET, 'apiKey': constants.API_KEY})
        print(
            'should return { env: \'Sandbox\', appName: \'Test APP\', clientId: \'test12345\', clientSecret: \'test54321\', apiKey: \'12345\' }')
