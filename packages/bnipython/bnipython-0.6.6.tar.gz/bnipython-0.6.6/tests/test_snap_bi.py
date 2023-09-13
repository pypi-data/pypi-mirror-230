from bnipython.lib.util import constants
from bnipython.lib.bniClient import BNIClient
from bnipython.lib.api.snapBI import SnapBI
import unittest


class TestSnapBI(unittest.TestCase):

    client = BNIClient({
        'env': 'dev',
        'appName': constants.APP_NAME_TEST,
        'clientId': constants.CLIENT_ID_ENCRYPT_SNAP_BI,
        'clientSecret': constants.CLIENT_SECRET_ENCRYPT_SNAP_BI,
        'apiKey': constants.API_KEY_ENCRYPT_SNAP_BI,
        'apiSecret': constants.API_SECRET_ENCRYPT_SNAP_BI,
    })

    def testGetBalance(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.balanceInquiry({
            'partnerReferenceNo': '202010290000000000002',
            'accountNo': '0115476117'
        })
        data = res['responseCode']
        self.assertEqual(data, '2001100')
        print('should return responseCode 2001100')

    def testBankStatement(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.bankStatement({
            'partnerReferenceNo': '202102102021',
            'accountNo': '115233527',
            'fromDateTime': '2010-01-01T12:08:56+07:00',
            'toDateTime': '2011-01-01T12:08:56+07:00'
        })
        data = res['responseCode']
        self.assertEqual(data, '2001400')
        print('should return responseCode 2001400')

    def testGetInternalAccountInquiry(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.internalAccountInquiry({
            'partnerReferenceNo': '202010290000000000002',
            'beneficiaryAccountNo': '0115476151'
        })
        data = res['responseCode']
        self.assertEqual(data, '2001500')
        print('should return responseCode 2001500')

    def testGetTransactionStatusInquiry(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transactionStatusInquiry({
            'originalPartnerReferenceNo': '202201911020000121',
            'originalReferenceNo': '220531103343739748',
            'originalExternalId': '20220531103340',
            'serviceCode': '17',
            'transactionDate': '2022-05-31',
            'amount': {
                'value': '15000.00',
                'currency': 'IDR'
            },
            'additionalInfo': {
                'deviceId': '123456',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2003600')
        print('should return responseCode 2003600')

    def testGetTransferIntraBank(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferIntraBank({
            'partnerReferenceNo': '207113OO00842662',
            'amount': {
                'value': '500000.00',
                'currency': 'IDR'
            },
            'beneficiaryAccountNo': '1000161562',
            'beneficiaryEmail': '',
            'currency': 'IDR',
            'customerReference': '207113OO00842662',
            'feeType': 'OUR',
            'remark': 'DANA20220426170737356898YuliantoSariputra',
            'sourceAccountNo': '1000164314',
            'transactionDate': '2022-09-05T10:29:57+07:00',
            'additionalInfo': {
                'deviceId': '123456',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2001700')
        print('should return responseCode 2001700')

    def testGetTransferRTGS(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferRTGS({
            'partnerReferenceNo': '20220513095840015788857',
            'amount': {
                'value': '100000001.00',
                'currency': 'IDR'
            },
            'beneficiaryAccountName': 'PTZomatoMediaIndonesia',
            'beneficiaryAccountNo': '3333333333',
            'beneficiaryAccountAddress': 'JlGatotSubrotoNoKav18RW1KuninganBarKecMampangPrptKotaJakartaSelatanDaerahKhususIbukotaJakarta12710',
            'beneficiaryBankCode': 'CENAIDJA',
            'beneficiaryBankName': 'PTBANKCENTRALASIATbk',
            'beneficiaryCustomerResidence': '1',
            'beneficiaryCustomerType': '2',
            'beneficiaryEmail': '',
            'currency': 'IDR',
            'customerReference': '20220513095840015788857',
            'feeType': 'OUR',
            'kodePos': '-',
            'recieverPhone': '-',
            'remark': 'DANA20220513095840015788857PTZomatoMediaIndonesia',
            'senderCustomerResidence': '-',
            'senderCustomerType': '-',
            'senderPhone': '',
            'sourceAccountNo': '0115476151',
            'transactionDate': '2020-06-17T01:03:04+07:00',
            'additionalInfo': {
                'deviceId': '',
                'channel': ''
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2002200')
        print('should return responseCode 2002200')

    def testGetTransferSKNBI(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferSKNBI({
            'partnerReferenceNo': '20220523150428586179325',
            'amount': {
                'value': '10000001.00',
                'currency': 'IDR'
            },
            'beneficiaryAccountName': 'PTZomatoMediaIndonesia',
            'beneficiaryAccountNo': '0115476117',
            'beneficiaryAddress': 'JlGatotSubrotoNoKav18RW1KuninganBarKecMampangPrptKotaJakartaSelatanDaerahKhususIbukotaJakarta12710',
            'beneficiaryBankCode': 'CENAIDJAXXX',
            'beneficiaryBankName': 'PTBANKCENTRALASIATbk',
            'beneficiaryCustomerResidence': '1',
            'beneficiaryCustomerType': '2',
            'beneficiaryEmail': '',
            'currency': 'IDR',
            'customerReference': '20220523150428586179325',
            'feeType': 'OUR',
            'kodePos': '',
            'recieverPhone': '',
            'remark': 'DANA20220523150428586179325PTZomatoMediaIndonesia',
            'senderCustomerResidence': '',
            'senderCustomerType': '',
            'senderPhone': '',
            'sourceAccountNo': '0115476151',
            'transactionDate': '2020-06-17T01:03:04+07:00',
            'additionalInfo': {
                'deviceId': '',
                'channel': ''
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2002300')
        print('should return responseCode 2002300')

    def testGetExternalAccountInquiry(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.externalAccountInquiry({
            'beneficiaryBankCode': '002',
            'beneficiaryAccountNo': '888801000157508',
            'partnerReferenceNo': '2020102900000000000001',
            'additionalInfo': {
                'deviceId': '123456',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2001600')
        print('should return responseCode 2001600')

    def testGetTransferInterBank(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferInterBank({
            'partnerReferenceNo': '2022090254000000000021',
            'amount': {
                'value': '55000',
                'currency': 'IDR'
            },
            'beneficiaryAccountName': 'BONIFASIUSPRIOKO',
            'beneficiaryAccountNo': '3333333333',
            'beneficiaryAddress': 'Palembang',
            'beneficiaryBankCode': '014',
            'beneficiaryBankName': 'BCA',
            'beneficiaryEmail': 'yories.yolanda@work.bri.co.id',
            'currency': 'IDR',
            'customerReference': '10052025',
            'sourceAccountNo': '0115476151',
            'transactionDate': '2022-06-14T12:08:56+07:00',
            'feeType': 'OUR',
            'additionalInfo': {
                'deviceId': '12345679237',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2001800')
        print('should return responseCode 2001800')

    ###################### CASES NEGATIVE #####################

    def testGetBalanceNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.balanceInquiry({
            'partnerReferenceNo': '2020102900000000000FF',
            'accountNo': '0115476117'
        })
        data = res['responseCode']
        self.assertEqual(data, '2001100')
        print('should return responseCode 2001100')

    def testBankStatementNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.bankStatement({
            'partnerReferenceNo': '2021021020FF',
            'accountNo': '115233527',
            'fromDateTime': '2010-01-01T12:08:56+07:00',
            'toDateTime': '2011-01-01T12:08:56+07:00'
        })
        data = res['responseCode']
        self.assertEqual(data, '2001400')
        print('should return responseCode 2001400')

    def testGetInternalAccountInquiryNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.internalAccountInquiry({
            'partnerReferenceNo': '2020102900000000000FF',
            'beneficiaryAccountNo': '0115476151'
        })
        data = res['responseCode']
        self.assertEqual(data, '2001500')
        print('should return responseCode 2001500')

    def testGetTransactionStatusInquiryNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transactionStatusInquiry({
            'originalPartnerReferenceNo': '2022019110200001FF',
            'originalReferenceNo': '220531103343739748',
            'originalExternalId': '20220531103340',
            'serviceCode': '17',
            'transactionDate': '2022-05-31',
            'amount': {
                'value': '15000.00',
                'currency': 'IDR'
            },
            'additionalInfo': {
                'deviceId': '123456',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2003600')
        print('should return responseCode 2003600')

    def testGetTransferIntraBankNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferIntraBank({
            'partnerReferenceNo': '207113OO008426FF',
            'amount': {
                'value': '500000.00',
                'currency': 'IDR'
            },
            'beneficiaryAccountNo': '1000161562',
            'beneficiaryEmail': '',
            'currency': 'IDR',
            'customerReference': '207113OO00842662',
            'feeType': 'OUR',
            'remark': 'DANA20220426170737356898YuliantoSariputra',
            'sourceAccountNo': '1000164314',
            'transactionDate': '2022-09-05T10:29:57+07:00',
            'additionalInfo': {
                'deviceId': '123456',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2001700')
        print('should return responseCode 2001700')

    def testGetTransferRTGSNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferRTGS({
            'partnerReferenceNo': '202205130958400157888FF',
            'amount': {
                'value': '100000001.00',
                'currency': 'IDR'
            },
            'beneficiaryAccountName': 'PTZomatoMediaIndonesia',
            'beneficiaryAccountNo': '3333333333',
            'beneficiaryAccountAddress': 'JlGatotSubrotoNoKav18RW1KuninganBarKecMampangPrptKotaJakartaSelatanDaerahKhususIbukotaJakarta12710',
            'beneficiaryBankCode': 'CENAIDJA',
            'beneficiaryBankName': 'PTBANKCENTRALASIATbk',
            'beneficiaryCustomerResidence': '1',
            'beneficiaryCustomerType': '2',
            'beneficiaryEmail': '',
            'currency': 'IDR',
            'customerReference': '20220513095840015788857',
            'feeType': 'OUR',
            'kodePos': '-',
            'recieverPhone': '-',
            'remark': 'DANA20220513095840015788857PTZomatoMediaIndonesia',
            'senderCustomerResidence': '-',
            'senderCustomerType': '-',
            'senderPhone': '',
            'sourceAccountNo': '0115476151',
            'transactionDate': '2020-06-17T01:03:04+07:00',
            'additionalInfo': {
                'deviceId': '',
                'channel': ''
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2002200')
        print('should return responseCode 2002200')

    def testGetTransferSKNBINegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferSKNBI({
            'partnerReferenceNo': '202205231504285861793FF',
            'amount': {
                'value': '10000001.00',
                'currency': 'IDR'
            },
            'beneficiaryAccountName': 'PTZomatoMediaIndonesia',
            'beneficiaryAccountNo': '0115476117',
            'beneficiaryAddress': 'JlGatotSubrotoNoKav18RW1KuninganBarKecMampangPrptKotaJakartaSelatanDaerahKhususIbukotaJakarta12710',
            'beneficiaryBankCode': 'CENAIDJAXXX',
            'beneficiaryBankName': 'PTBANKCENTRALASIATbk',
            'beneficiaryCustomerResidence': '1',
            'beneficiaryCustomerType': '2',
            'beneficiaryEmail': '',
            'currency': 'IDR',
            'customerReference': '20220523150428586179325',
            'feeType': 'OUR',
            'kodePos': '',
            'recieverPhone': '',
            'remark': 'DANA20220523150428586179325PTZomatoMediaIndonesia',
            'senderCustomerResidence': '',
            'senderCustomerType': '',
            'senderPhone': '',
            'sourceAccountNo': '0115476151',
            'transactionDate': '2020-06-17T01:03:04+07:00',
            'additionalInfo': {
                'deviceId': '',
                'channel': ''
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2002300')
        print('should return responseCode 2002300')

    def testGetExternalAccountInquiryNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.externalAccountInquiry({
            'beneficiaryBankCode': '002',
            'beneficiaryAccountNo': '888801000157508',
            'partnerReferenceNo': '20201029000000000000FF',
            'additionalInfo': {
                'deviceId': '123456',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2001600')
        print('should return responseCode 2001600')

    def testGetTransferInterBankNegative(self):
        print('\n==============================================')
        snap = SnapBI(
            self.client,  {'privateKeyPath': './private.key', 'channelId': '95221'})
        res = snap.transferInterBank({
            'partnerReferenceNo': '20220902540000000000FF',
            'amount': {
                'value': '55000',
                'currency': 'IDR'
            },
            'beneficiaryAccountName': 'BONIFASIUSPRIOKO',
            'beneficiaryAccountNo': '3333333333',
            'beneficiaryAddress': 'Palembang',
            'beneficiaryBankCode': '014',
            'beneficiaryBankName': 'BCA',
            'beneficiaryEmail': 'yories.yolanda@work.bri.co.id',
            'currency': 'IDR',
            'customerReference': '10052025',
            'sourceAccountNo': '0115476151',
            'transactionDate': '2022-06-14T12:08:56+07:00',
            'feeType': 'OUR',
            'additionalInfo': {
                'deviceId': '12345679237',
                'channel': 'mobilephone'
            }
        })
        data = res['responseCode']
        self.assertEqual(data, '2001800')
        print('should return responseCode 2001800')
if __name__ == '__main__':
    unittest.main()
