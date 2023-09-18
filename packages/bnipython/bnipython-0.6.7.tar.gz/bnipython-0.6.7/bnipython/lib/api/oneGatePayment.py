from bnipython.lib.net.httpClient import HttpClient
from bnipython.lib.util.utils import generateClientId, generateSignature
from bnipython.lib.util.response import responseOGP


class OneGatePayment():
    def __init__(self, client):
        self.client = client.config
        self.baseUrl = client.getBaseUrl()
        self.config = client.getConfig()
        self.token = client.getToken()
        self.httpClient = HttpClient()

    def getBalance(self, params={'accountNo'}):
        payload = {}
        body = {
            'accountNo': params['accountNo'],
            'clientId': generateClientId(self.client['appName'])
        }
        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})

        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/getbalance',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'getBalanceResponse'})

    def getInHouseInquiry(self, params={'accountNo'}):
        payload = {}
        body = {
            'accountNo': params['accountNo'],
            'clientId': generateClientId(self.client['appName'])
        }
        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})

        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/getinhouseinquiry',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'getInHouseInquiryResponse'})

    def doPayment(self,
                  params={
                      'customerReferenceNumber',
                      'paymentMethod',
                      'debitAccountNo',
                      'creditAccountNo',
                      'valueDate',
                      'valueCurrency',
                      'valueAmount',
                      'remark',
                      'beneficiaryEmailAddress',
                      'beneficiaryName',
                      'beneficiaryAddress1',
                      'beneficiaryAddress2',
                      'destinationBankCode',
                      'chargingModelId'
                  }):
        payload = {}
        body = {
            'clientId': generateClientId(self.client['appName']),
            'customerReferenceNumber': params['customerReferenceNumber'],
            'paymentMethod': params['paymentMethod'],
            'debitAccountNo': params['debitAccountNo'],
            'creditAccountNo': params['creditAccountNo'],
            'valueDate': params['valueDate'],
            'valueCurrency': params['valueCurrency'],
            'valueAmount': params['valueAmount'],
            'remark': params['remark'],
            'beneficiaryEmailAddress': params['beneficiaryEmailAddress'],
            'beneficiaryName': params['beneficiaryName'],
            'beneficiaryAddress1': params['beneficiaryAddress1'],
            'beneficiaryAddress2': params['beneficiaryAddress2'],
            'destinationBankCode': params['destinationBankCode'],
            'chargingModelId': params['chargingModelId']
        }

        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})

        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/dopayment',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'doPaymentResponse'})

    def getPaymentStatus(self, params={'customerReferenceNumber'}):
        payload = {}
        body = {
            'clientId': generateClientId(self.client['appName']),
            'customerReferenceNumber': params['customerReferenceNumber']
        }

        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/getpaymentstatus',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'getPaymentStatusResponse'})

    def getInterBankInquiry(self,  params={
        'customerReferenceNumber',
        'accountNum',
        'destinationBankCode',
        'destinationAccountNum'
    }):
        payload = {}
        body = {
            'clientId': generateClientId(self.client['appName']),
            'customerReferenceNumber': params['customerReferenceNumber'],
            'accountNum': params['accountNum'],
            'destinationBankCode': params['destinationBankCode'],
            'destinationAccountNum': params['destinationAccountNum']
        }
        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/getinterbankinquiry',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'getInterbankInquiryResponse'})

    def getInterBankPayment(self, params={
        'customerReferenceNumber',
        'amount',
        'destinationAccountNum',
        'destinationAccountName',
        'destinationBankCode',
        'destinationBankName',
        'accountNum',
        'retrievalReffNum'
    }):
        payload = {}
        body = {
            'clientId': generateClientId(self.client['appName']),
            'customerReferenceNumber': params['customerReferenceNumber'],
            'amount': params['amount'],
            'destinationAccountNum': params['destinationAccountNum'],
            'destinationAccountName': params['destinationAccountName'],
            'destinationBankCode': params['destinationBankCode'],
            'destinationBankName': params['destinationBankName'],
            'accountNum': params['accountNum'],
            'retrievalReffNum': params['retrievalReffNum']
        }
        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/getinterbankpayment',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'getInterbankPaymentResponse'})

    def holdAmount(self, params={
        'customerReferenceNumber',
        'amount',
        'accountNo',
        'detail'
    }):
        payload = {}
        body = {
            'clientId': generateClientId(self.client['appName']),
            'customerReferenceNumber': params['customerReferenceNumber'],
            'amount': params['amount'],
            'accountNo': params['accountNo'],
            'detail': params['detail']
        }
        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/holdamount',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'holdAmountResponse'})

    def holdAmountRelease(self, params={
        'customerReferenceNumber',
        'amount',
        'accountNo',
        'bankReference',
        'holdTransactionDate'
    }):
        payload = {}
        body = {
            'clientId': generateClientId(self.client['appName']),
            'customerReferenceNumber': params['customerReferenceNumber'],
            'amount': params['amount'],
            'accountNo': params['accountNo'],
            'bankReference': params['bankReference'],
            'holdTransactionDate': params['holdTransactionDate']
        }
        payload = body
        payload['signature'] = generateSignature(
            {'body': body, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.request({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/H2H/v2/holdamountrelease',
            'data': payload
        })
        return responseOGP(params={'res': res, 'resObj': 'holdAmountReleaseResponse'})
