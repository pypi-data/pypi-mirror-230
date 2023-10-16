from bnipython.lib.net.httpClient import HttpClient
from bnipython.lib.util import constants


class BNIClient:
    def __init__(self, options={'env': False, 'appName': '', 'clientId': '', 'clientSecret': '', 'apiKey': '', 'apiSecret': ''}):
        self.config = options
        self.httpClient = HttpClient()

    def getConfig(self):
        return self.config

    def getBaseUrl(self):
        if self.config['env'] == 'dev':
            return constants.DEV_BASE_URL
        elif self.config['env'] == 'dev-2':
            return constants.DEV_TUNNELING_BASE_URL
        elif self.config['env'] == 'uat':
            return constants.UAT_BASE_URL
        elif self.config['env'] == 'sandbox':
            return constants.SANDBOX_BASE_URL
        elif self.config['env'] == 'sandbox-2':
            return constants.SANDBOX_TUNNELING_BASE_URL
        elif self.config['env'] == 'prod':
            return constants.PRODUCTION_BASE_URL

    def getToken(self):
        token = self.httpClient.tokenRequest({
            'url': self.getBaseUrl(),
            'path': '/api/oauth/token',
            'username': self.config['clientId'],
            'password': self.config['clientSecret']
        })
        return token['access_token']
