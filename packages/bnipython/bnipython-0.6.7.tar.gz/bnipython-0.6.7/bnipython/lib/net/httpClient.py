import http.client
import json
import ssl
import base64
import requests
from bnipython.lib.util.utils import getTimestamp, generateTokenSignature


class HttpClient():
    def __init__(self):
        self.httpClient = http.client.HTTPSConnection('')

    def tokenRequest(self, options={'url', 'path', 'username', 'password'}):
        url = str(options['url']).replace(
            'http://', '').replace('https://', '')
        httpClient = http.client.HTTPSConnection(
            url, context=ssl._create_unverified_context())
        username = options['username']
        password = options['password']
        authorize = base64.b64encode(f'{username}:{password}'.encode('utf-8'))
        headers = {
            'User-Agent': 'bni-python/0.1.0',
            'Authorization': f'Basic {authorize.decode()}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = 'grant_type=client_credentials'

        httpClient.request('POST', options['path'], payload, headers)
        res = httpClient.getresponse()
        data = res.read()
        return json.loads(str(data.decode('utf-8')))

    def request(self, options={'method', 'apiKey', 'accessToken', 'url', 'path', 'data'}):
        url = str(options['url']).replace(
            'http://', '').replace('https://', '')
        httpClient = http.client.HTTPSConnection(
            url, context=ssl._create_unverified_context())
        accessToken = options['accessToken']
        path = options['path']
        url = f'{path}?access_token={accessToken}'
        payload = json.dumps(options['data'])
        headers = {
            'User-Agent': 'bni-python/0.1.0',
            'x-api-key': options['apiKey'],
            'Content-Type': 'application/json'
        }
        httpClient.request(options['method'], url, payload, headers)
        res = httpClient.getresponse()
        data = res.read()
        return json.loads(str(data.decode('utf-8')))

    def tokenRequestSnapBI(self, options={'url', 'clientId', 'privateKeyPath'}):
        timeStamp = getTimestamp()
        payload = "{\n\"grantType\":\"client_credentials\",\n\"additionalInfo\": {}\n}"
        headers = {
            'Content-Type': 'application/json',
            'X-SIGNATURE': generateTokenSignature({
                'privateKeyPath': options['privateKeyPath'],
                'clientId': options['clientId'],
                'timeStamp': timeStamp
            }),
            'X-TIMESTAMP': timeStamp,
            'X-CLIENT-KEY': options['clientId']
        }

        response = requests.request(
            "POST", options['url'], headers=headers, data=payload)
        return json.loads(response.text.encode('utf8'))

    def requestSnapBI(self, options={'method', 'apiKey', 'accessToken', 'url', 'data', 'additionalHeader'}):
        accessToken = options['accessToken']
        header = {
            'content-type': 'application/json',
            'user-agent': 'bni-python/0.1.0',
            'Authorization': f'Bearer {accessToken}',
        }
        header.update(options['additionalHeader'])
        payload = json.dumps(options['data'])
        response = requests.request(
            "POST", options['url'], headers=header, data=payload)
        return json.loads(response.text.encode('utf8'))
    
    def requestV2(self, options={'method', 'apiKey', 'accessToken', 'url', 'path', 'data', 'signature', 'timestamp'}):
        url = str(options['url']).replace(
            'http://', '').replace('https://', '')
        httpClient = http.client.HTTPSConnection(
            url, context=ssl._create_unverified_context())
        accessToken = options['accessToken']
        path = options['path']
        url = f'{path}?access_token={accessToken}'
        payload = json.dumps(options['data'])
        headers = {
            'User-Agent': 'bni-python/0.1.0',
            'x-api-key': options['apiKey'],
            'x-signature': options['signature'],
            'x-timestamp': options['timestamp'],
            'Content-Type': 'application/json'
        }
        httpClient.request(options['method'], url, payload, headers)
        res = httpClient.getresponse()
        data = res.read()
        return json.loads(str(data.decode('utf-8')))
