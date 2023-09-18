from bnipython.lib.api.rdf import RDF
from bnipython.lib.util import constants
import unittest
from bnipython.lib.bniClient import BNIClient
import json


class TestRDF(unittest.TestCase):
    client = BNIClient({
        'env': 'sandbox-dev',
        'appName': constants.APP_NAME,
        'clientId': constants.CLIENT_ID_ENCRYPT,
        'clientSecret': constants.CLIENT_SECRET_ENCRYPT,
        'apiKey': constants.API_KEY_ENCRYPT,
        'apiSecret': constants.API_SECRET_ENCRYPT
    })

    def testInquiryAccountBalance(self):
        print('\n============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryAccountBalance({
            'companyId': 'SANDBOX',
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117'
        })
        data = res['response']['responseCode']
        # print(json.dumps(res, indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryAccountInfo(self):
        print('\n============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryAccountInfo({
            'companyId': 'SANDBOX',
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117'
        })
        data = res['response']['responseCode']
        # print(json.dumps(res, indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingTransfer(self):
        print('\n============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingTransfer({
            'companyId': 'SANDBOX',
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117',
            'beneficiaryAccountNumber': '0115471119',
            'currency': 'IDR',
            'amount': '11500',
            'remark': 'Test P2PL'
        })
        data = res['response']['responseCode']
        # print(json.dumps(res, indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testRegisterInvestor(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.registerInvestor({
            "companyId": "SANDBOX",
            "parentCompanyId": "STI_CHS",
            "uuidFaceRecog": "492F33851D634CFB",
            "title": "01",
            "firstName": "Agus",
            "middleName": "",
            "lastName": "Saputra",
            "optNPWP": "1",
            "NPWPNum": "001058893408123",
            "nationality": "ID",
            "domicileCountry": "ID",
            "religion": "2",
            "birthPlace": "Semarang",
            "birthDate": "14081982",
            "gender": "M",
            "isMarried": "S",
            "motherMaidenName": "Dina Maryati",
            "jobCode": "01",
            "education": "07",
            "idType": "01",
            "idNumber": "4147016201959998",
            "idIssuingCity": "Jakarta Barat",
            "idExpiryDate": "26102099",
            "addressStreet": "Jalan Mawar Melati",
            "addressRtRwPerum": "003009Sentosa",
            "addressKel": "Cengkareng Barat",
            "addressKec": "Cengkareng/Jakarta Barat",
            "zipCode": "11730",
            "homePhone1": "0214",
            "homePhone2": "7459",
            "officePhone1": "",
            "officePhone2": "",
            "mobilePhone1": "0812",
            "mobilePhone2": "12348331",
            "faxNum1": "",
            "faxNum2": "",
            "email": "agus.saputra@gmail.com",
            "monthlyIncome": "8000000",
            "branchOpening": "0259",
            "institutionName": "PT. BNI SECURITIES",
            "sid": "IDD280436215354",
            "employerName": "Salman",
            "employerAddDet": "St Baker",
            "employerAddCity": "Arrandelle",
            "jobDesc": "Pedagang",
            "ownedBankAccNo": "0337109074",
            "idIssuingDate": "10122008"
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testRegisterInvestorAccount(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.registerInvestorAccount({
            "companyId": "SANDBOX",
            "parentCompanyId": "STI_CHS",
            "cifNumber": "9100749959",
            "accountType": "RDF",
            "currency": "IDR",
            "openAccountReason": "2",
            "sourceOfFund": "1",
            "branchId": "0259"
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryAccountHistory(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryAccountHistory({
            "companyId": "SANDBOX",
            "parentCompanyId": "STI_CHS",
            "accountNumber": "0115476117"
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingClearing(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingClearing({
            "companyId": "SANDBOX",
            "parentCompanyId": "STI_CHS",
            "accountNumber": "0115476117",
            "beneficiaryAccountNumber": "3333333333",
            "beneficiaryAddress1": "Jakarta",
            "beneficiaryAddress2": "",
            "beneficiaryBankCode": "140397",
            "beneficiaryName": "Panji Samudra",
            "currency": "IDR",
            "amount": "15000",
            "remark": "Test kliring",
            "chargingType": "OUR"
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingRTGS(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingRTGS({
            "companyId": "SANDBOX",
            "parentCompanyId": "STI_CHS",
            "accountNumber": "0115476117",
            "beneficiaryAccountNumber": "3333333333",
            "beneficiaryAddress1": "Jakarta",
            "beneficiaryAddress2": "",
            "beneficiaryBankCode": "CENAIDJA",
            "beneficiaryName": "Panji Samudra",
            "currency": "IDR",
            "amount": "150000000",
            "remark": "Test rtgs",
            "chargingType": "OUR"
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryPaymentStatus(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryPaymentStatus({
            "companyId": "SANDBOX",
            "parentCompanyId": "STI_CHS",
            "requestedUuid": "E8C6E0027F6E429F",
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryInterbankAccount(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryInterbankAccount({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '0115476117',
            'beneficiaryBankCode': '013',
            'beneficiaryAccountNumber': '01300000'
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingInterbank(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingInterbank({
            "companyId": "SANDBOX",
            "parentCompanyId": "STI_CHS",
            "accountNumber": "0115476117",
            "beneficiaryBankCode": "014",
            "beneficiaryBankName": "BCA",
            "beneficiaryAccountNumber": "01400000",
            "beneficiaryAccountName": "Bpk HANS",
            "amount": "15000"
        })
        data = res['response']['responseCode']
        # print(json.dumps(res['response'], indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testFaceRecog(self):
        print('\n==============================================')
        rekening_dana_nasabah = RDF(self.client)
        res = rekening_dana_nasabah.faceRecognition({
            'companyId': 'SANDBOX',
            'parentCompanyId': 'STI_CHS',
            'firstName': 'MOHAMMAD',
            'middleName': 'BAQER',
            'lastName': 'ZALQAD',
            'idNumber': '0141111121260118',
            'birthDate': '29-09-2021',
            'birthPlace': 'BANDUNG',
            'gender': 'M',
            'cityAddress': 'Bandung',
            'stateProvAddress': 'Jawa Barat',
            'addressCountry': 'ID',
            'streetAddress1': 'bandung',
            'streetAddress2': 'bandung',
            'postCodeAddress': '40914',
            'country': 'ID',
            'selfiePhoto': '29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuP'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryAccountBalanceFailed(self):
        print('\n============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryAccountBalance({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '0221869561'
        })
        data = res['response']['responseCode']
        # print(json.dumps(res, indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryAccountInfoFailed(self):
        print('\n============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryAccountInfo({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '1122334455'
        })
        data = res['response']['responseCode']
        # print(json.dumps(res, indent=2))
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingTransferFailed(self):
        print('\n============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingTransfer({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '1000152671',
            'beneficiaryAccountNumber': '0316031099',
            'currency': 'IDR',
            'amount': '30000000',
            'remark': 'Test RDF'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testRegisterInvestorFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.registerInvestor({
            'companyId': 'SANDBOX',
            'parentCompanyId': 'STI_CHS',
            'requestUuid': '70HCB72E71D34F14',
            'uuidFaceRecog': '492F33851D634CFB',
            'title': '01',
            'firstName': 'Agus',
            'middleName': '',
            'lastName': 'Saputra',
            'optNPWP': '1',
            'NPWPNum': '001058893408123',
            'nationality': 'ID',
            'domicileCountry': 'ID',
            'religion': '2',
            'birthPlace': 'Semarang',
            'birthDate': '14081982',
            'gender': 'M',
            'isMarried': 'S',
            'motherMaidenName': 'Dina Maryati',
            'jobCode': '01',
            'education': '07',
            'idType': '01',
            'idNumber': '4147016201959999',
            'idIssuingCity': 'Jakarta Barat',
            'idExpiryDate': '26102099',
            'addressStreet': 'Jalan Mawar Melati',
            'addressRtRwPerum': '003009Sentosa',
            'addressKel': 'Cengkareng Barat',
            'addressKec': 'Cengkareng/Jakarta Barat',
            'zipCode': '11730',
            'homePhone1': '0214',
            'homePhone2': '7459',
            'officePhone1': '',
            'officePhone2': '',
            'mobilePhone1': '0812',
            'mobilePhone2': '12348331',
            'faxNum1': '',
            'faxNum2': '',
            'email': 'agus.saputra@gmail.com',
            'monthlyIncome': '8000000',
            'branchOpening': '0259',
            'institutionName': 'PT. BNI SECURITIES',
            'sid': 'IDD280436215354',
            'employerName': 'Salman',
            'employerAddDet': 'St Baker',
            'employerAddCity': 'Arrandelle',
            'jobDesc': 'Pedagang',
            'ownedBankAccNo': '0337109074',
            'idIssuingDate': '10122008'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testRegisterInvestorAccountFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.registerInvestorAccount({
            'companyId': ' NI001',
            'parentCompanyId': 'KSEI',
            'cifNumber': '10123456781',
            "accountType": "RDF",
            'currency': 'IDR',
            'openAccountReason': '2',
            'sourceOfFund': '1',
            'branchId': '0259',
            'bnisId': '19050813401',
            'sre': 'NI001CX5U00109'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryAccountHistoryFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryAccountHistory({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'requestUuid': 'E26DB4C8F6484E72',
            'accountNumber': '0315617904'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingClearingFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingClearing({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '1122334455',
            'beneficiaryAccountNumber': '3333333333',
            'beneficiaryAddress1': 'Jakarta',
            'beneficiaryAddress2': '',
            'beneficiaryBankCode': '140397',
            'beneficiaryName': 'Panji Samudra',
            'currency': 'IDR',
            'amount': '900000000',
            'remark': 'Test kliring',
            'chargingType': 'OUR'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingRTGSFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingRTGS({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '1122334455',
            'beneficiaryAccountNumber': '3333333333',
            'beneficiaryAddress1': 'Jakarta',
            'beneficiaryAddress2': '',
            'beneficiaryBankCode': 'CENAIDJA',
            'beneficiaryName': 'Panji Samudra',
            'currency': 'IDR',
            'amount': '150000000',
            'remark': 'Test rtgs',
            'chargingType': 'OUR'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryPaymentStatusFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryPaymentStatus({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'requestUuid': '106323AEB63D4FF0',
            'requestedUuid': '123456AAAAAABBB0'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquirtInterbankAccountFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.inquiryInterbankAccount({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '0115476117',
            'beneficiaryBankCode': '019',
            'beneficiaryAccountNumber': '01900000'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingInterbankFailed(self):
        print('\n==============================================')
        rekening_dana_funder = RDF(self.client)
        res = rekening_dana_funder.paymentUsingInterbank({
            'companyId': 'NI001',
            'parentCompanyId': 'KSEI',
            'accountNumber': '0315617904',
            'beneficiaryAccountNumber': '3333333333',
            'beneficiaryAccountName': 'KEN AROK',
            'beneficiaryBankCode': '014',
            'beneficiaryBankName': 'BANK BCA',
            'amount': '15000'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')
