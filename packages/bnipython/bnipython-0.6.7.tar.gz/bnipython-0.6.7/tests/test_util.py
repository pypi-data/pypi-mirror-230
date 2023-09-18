from bnipython.lib.util import constants
from bnipython.lib.util.utils import generateClientId, generateSignature, generateUUID
import unittest

class TestUtil(unittest.TestCase):

    def testClientId(self):
        print('\n==============================================')
        clientId = generateClientId(constants.APP_NAME)
        self.assertEqual(clientId, constants.CLIENT_ID_BASE64)
        print(f'should return {constants.CLIENT_ID_BASE64}')

    def testSignature(self):
        print('\n==============================================')
        clientId = generateClientId(constants.APP_NAME)
        payload = {'body': {'clientId': clientId,
                            'accountNo': constants.ACCOUNT_NO}, 'apiSecret': constants.API_SECRET}
        token = generateSignature(payload)
        self.assertEqual(token, constants.TOKEN_JWT)
        print(f'should return {constants.TOKEN_JWT}')
    
    def testUUID(self):
        print('\n==============================================')
        uuid = generateUUID()
        print(f'should return {uuid}')