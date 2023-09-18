from bnipython.lib.net.httpClient import HttpClient
from bnipython.lib.util.utils import generateUUID, generateSignature, getTimestamp
from bnipython.lib.util.response import responseRDL

class RDL():
    def __init__(self, client):
        self.client = client.config
        self.baseUrl = client.getBaseUrl()
        self.config = client.getConfig()
        self.token = client.getToken()
        self.httpClient = HttpClient()

    def faceRecognition(self, params={
        'companyId',
        'parentCompanyId',
        'requestUuid',
        'firstName',
        'middleName',
        'lastName',
        'idNumber',
        'birthDate',
        'birthPlace',
        'gender',
        'cityAddress',
        'stateProcAddress',
        'addressCountry',
        'streetAddress1',
        'streetAddress2',
        'postAddress',
        'country',
        'selfiePhoto'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'firstName': params['firstName'],
            'middleName': params['middleName'],
            'lastName': params['lastName'],
            'idNumber': params['idNumber'], 
            'birthDate': params['birthDate'], 
            'birthPlace': params['birthPlace'], 
            'birthDate': params['birthDate'],
            'birthPlace': params['birthPlace'],
            'gender': params['gender'],
            'cityAddress': params['cityAddress'],
            'stateProvAddress': params['stateProvAddress'],
            'addressCountry': params['addressCountry'],
            'streetAddress1': params['streetAddress1'],
            'streetAddress2': params['streetAddress2'],
            'postCodeAddress': params['postCodeAddress'],
            'country': params['country'],
            'selfiePhoto': params['selfiePhoto']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/rekdana/v1.1/face/recog',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'faceRecognitionResponse'})
        
    def registerInvestor(self, params={
        'companyId',
        'parenCompanyId',
        'uuidFaceRecog',
        'title',
        'firstName',
        'middleName',
        'lastName',
        'optNPWP',
        'NPWPNum',
        'nationality',
        'domicileCountry',
        'religion',
        'birthPlace',
        'birthDate',
        'gender',
        'isMarried',
        'motherMaidenName',
        'jobCode',
        'education',
        'idType',
        'idNumber',
        'idIssuingCity',
        'idExpiryDate',
        'addressStreet',
        'addressRtRwPerum',
        'addressKel',
        'addressKec',
        'zipCode',
        'homePhone1',
        'homePhone2',
        'officePhone1',
        'officePhone2',
        'mobilePhone1',
        'mobilePhone2',
        'faxNum1',
        'faxNum2',
        'email',
        'monthlyIncome',
        'branchOpening',
        'institutionName',
        'sid',
        'employerName',
        'employerAddDet',
        'employerAddCity',
        'jobDesc',
        'ownedBankAccNo',
        'idIssuingDate'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'uuidFaceRecog': params['uuidFaceRecog'],
            'title': params['title'],
            'firstName': params['firstName'],
            'middleName': params['middleName'],
            'lastName': params['lastName'],
            'optNPWP': params['optNPWP'],
            'NPWPNum': params['NPWPNum'],
            'nationality': params['nationality'],
            'domicileCountry': params['domicileCountry'],
            'religion': params['religion'],
            'birthPlace': params['birthPlace'],
            'birthDate': params['birthDate'],
            'gender': params['gender'],
            'isMarried': params['isMarried'],
            'motherMaidenName': params['motherMaidenName'],
            'jobCode': params['jobCode'],
            'education': params['education'],
            'idType': params['idType'],
            'idNumber': params['idNumber'],
            'idIssuingCity': params['idIssuingCity'],
            'idExpiryDate': params['idExpiryDate'],
            'addressStreet': params['addressStreet'],
            'addressRtRwPerum': params['addressRtRwPerum'],
            'addressKel': params['addressKel'],
            'addressKec': params['addressKec'],
            'zipCode': params['zipCode'],
            'homePhone1': params['homePhone1'],
            'homePhone2': params['homePhone2'],
            'officePhone1': params['officePhone1'],
            'officePhone2': params['officePhone2'],
            'mobilePhone1': params['mobilePhone1'],
            'mobilePhone2': params['mobilePhone2'],
            'faxNum1': params['faxNum1'],
            'faxNum2': params['faxNum2'],
            'email': params['email'],
            'monthlyIncome': params['monthlyIncome'],
            'branchOpening': params['branchOpening'],
            'institutionName': params['institutionName'],
            'sid': params['sid'],
            'employerName': params['employerName'],
            'employerAddDet': params['employerAddDet'],
            'employerAddCity': params['employerAddCity'],
            'jobDesc': params['jobDesc'],
            'ownedBankAccNo': params['ownedBankAccNo'],
            'idIssuingDate': params['idIssuingDate']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/register/investor',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'registerInvestorResponse'})
    
    def registerInvestorAccount(self, params={
        'companyId',
        'parentCompanyId',
        'cifNumber',
        'currency',
        'openAccountReason',
        'sourceOfFund',
        'branchId',
        'bnisId',
        'sre'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'cifNumber': params['cifNumber'],
            'currency': params['currency'],
            'openAccountReason': params['openAccountReason'],
            'sourceOfFund': params['sourceOfFund'],
            'branchId': params['branchId'],        
            'sre': params['sre'],
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/register/investor/account',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'registerInvestorAccountResponse'})
    

    def inquiryAccountInfo(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/inquiry/account/info',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'inquiryAccountInfoResponse'})
    
    def inquiryAccountBalance(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/inquiry/account/balance',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'inquiryAccountBalanceResponse'})
    
    def inquiryAccountHistory(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/inquiry/account/history',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'inquiryAccountHistoryResponse'})
    
    def paymentUsingTransfer(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber',
        'beneficiaryAccountNumber',
        'currency',
        'amount',
        'remark'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber'],
            'beneficiaryAccountNumber': params['beneficiaryAccountNumber'],
            'currency': params['currency'],
            'amount': params['amount'],
            'remark': params['remark']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/payment/transfer',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'paymentUsingTransferResponse'})
    
    def inquiryPaymentStatus(self, params={
        'companyId',
        'parentCompanyId',
        'requestedUuid'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'requestedUuid': params['requestedUuid']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/inquiry/payment/status',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'inquiryPaymentStatusResponse'})
    
    def paymentUsingClearing(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber',
        'beneficiaryAccountNumber',
        'beneficiaryAddress1',
        'beneficiaryAddress2',
        'beneficiaryBankCode',
        'beneficiaryName',
        'currency',
        'amount',
        'remark',
        'chargingType'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber'],
            'beneficiaryAccountNumber': params['beneficiaryAccountNumber'],
            'beneficiaryAddress1': params['beneficiaryAddress1'],
            'beneficiaryAddress2': params['beneficiaryAddress2'],
            'beneficiaryBankCode': params['beneficiaryBankCode'],
            'beneficiaryName': params['beneficiaryName'],
            'currency': params['currency'],
            'amount': params['amount'],
            'remark': params['remark'],
            'chargingType': params['chargingType']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/payment/clearing',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'paymentUsingClearingResponse'})
    
    def paymentUsingRTGS(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber',
        'beneficiaryAccountNumber',
        'beneficiaryAddress1',
        'beneficiaryAddress2',
        'beneficiaryBankCode',
        'beneficiaryName',
        'currency',
        'amount',
        'remark',
        'chargingType'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber'],
            'beneficiaryAccountNumber': params['beneficiaryAccountNumber'],
            'beneficiaryAddress1': params['beneficiaryAddress1'],
            'beneficiaryAddress2': params['beneficiaryAddress2'],
            'beneficiaryBankCode': params['beneficiaryBankCode'],
            'beneficiaryName': params['beneficiaryName'],
            'currency': params['currency'],
            'amount': params['amount'],
            'remark': params['remark'],
            'chargingType': params['chargingType']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/payment/rtgs',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'paymentUsingRTGSResponse'})
    
    def inquiryInterbankAccount(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber',
        'beneficiaryBankCode',
        'beneficiaryAccountNumber'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber'],
            'beneficiaryBankCode': params['beneficiaryBankCode'],
            'beneficiaryAccountNumber': params['beneficiaryAccountNumber']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/inquiry/interbank/account',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'inquiryInterbankAccountResponse'})
    
    def paymentUsingInterbank(self, params={
        'companyId',
        'parentCompanyId',
        'accountNumber',
        'beneficiaryAccountNumber',
        'beneficiaryAccountName',
        'beneficiaryBankCode',
        'beneficiaryBankName',
        'amount'
    }):
        timeStamp = getTimestamp()
        payload = {}
        payload['request'] = {}
        payload['request'] = {
            'header': {
                'companyId': params['companyId'],
                'parentCompanyId': params['parentCompanyId'],
                'requestUuid': generateUUID()
            },
            'accountNumber': params['accountNumber'],
            'beneficiaryAccountNumber': params['beneficiaryAccountNumber'],
            'beneficiaryAccountName': params['beneficiaryAccountName'],
            'beneficiaryBankCode': params['beneficiaryBankCode'],
            'beneficiaryBankName': params['beneficiaryBankName'],
            'amount': params['amount']
        }
        payload = {**payload, **{ 'timestamp': timeStamp }}
        signature = generateSignature(
            {'body': payload, 'apiSecret': self.client['apiSecret']})
        res = self.httpClient.requestV2({
            'method': 'POST',
            'apiKey': self.client['apiKey'],
            'accessToken': self.token,
            'url': f'{self.baseUrl}',
            'path': '/p2pl/v2.1/payment/interbank',
            'signature': signature.split('.')[2],
            'timestamp': timeStamp,
            'data': {'request': payload['request']}
        })
        return responseRDL(params={'res': res, 'resObj': 'paymentUsingInterbankResponse'})