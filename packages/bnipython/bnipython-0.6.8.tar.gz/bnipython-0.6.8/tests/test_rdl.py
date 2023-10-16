from bnipython.lib.api.rdl import RDL
from bnipython.lib.util import constants
import unittest
from bnipython.lib.bniClient import BNIClient

class TestRDL(unittest.TestCase):
    client = BNIClient({
        'env': 'sandbox-dev',
        'appName': constants.APP_NAME,
        'clientId': constants.CLIENT_ID_ENCRYPT,
        'clientSecret': constants.CLIENT_SECRET_ENCRYPT,
        'apiKey': constants.API_KEY_ENCRYPT,
        'apiSecret': constants.API_SECRET_ENCRYPT
    })

    def testFaceRecog(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.faceRecognition({
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
        
    def testRegisterInvestor(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.registerInvestor({
            'companyId': 'SANDBOX',
            'parentCompanyId': 'STI_CHS',
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
            'idNumber': '4147016201959998',
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
    
    def testRegisterInvestorAccount(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.registerInvestorAccount({
            'companyId': 'SANDBOX',
            'parentCompanyId': 'STI_CHS',
            'cifNumber': '9100749959', 
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

    def testInquiryAccountInfo(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.inquiryAccountInfo({
            'companyId': 'SANDBOX', 
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryAccountBalance(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.inquiryAccountBalance({
            'companyId': 'SANDBOX', 
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryAccountHistory(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.inquiryAccountHistory({
            'companyId': 'SANDBOX', 
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingTransfer(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.paymentUsingTransfer({
            'companyId': 'SANDBOX', 
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117', 
            'beneficiaryAccountNumber': '0115471119', 
            'currency': 'IDR',
            'amount': '11500',
            'remark': 'Test RDL'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testInquiryPaymentStatus(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.inquiryPaymentStatus({
            'companyId': 'SANDBOX', 
            'parentCompanyId': 'STI_CHS',
            'requestedUuid': 'E8C6E0027F6E429F'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingClearing(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.paymentUsingClearing({
            'companyId': 'SANDBOX', 
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117', 
            'beneficiaryAccountNumber': '3333333333', 
            'beneficiaryAddress1': 'Jakarta', 
            'beneficiaryAddress2': '', 
            'beneficiaryBankCode': '140397', 
            'beneficiaryName': 'Panji Samudra', 
            'currency': 'IDR',
            'amount': '15000',
            'remark': 'Test kliring',
            'chargingType': 'OUR'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingRTGS(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.paymentUsingRTGS({
            'companyId': 'NI001', 
            'parentCompanyId': 'KSEI',
            'accountNumber': '0115476117',
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

    def testInquiryInterbankAccount(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.inquiryInterbankAccount({
            'companyId': 'NI001', 
            'parentCompanyId': 'KSEI',
            'accountNumber': '0115476117',
            'beneficiaryBankCode': '013',
            'beneficiaryAccountNumber': '01300000'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    def testPaymentUsingInterbank(self):
        print('\n==============================================')
        p2pl = RDL(self.client)
        res = p2pl.paymentUsingInterbank({
            'companyId': 'SANDBOX', 
            'parentCompanyId': 'STI_CHS',
            'accountNumber': '0115476117', 
            'beneficiaryAccountNumber': '3333333333', 
            'beneficiaryAccountName': 'KEN AROK', 
            'beneficiaryBankCode': '014', 
            'beneficiaryBankName': 'BANK BCA', 
            'amount': '15000'
        })
        data = res['response']['responseCode']
        self.assertEqual(data, '0001')
        print('\033[92m should return responseCode 0001 \033[0m')

    #################### CASES NEGATIVE #####################

    # def testFaceRecog(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.faceRecognition({
    #         'companyId': 'SANDBOX',
    #         'parentCompanyId': 'STI_CHS',
    #         'firstName': 'MOHAMMAD',
    #         'middleName': 'BAQER',
    #         'lastName': 'ZALQAD',
    #         'idNumber': '0141111121260118',
    #         'birthDate': '29-09-2021',
    #         'birthPlace': 'BANDUNG',
    #         'gender': 'M',
    #         'cityAddress': 'Bandung',
    #         'stateProvAddress': 'Jawa Barat',
    #         'addressCountry': 'ID',
    #         'streetAddress1': 'bandung',
    #         'streetAddress2': 'bandung',
    #         'postCodeAddress': '40914',
    #         'country': 'ID',
    #         'selfiePhoto': '546457658fhggjnrtn'})  
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')
        
    # def testRegisterInvestor(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.registerInvestor({
    #         'companyId': 'SANDBOX',
    #         'parentCompanyId': 'STI_CHS',
    #         'uuidFaceRecog': '492F33851D634CFB',
    #         'title': '01',
    #         'firstName': 'Agus',
    #         'middleName': '',
    #         'lastName': 'Saputra',
    #         'optNPWP': '1',
    #         'NPWPNum': '001058893408123',
    #         'nationality': 'ID',
    #         'domicileCountry': 'ID',
    #         'religion': '2',
    #         'birthPlace': 'Semarang',
    #         'birthDate': '14081982',
    #         'gender': 'M',
    #         'isMarried': 'S',
    #         'motherMaidenName': 'Dina Maryati',
    #         'jobCode': '01',
    #         'education': '07',
    #         'idType': '01',
    #         'idNumber': '4147016201959998',
    #         'idIssuingCity': 'Jakarta Barat',
    #         'idExpiryDate': '26102099',
    #         'addressStreet': 'Jalan Mawar Melati',
    #         'addressRtRwPerum': '003009Sentosa',
    #         'addressKel': 'Cengkareng Barat',
    #         'addressKec': 'Cengkareng/Jakarta Barat',
    #         'zipCode': '11730',
    #         'homePhone1': '0214',
    #         'homePhone2': '7459',
    #         'officePhone1': '',
    #         'officePhone2': '',
    #         'mobilePhone1': '0812',
    #         'mobilePhone2': '123483313',
    #         'faxNum1': '',
    #         'faxNum2': '',
    #         'email': 'agus.saputra@gmail.com',
    #         'monthlyIncome': '8000000',
    #         'branchOpening': '0259',
    #         'institutionName': 'PT. BNI SECURITIES',
    #         'sid': 'IDD280436215354',
    #         'employerName': 'Salman',
    #         'employerAddDet': 'St Baker',
    #         'employerAddCity': 'Arrandelle',
    #         'jobDesc': 'Pedagang',
    #         'ownedBankAccNo': '0337109074',
    #         'idIssuingDate': '10122008'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')
    
    # def testRegisterInvestorAccount(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.registerInvestorAccount({
    #         'companyId': 'SANDBOX',
    #         'parentCompanyId': 'STI_CHS',
    #         'cifNumber': '9100749645262456959', 
    #         'currency': 'IDR', 
    #         'openAccountReason': '2', 
    #         'sourceOfFund': '1', 
    #         'branchId': '0259',
    #         'bnisId': '19050813401', 
    #         'sre': 'NI001CX5U00109'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testInquiryAccountInfo(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.inquiryAccountInfo({
    #         'companyId': 'SANDBOX', 
    #         'parentCompanyId': 'STI_CHS',
    #         'accountNumber': '64567652'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testInquiryAccountBalance(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.inquiryAccountBalance({
    #         'companyId': 'SANDBOX', 
    #         'parentCompanyId': 'STI_CHS',
    #         'accountNumber': '4526756'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testInquiryAccountHistory(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.inquiryAccountHistory({
    #         'companyId': 'SANDBOX', 
    #         'parentCompanyId': 'STI_CHS',
    #         'accountNumber': '24565427'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testPaymentUsingTransfer(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.paymentUsingTransfer({
    #         'companyId': 'SANDBOX', 
    #         'parentCompanyId': 'STI_CHS',
    #         'accountNumber': '6245775', 
    #         'beneficiaryAccountNumber': '0115471119', 
    #         'currency': 'IDR',
    #         'amount': '11500',
    #         'remark': 'Test RDL'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testInquiryPaymentStatus(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.inquiryPaymentStatus({
    #         'companyId': 'SANDBOX4', 
    #         'parentCompanyId': 'STI_CHS4',
    #         'requestedUuid': 'E8C6E0027F6E429F'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testPaymentUsingClearing(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.paymentUsingClearing({
    #         'companyId': 'SANDBOX', 
    #         'parentCompanyId': 'STI_CHS',
    #         'accountNumber': '67347634', 
    #         'beneficiaryAccountNumber': '3333333333', 
    #         'beneficiaryAddress1': 'Jakarta', 
    #         'beneficiaryAddress2': '', 
    #         'beneficiaryBankCode': '140397', 
    #         'beneficiaryName': 'Panji Samudra', 
    #         'currency': 'IDR',
    #         'amount': '15000',
    #         'remark': 'Test kliring',
    #         'chargingType': 'OUR'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testPaymentUsingRTGS(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.paymentUsingRTGS({
    #         'companyId': 'NI001', 
    #         'parentCompanyId': 'KSEI',
    #         'accountNumber': '4537646376',
    #         'beneficiaryAccountNumber': '3333333333',
    #         'beneficiaryAddress1': 'Jakarta',
    #         'beneficiaryAddress2': '',
    #         'beneficiaryBankCode': 'CENAIDJA',
    #         'beneficiaryName': 'Panji Samudra',
    #         'currency': 'IDR',
    #         'amount': '150000000',
    #         'remark': 'Test rtgs',
    #         'chargingType': 'OUR'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testInquiryInterbankAccount(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.inquiryInterbankAccount({
    #         'companyId': 'NI001', 
    #         'parentCompanyId': 'KSEI',
    #         'accountNumber': '5625762w45',
    #         'beneficiaryBankCode': '013',
    #         'beneficiaryAccountNumber': '01300000'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')

    # def testPaymentUsingInterbank(self):
    #     print('\n==============================================')
    #     p2pl = RDL(self.client)
    #     res = p2pl.paymentUsingInterbank({
    #         'companyId': 'SANDBOX', 
    #         'parentCompanyId': 'STI_CHS',
    #         'accountNumber': '542576536', 
    #         'beneficiaryAccountNumber': '3333333333', 
    #         'beneficiaryAccountName': 'KEN AROK', 
    #         'beneficiaryBankCode': '014', 
    #         'beneficiaryBankName': 'BANK BCA', 
    #         'amount': '15000000'
    #     })
    #     data = res['response']['responseCode']
    #     self.assertEqual(data, '0001')
    #     print('\033[92m should return responseCode 0001 \033[0m')
