
BNI API SDK - Python
===============
This is the Official Python API client / library for BNI API. 
Please visit [Digital Services](https://digitalservices.bni.co.id/en/) for more information about our product and visit our documentation page at [API Documentation](https://digitalservices.bni.co.id/documentation/public/en) for more technical details.

## 1. Installation

### 1.1 Using PyPI

```
pip install bnipython
```

### 1.2 Manual Installation

If you are not using PyPI, you can clone or [download](https://github.com/bni-api/bnipython/archive/refs/heads/main.zip) this repository.
Then import from bnipython folder. Or run Pip install from the repo folder.

```
pip install .
```

### 1.3 Using PyPI Install Third Party

```
pip install requests
pip install pyOpenSSL
pip install pytz
```

## 2. Usage

### 2.1 Choose an API Product

We have 2 API products you can use:
- [One Gate Payment](#22A-snap) - A solution for a company to integrate its application / system with banking transaction services. [documentation](https://digitalservices.bni.co.id/en/api-one-gate-payment)
- [Snap BI](https://apidevportal.bi.go.id/snap/info) - Integrate with SNAP BI [documentation](https://apidevportal.bi.go.id/snap/api-services)


### 2.2 Client Initialization and Configuration

Get your client key and server key from [Menu - Applications](https://digitalservices.bni.co.id/en/profile-menu/apps)
Create API client object

```python
from bnipython import BNIClient
# Create Core API instance
client = BNIClient({
  'env': False,
  'clientId': '{your-client-id}',
  'clientSecret': '{your-client-secret}',
  'apiKey': '{your-api-key}',
  'apiSecret': '{your-api-secret}',
  'appName': '{your-app-name}'
})
```

### 2.2.A One Gate Payment

Create `One Gate Payment` class object
```python
from bnipython import BNIClient, OneGatePayment

# Create Client instance
client = BNIClient({
  'env': False,
  'clientId': '{your-client-id}',
  'clientSecret': '{your-client-secret}',
  'apiKey': '{your-api-key}',
  'apiSecret': '{your-api-secret}',
  'appName': '{your-app-name}'
})

ogp = OneGatePayment(client)
```

Available methods for `One Gate Payment` class
#### Get Balance
```python
# return as Object
res = ogp.getBalance({
  'accountNo': '113183203'
})
```

#### Get In House Inquiry
```python
# return as Object
getInHouseInquiry = ogp.getInHouseInquiry({
  'accountNo': '113183203'
})
```

#### Do Payment
```python
# return as Object
doPayment = ogp.doPayment({
  'customerReferenceNumber': '20170227000000000020', # max 20 char client defined reference number
  'paymentMethod': '0', # 0: In-house (intra BNI), 1: RTGS transfer, 2: Kliring transfer
  'debitAccountNo': '113183203',
  'creditAccountNo': '115471119',
  'valueDate': '20170227000000000',
  'valueCurrency': 'IDR',
  'valueAmount': '100500',
  'remark': '', # optional
  'beneficiaryEmailAddress': 'mail@example.com', # optional
  'beneficiaryName': 'Mr. X', # optional max 50 char (mandatory if paymentMethod 1 / 2)
  'beneficiaryAddress1': 'Jakarta', # optional max 50 char (mandatory if paymentMethod 1 / 2)
  'beneficiaryAddress2': '', # optional max 50 char
  'destinationBankCode': '', # optional (mandatory if paymentMethod 1 / 2)
  'chargingModelId': 'OUR' # OUR: fee will be paid by sender (default), BEN: fee will be paid by beneficary, SHA: fee divided
})
```

#### Get Payment Status
```python
# return as Object
getPaymentStatus = ogp.getPaymentStatus({
  'customerReferenceNumber': '20170227000000000020' # max 20 char client defined reference number
})
```

#### Get Inter Bank Inquiry
```python
# return as Object
getInterBankInquiry = ogp.getInterBankInquiry({
  'customerReferenceNumber': '20180930112233003', # max 20 char client defined reference number
  'accountNum': '0115476117',
  'destinationBankCode': '014',
  'destinationAccountNum': '01400000'
})
```

#### Get Inter Bank Payment
```python
# return as Object
getInterBankPayment = ogp.getInterBankPayment({
  'customerReferenceNumber': '20170227000000000021', # max 20 char client defined reference number
  'amount': '100500',
  'destinationAccountNum': '3333333333',
  'destinationAccountName': 'BENEFICIARY NAME 1 UNTIL HERE1BENEFICIARY NAME 2(OPT) UNTIL HERE2',
  'destinationBankCode': '014',
  'destinationBankName': 'BCA',
  'accountNum': '115471119',
  'retrievalReffNum': '100000000024' # refference number for Interbank Transaction
})
```

#### Hold Amount
```python
# return as Object
holdAmount = ogp.holdAmount({
  'customerReferenceNumber': '20170504153218296', # max 20 char client defined reference number
  'amount': '12007',
  'accountNo': '0115476151',
  'detail': '' # optional
})
```

#### Hold Amount Release
```python
# return as Object
holdAmountRelease = ogp.holdAmountRelease({
  'customerReferenceNumber': '20170504153218296', # max 20 char client defined reference number
  'amount': '12007',
  'accountNo': '0115476151',
  'bankReference': '513668', # journal number. you can get this value from hold amount response
  'holdTransactionDate': '31052010' # the date when you do the hold transaction
})
```

### 2.2.B Snap BI

Create `Snap BI` class object
```python
from bnipython import BNIClient, SnapBI

# Create Client instance
client = BNIClient({
  'env': False,
  'clientId': '{your-client-id}',
  'clientSecret': '{your-client-secret}',
  'apiKey': '{your-api-key}',
  'apiSecret': '{your-api-secret}',
  'appName': '{your-app-name}'
})

snap = SnapBI(self.client, { 
  'privateKeyPath': '{your-rsa-private-key-path}', 
  'channelId': '{your-channel-id}' 
})
```

Available methods for `Snap BI` class
#### Balance Inquiry
```python
# return as Object
balanceInquiry = snap.balanceInquiry({
  'partnerReferenceNo': '202010290000000000002', # optional
  'accountNo': '0115476117'
})
```

#### Bank Statement
```python
# return as Object
bankStatement = snap.bankStatement({
  'partnerReferenceNo': '202010290000000000002', # optional
  'accountNo': '0115476117',
  'fromDateTime': '2010-01-01T12:08:56+07:00', # optional
  'toDateTime': '2011-01-01T12:08:56+07:00' # optional
})
```

#### Internal Account Inquiry
```python
# return as Object
internalAccountInquiry = snap.internalAccountInquiry({
  'partnerReferenceNo': '2020102900000000000001', # optional
  'beneficiaryAccountNo': '0115476151'
})
```

#### Transaction Status Inquiry
```python
# return as Object
transactionStatusInquiry = snap.transactionStatusInquiry({
  'originalPartnerReferenceNo': '20211213100434', # optional
  'originalReferenceNo': '20211220141520', # transaction reference number
  'originalExternalId': '20211220141520', # optional
  'serviceCode': '36', # SNAP BI service code
  'transactionDate': '2021-12-20',
  'amount': {
    'value': '12500',
    'currency': 'IDR'
  },
  'additionalInfo': {
    'deviceId': '123456', # optional
    'channel': 'mobilephone' # optional
  }
})
```

#### Transfer Intra Bank
```python
# return as Object
transferIntraBank = snap.transferIntraBank({
  'partnerReferenceNo': '202201911020300006', # transaction reference number
  'amount': {
    'value': '12500',
    'currency': 'IDR'
  },
  'beneficiaryAccountNo': '0115476117',
  'beneficiaryEmail': 'mail@example.com', # optional
  'currency': 'IDR', # optional
  'customerReference': '14045', # optional
  'feeType': 'OUR', # OUR: fee will be paid by sender (default), BEN: fee will be paid by beneficary, SHA: fee divided
  'remark': '', # optional
  'sourceAccountNo': '0115476151',
  'transactionDate': '2021-12-13',
  'additionalInfo': {
    'deviceId': '123456', # optional
    'channel': 'mobilephone' # optional
  }
})
```

#### Transfer RTGS
```python
# return as Object
'transferRTGS' = snap.transferRTGS({
  'partnerReferenceNo': '202201911020300011', # transaction reference number
  'amount': {
    'value': '150005001',
    'currency': 'IDR'
  },
  'beneficiaryAccountName': 'IKO',
  'beneficiaryAccountNo': '"3333333333',
  'beneficiaryAccountAddress': 'Jakarta Barat', # optional
  'beneficiaryBankCode': 'CENAIDJA',
  'beneficiaryBankName': 'PT. BANK CENTRAL ASIA Tbk.', # optional
  'beneficiaryCustomerResidence': '1',
  'beneficiaryCustomerType': '1',
  'beneficiaryEmail': 'mail@example.com', # optional
  'currency': 'IDR', # optional
  'customerReference': '202201911020300006',
  'feeType': 'OUR', # OUR: fee will be paid by sender (default), BEN: fee will be paid by beneficary, SHA: fee divided
  'kodePos': '12550', # optional
  'recieverPhone': '08123456789', # optional
  'remark': '', # optional
  'senderCustomerResidence': '1', # optional
  'senderCustomerType': '1', # optional
  'senderPhone': '08123456789', # optional
  'sourceAccountNo': '0115476151',
  'transactionDate': '2022-01-25',
  'additionalInfo': {
    'deviceId': '123456', # optional
    'channel': 'mobilephone' # optional
  }
})
```

#### Transfer SKNBI
```python
# return as Object
transferSKNBI = snap.transferSKNBI({
  'partnerReferenceNo': '202201911020300012', # transaction reference number
  'amount': {
    'value': '150005001',
    'currency': 'IDR'
  },
  'beneficiaryAccountName': 'SAN',
  'beneficiaryAccountNo': '3333333333',
  'beneficiaryAddress': 'Jakarta Barat', # optional
  'beneficiaryBankCode': '0140397',
  'beneficiaryBankName': 'PT. BANK CENTRAL ASIA Tbk.', # optional
  'beneficiaryCustomerResidence': '1',
  'beneficiaryCustomerType': '1',
  'beneficiaryEmail': 'mail@example.com', # optional
  'currency': 'IDR', # optional
  'customerReference': '202201911020300006',
  'feeType': 'OUR', # OUR: fee will be paid by sender (default), BEN: fee will be paid by beneficary, SHA: fee divided
  'kodePos': '12550', # optional
  'recieverPhone': '08123456789', # optional
  'remark': '', # optional
  'senderCustomerResidence': '1', # optional
  'senderCustomerType': '1', # optional
  'senderPhone': '08123456789', # optional
  'sourceAccountNo': '0115476151',
  'transactionDate': '2022-01-25',
  'additionalInfo': {
    'deviceId': '123456', # optional
    'channel': 'mobilephone' # optional
  }
})
```

#### External Account Inquiry
```python
# return as Object
externalAccountInquiry = snap.externalAccountInquiry({
  'beneficiaryBankCode': '002',
  'beneficiaryAccountNo': '888801000157508',
  'partnerReferenceNo': '2020102900000000000001', # optional
  'additionalInfo': {
    'deviceId': '123456', # optional
    'channel': 'mobilephone' # optional
  }
})
```

#### Transfer Inter Bank
```python
# return as Object
transferInterBank = snap.transferInterBank({
  'partnerReferenceNo': '2020102900000000000001', # transaction reference number
  'amount': {
    'value': '12345678',
    'currency': 'IDR'
  },
  'beneficiaryAccountName': 'Yories Yolanda',
  'beneficiaryAccountNo': '888801000003301',
  'beneficiaryAddress': 'Palembang', # optional
  'beneficiaryBankCode': '002',
  'beneficiaryBankName': 'Bank BRI', # optional
  'beneficiaryEmail': 'mail@example.com', # optional
  'currency': 'IDR', # optional
  'customerReference': '10052019', # optional
  'sourceAccountNo': '888801000157508',
  'transactionDate': '2019-07-03T12:08:56+07:00',
  'feeType': 'OUR', # OUR: fee will be paid by sender (default), BEN: fee will be paid by beneficary, SHA: fee divided
  'additionalInfo': {
    'deviceId': '123456', # optional
    'channel': 'mobilephone' # optional
  }
})

```

### 2.3.C RDN
Create `RDN` class object
```python
from bnipython import BNIClient, RDN

# Create Client instance
client = BNIClient({
  'env': False,
  'clientId': '{your-client-id}',
  'clientSecret': '{your-client-secret}',
  'apiKey': '{your-api-key}',
  'apiSecret': '{your-api-secret}',
  'appName': '{your-app-name}'
})
rekening_dana_nasabah = RDN(client)
```
Available methods for `RDN` class

#### Face Recognition
```python
# return as Object
faceRecognition = rekening_dana_nasabah.faceRecognition({
  'companyId': 'SANDBOX', 
  'parentCompanyId': 'STI_CHS', # optional
  'firstName': 'MOHAMMAD', # optional
  'middleName': 'BAQER', # optional
  'lastName': 'ZALQAD',
  'idNumber': '0141111121260118', # Identity Number (KTP only)
  'birthDate': '29-09-2021', # dd-mm-yyyy
  'birthPlace': 'BANDUNG', # e.g. : “Semarang”
  'gender': 'M', # "M" or "F"
  'cityAddress': 'Bandung',
  'stateProvAddress': 'Jawa Barat',
  'addressCountry': 'ID', # e.g.: “ID”
  'streetAddress1': 'bandung',
  'streetAddress2': 'bandung',
  'postCodeAddress': '40914',
  'country': 'ID', # e.g.: “ID”
  'selfiePhoto': '29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuP' # Base64 encoded selfie photo
})
```

#### Register Investor
```python
# return as Object
registerInvestor = rekening_dana_nasabah.registerInvestor({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'uuidFaceRecog': '492F33851D634CFB', # RequestUuid successed value from Face Recognition API (KYC valid)
  'title': '01', 
  'firstName': 'Agus', # e.g.: "Iko"
  'middleName': '', # optional
  'lastName': 'Saputra', # e.g.: "Wirya"
  'optNPWP': '1', # “1” or “0” (Default “1”)
  'NPWPNum': '001058893408123', # e.g.: "475519484101000"
  'nationality': 'ID', # e.g.: "ID"
  'domicileCountry': 'ID', # e.g.: "ID"
  'religion': '2',
  'birthPlace': 'Semarang', # e.g.: "Semarang"
  'birthDate': '14081982', # e.g.: "ddMMyyyy"
  'gender': 'M', # "M" or "F"
  'isMarried': 'S', 
  'motherMaidenName': 'Dina Maryati', # Mother’s name, e.g.: "Dina Maryati"
  'jobCode': '01', 
  'education': '7',
  'idType': '01', # For WNI, fill with "01" (KTP). For WNA, fill with "03" (Passport)
  'idNumber': '4147016201959998', # Identity Number (KTP for idType 01, Passport Number for idType 03)
  'idIssuingCity': 'Jakarta Barat', # KTP issued city, e.g.: "Jakarta Barat"
  'idExpiryDate': '26102099', # e.g.: "ddMMyyyy"
  'addressStreet': 'Jalan Mawar Melati', # e.g.: "Jalan Mawar Melati"
  'addressRtRwPerum': '003009Sentosa', # e.g.: "003009Sentosa"
  'addressKel': 'Cengkareng Barat', # e.g.: "Cengkareng Barat"
  'addressKec': 'Cengkareng/Jakarta Barat', # e.g.: "Cengkareng/Jakarta Barat"
  'zipCode': '11730', # Postal code, e.g.: "11730"
  'homePhone1': '0214', # Area code, e.g. 021 (3 - 4 digit) If not exist, fill with "9999"
  'homePhone2': '7459', # Number after area code (min 4 digit) If not exist, fill with "99999999"
  'officePhone1': '', # Area code, e.g. 021
  'officePhone2': '', # Number after area code
  'mobilePhone1': '0812', # Operator code, e.g. 0812 (4 digit) If not exist, fill with "0899"
  'mobilePhone2': '12348331', # Number after operator code (min 6 digit) If not exist, fill with "999999"
  'faxNum1': '', # Area code, e.g. 021
  'faxNum2': '', # Number after area code
  'email': 'agus.saputra@gmail.com', # Email address
  'monthlyIncome': '8000000',
  'branchOpening': '0259',
  'institutionName': 'PT. BNI SECURITIES', # PT. BNI SECURITIES
  'sid': 'IDD280436215354', # Single Investor ID
  'employerName': 'Salman', # Employer Name / Company Name
  'employerAddDet': 'St Baker', # Employer street address / home street address
  'employerAddCity': 'Arrandelle', # Employer city address / home city address
  'jobDesc': 'Pedagang',
  'ownedBankAccNo': '0337109074', # Investor’s owned bank account
  'idIssuingDate': '10122008'
})
```

#### CheckSID
```python
# return as Object
checkSID = rekening_dana_nasabah.checkSID({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS',
  'participantId': 'NI001', # Institution code, e.g.: "NI001"
  'sidNumber': 'IDD1206M9527805', # SID number, e.g.: "IDD12345002"
  'accountNumberOnKsei': 'NI001CRKG00146', 
  'branchCode': '0259',
  'ack': 'Y' # N = send data to KSEI & Y = check previous checkSID status
})
```

#### Register Investor Account
```python
# return as Object
registerInvestorAccount = rekening_dana_nasabah.registerInvestorAccount({
  'companyId': 'SANDBOX',≈
  'parentCompanyId': 'STI_CHS', # optional
  'cifNumber': '9100749959', # CIF number
  'currency': 'IDR', # "IDR" or "USD"
  'openAccountReason': '2', 
  'sourceOfFund': '1', 
  'branchId': '0259',
  'bnisId': '19050813401', # Value = requestUuid.
  'sre': 'NI001CX5U00109' # No. Sub rekening efek, e.g: “NI001CX5U00109”
})
```

#### Send Data Static
```python
# return as Object
sendDataStatic = rekening_dana_nasabah.sendDataStatic({
  'companyId': 'SPS App', # Registered participan id from KSEI
  'parentCompanyId': 'KSEI', # optional
  'participantCode': 'NI001', # Institution code, e.g: “NI001”
  'participantName': 'PT. BNI SECURITIES', # Institution name, e.g.: “PT. BNI SECURITIES”
  'investorName': 'SUMARNO', # Investor name
  'investorCode': 'IDD250436742277', # Investor code, e.g.: "IDD250436742277"
  'investorAccountNumber': 'NI001042300155', # Investor account number, e.g.: "NI001042300155"
  'bankAccountNumber': '242345393', # e.g.: "242345393"
  'activityDate': '20180511', # e.g: "yyyyMMdd"
  'activity': 'O' # (O)pening / (C)lose / (B)lock Account / (U)nblock Account
})
```

#### Inquiry Account Info
```python
# return as Object
inquiryAccountInfo = rekening_dana_nasabah.inquiryAccountInfo({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```

#### Inquiry Account Balance
```python
# return as Object
inquiryAccountInfo = rekening_dana_nasabah.inquiryAccountInfo({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```

#### Payment Using Transfer
```python
# return as Object
paymentUsingTransfer = rekening_dana_nasabah.paymentUsingTransfer({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', # Transfer/payment provider Account number
  'beneficiaryAccountNumber': '0115471119', # Transfer/payment receiver account number
  'currency': 'IDR', # e.g.: “IDR”
  'amount': '11500', # Total payment/transfer
  'remark': 'Test RDN' # Recommended for the reconciliation purpose
})
```

#### Inquiry Payment Status
```python
# return as Object
inquiryPaymentStatus = rekening_dana_nasabah.inquiryPaymentStatus({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'requestedUuid': 'E8C6E0027F6E429F'
})
```

#### Payment Using Clearing
```python
# return as Object
paymentUsingClearing = rekening_dana_nasabah.paymentUsingClearing({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', #  Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAddress1': 'Jakarta', # Receiver address, e.g.: "Jakarta"
  'beneficiaryAddress2': '', # optional
  'beneficiaryBankCode': '140397', 
  'beneficiaryName': 'Panji Samudra', # Receiver name
  'currency': 'IDR', # e.g., “IDR”
  'amount': '15000', # Total payment/transfer
  'remark': 'Test kliring', # Recommended for the reconciliation purpose
  'chargingType': 'OUR'
})
```

#### Payment Using RTGS
```python
# return as Object
paymentUsingRTGS = rekening_dana_nasabah.paymentUsingRTGS({
  'companyId': 'NI001', # Registered participan id from KSEI
  'parentCompanyId': 'KSEI', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAddress1': 'Jakarta', # Receiver address, e.g.: "Jakarta"
  'beneficiaryAddress2': '', # optional
  'beneficiaryBankCode': 'CENAIDJA',
  'beneficiaryName': 'Panji Samudra', # Receiver name
  'currency': 'IDR', # e.g., “IDR”
  'amount': '150000000', # Total payment/transfer
  'remark': 'Test rtgs', # Recommended for the reconciliation purpose
  'chargingType': 'OUR'
})
```

#### Inquiry Inter Bank Account
```python
# return as Object
inquiryInterbankAccount = rekening_dana_nasabah.inquiryInterbankAccount({
  'companyId': 'NI001', # Registered participan id from KSEI
  'parentCompanyId': 'KSEI', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryBankCode': '013',
  'beneficiaryAccountNumber': '01300000' # Transfer/payment receiver account number
})
```

#### Payment Using Inter Bank
```python
# return as Object
paymentUsingInterbank = rekening_dana_nasabah.paymentUsingInterbank({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAccountName': 'KEN AROK', # Get from Inquiry Interbank Account
  'beneficiaryBankCode': '014', 
  'beneficiaryBankName': 'BANK BCA',  # Get from Inquiry Interbank Account
  'amount': '15000' # Total payment/transfer
})
```

### 2.4.C RDL
Create `RDL` class object
```python
from bnipython import BNIClient, RDL

# Create Client instance
client = BNIClient({
  'env': False,
  'clientId': '{your-client-id}',
  'clientSecret': '{your-client-secret}',
  'apiKey': '{your-api-key}',
  'apiSecret': '{your-api-secret}',
  'appName': '{your-app-name}'
})
p2p_lending = RDL(client)
```
Available methods for `RDL` class

#### Face Recognition
```python
# return as Object
faceRecognition = p2p_lending.faceRecognition({
  'companyId': 'SANDBOX',
  'parentCompanyId': 'STI_CHS', # optional
  'firstName': 'MOHAMMAD', # optional
  'middleName': 'BAQER', # optional
  'lastName': 'ZALQAD', 
  'idNumber': '0141111121260118', # Identity Number (KTP only)
  'birthDate': '29-09-2021', # dd-mm-yyyy
  'birthPlace': 'BANDUNG', # e.g. : “Semarang”
  'gender': 'M', # "M" or "F"
  'cityAddress': 'Bandung',
  'stateProvAddress': 'Jawa Barat',
  'addressCountry': 'ID', # e.g.: “ID”
  'streetAddress1': 'bandung',
  'streetAddress2': 'bandung',
  'postCodeAddress': '40914',
  'country': 'ID', # e.g.: “ID”
  'selfiePhoto': '29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuP' # Base64 encoded selfie photo
})
```

#### Register Investor
```python
# return as Object
registerInvestor = p2p_lending.registerInvestor({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'uuidFaceRecog': '492F33851D634CFB', # RequestUuid successed value from Face Recognition API (KYC valid)
  'title': '01', 
  'firstName': 'Agus', # e.g.: "Iko"
  'middleName': '', # optional
  'lastName': 'Saputra', # e.g.: "Wirya"
  'optNPWP': '1',  # “1” or “0” (Default “1”)
  'NPWPNum': '001058893408123', # e.g.: "475519484101000"
  'nationality': 'ID', # e.g.: "ID"
  'domicileCountry': 'ID', # e.g.: "ID"
  'religion': '2', 
  'birthPlace': 'Semarang', # e.g.: "Semarang"
  'birthDate': '14081982', # e.g.: "ddMMyyyy"
  'gender': 'M', # "M" or "F"
  'isMarried': 'S',
  'motherMaidenName': 'Dina Maryati', # Mother’s name, e.g.: "Dina Maryati"
  'jobCode': '01',
  'education': '07',
  'idType': '01', # For WNI, fill with "01" (KTP). For WNA, fill with "03" (Passport)
  'idNumber': '4147016201959998', # Identity Number (KTP for idType 01, Passport Number for idType 03)
  'idIssuingCity': 'Jakarta Barat', # KTP issued city, e.g.: "Jakarta Barat"
  'idExpiryDate': '26102099', # e.g.: "ddMMyyyy"
  'addressStreet': 'Jalan Mawar Melati',
  'addressRtRwPerum': '003009Sentosa',
  'addressKel': 'Cengkareng Barat',
  'addressKec': 'Cengkareng/Jakarta Barat',
  'zipCode': '11730', # Postal code, e.g.: "11730"
  'homePhone1': '0214', # Area code, e.g. 021 (3 - 4 digit) If not exist, fill with "9999"
  'homePhone2': '7459', # Number after area code (min 4 digit) If not exist, fill with "99999999"
  'officePhone1': '', # Area code, e.g. 021
  'officePhone2': '', # Number after area code
  'mobilePhone1': '0812', # Operator code, e.g. 0812 (4 digit) If not exist, fill with "0899"
  'mobilePhone2': '12348331', # Number after operator code (min 6 digit) If not exist, fill with "999999"
  'faxNum1': '', # Area code, e.g. 021
  'faxNum2': '', # Number after area code
  'email': 'agus.saputra@gmail.com', # Email address
  'monthlyIncome': '8000000',
  'branchOpening': '0259',
  'institutionName': 'PT. BNI SECURITIES', # PT. BNI SECURITIES
  'sid': 'IDD280436215354',  # Single Investor ID
  'employerName': 'Salman',  # Employer Name / Company Name
  'employerAddDet': 'St Baker', # Employer street address / home street address
  'employerAddCity': 'Arrandelle', # Employer city address / home city address
  'jobDesc': 'Pedagang',
  'ownedBankAccNo': '0337109074', # Investor’s owned bank account
  'idIssuingDate': '10122008'
})
```

#### Register Investor Account
```python
# return as Object
registerInvestorAccount = p2p_lending.registerInvestorAccount({
  'companyId': 'SANDBOX',≈
  'parentCompanyId': 'STI_CHS', # optional
  'cifNumber': '9100749959', # CIF number
  'currency': 'IDR', # "IDR" or "USD"
  'openAccountReason': '2', 
  'sourceOfFund': '1', 
  'branchId': '0259',
  'bnisId': '19050813401', # Value = requestUuid.
  'sre': 'NI001CX5U00109' # No. Sub rekening efek, e.g: “NI001CX5U00109”
})
```

#### Inquiry Account Info
```python
# return as Object
inquiryAccountInfo = p2p_lending.inquiryAccountInfo({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```


#### Inquiry Account Balance
```python
# return as Object
inquiryAccountInfo = p2p_lending.inquiryAccountInfo({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```

#### Inquiry Account History
```python
# return as Object
inquiryAccountHistory = p2p_lending.inquiryAccountHistory({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```

#### Payment Using Transfer
```python
# return as Object
inquiryAccountHistory = p2p_lending.paymentUsingTransfer({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', # Account number
  'beneficiaryAccountNumber': '0115471119', # Transfer/payment receiver account number
  'currency': 'IDR', # e.g.: “IDR”
  'amount': '11500', # Total payment/transfer
  'remark': 'Test RDL' # Recommended for the reconciliation purpose
})
```

#### Inquiry Payment Status
```python
# return as Object
inquiryPaymentStatus = p2p_lending.inquiryPaymentStatus({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'requestedUuid': 'E8C6E0027F6E429F'
})
```

#### Payment Using Clearing
```python
# return as Object
paymentUsingClearing = p2p_lending.paymentUsingClearing({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', #  Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAddress1': 'Jakarta', # Receiver address, e.g.: "Jakarta"
  'beneficiaryAddress2': '', # optional
  'beneficiaryBankCode': '140397', 
  'beneficiaryName': 'Panji Samudra', # Receiver name
  'currency': 'IDR', # e.g., “IDR”
  'amount': '15000', # Total payment/transfer
  'remark': 'Test kliring', # Recommended for the reconciliation purpose
  'chargingType': 'OUR'
})
```

#### Payment Using RTGS
```python
# return as Object
paymentUsingRTGS = p2p_lending.paymentUsingRTGS({
  'companyId': 'NI001', # Registered participan id from KSEI
  'parentCompanyId': 'KSEI', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAddress1': 'Jakarta', # Receiver address, e.g.: "Jakarta"
  'beneficiaryAddress2': '', # optional
  'beneficiaryBankCode': 'CENAIDJA',
  'beneficiaryName': 'Panji Samudra', # Receiver name
  'currency': 'IDR', # e.g., “IDR”
  'amount': '150000000', # Total payment/transfer
  'remark': 'Test rtgs', # Recommended for the reconciliation purpose
  'chargingType': 'OUR'
})
```


#### Inquiry Inter Bank Account
```python
# return as Object
inquiryInterbankAccount = p2p_lending.inquiryInterbankAccount({
  'companyId': 'NI001', # Registered participan id from KSEI
  'parentCompanyId': 'KSEI', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryBankCode': '013',
  'beneficiaryAccountNumber': '01300000' # Transfer/payment receiver account number
})
```

#### Payment Using Inter Bank
```python
# return as Object
paymentUsingInterbank = p2p_lending.paymentUsingInterbank({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAccountName': 'KEN AROK', # Get from Inquiry Interbank Account
  'beneficiaryBankCode': '014', 
  'beneficiaryBankName': 'BANK BCA',  # Get from Inquiry Interbank Account
  'amount': '15000' # Total payment/transfer
})
```

### 2.5.E RDF
Create `RDF` class object
```python
from bnipython import BNIClient, RDF

# Create Client instance
client = BNIClient({
  'env': False,
  'clientId': '{your-client-id}',
  'clientSecret': '{your-client-secret}',
  'apiKey': '{your-api-key}',
  'apiSecret': '{your-api-secret}',
  'appName': '{your-app-name}'
})
rekening_dana_funder = RDF(client)
```
Available methods for `RDF` class

#### Face Recognition
```python
# return as Object
faceRecognition = rekening_dana_funder.faceRecognition({
  'companyId': 'SANDBOX',
  'parentCompanyId': 'STI_CHS', # optional
  'firstName': 'MOHAMMAD', # optional
  'middleName': 'BAQER', # optional
  'lastName': 'ZALQAD', 
  'idNumber': '0141111121260118', # Identity Number (KTP only)
  'birthDate': '29-09-2021', # dd-mm-yyyy
  'birthPlace': 'BANDUNG', # e.g. : “Semarang”
  'gender': 'M', # "M" or "F"
  'cityAddress': 'Bandung',
  'stateProvAddress': 'Jawa Barat',
  'addressCountry': 'ID', # e.g.: “ID”
  'streetAddress1': 'bandung',
  'streetAddress2': 'bandung',
  'postCodeAddress': '40914',
  'country': 'ID', # e.g.: “ID”
  'selfiePhoto': '29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuP' # Base64 encoded selfie photo
})
```

#### Register Investor
```python
# return as Object
registerInvestor = rekening_dana_funder.registerInvestor({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'uuidFaceRecog': '492F33851D634CFB', # RequestUuid successed value from Face Recognition API (KYC valid)
  'title': '01', 
  'firstName': 'Agus', # e.g.: "Iko"
  'middleName': '', # optional
  'lastName': 'Saputra', # e.g.: "Wirya"
  'optNPWP': '1',  # “1” or “0” (Default “1”)
  'NPWPNum': '001058893408123', # e.g.: "475519484101000"
  'nationality': 'ID', # e.g.: "ID"
  'domicileCountry': 'ID', # e.g.: "ID"
  'religion': '2', 
  'birthPlace': 'Semarang', # e.g.: "Semarang"
  'birthDate': '14081982', # e.g.: "ddMMyyyy"
  'gender': 'M', # "M" or "F"
  'isMarried': 'S',
  'motherMaidenName': 'Dina Maryati', # Mother’s name, e.g.: "Dina Maryati"
  'jobCode': '01',
  'education': '07',
  'idType': '01', # For WNI, fill with "01" (KTP). For WNA, fill with "03" (Passport)
  'idNumber': '4147016201959998', # Identity Number (KTP for idType 01, Passport Number for idType 03)
  'idIssuingCity': 'Jakarta Barat', # KTP issued city, e.g.: "Jakarta Barat"
  'idExpiryDate': '26102099', # e.g.: "ddMMyyyy"
  'addressStreet': 'Jalan Mawar Melati',
  'addressRtRwPerum': '003009Sentosa',
  'addressKel': 'Cengkareng Barat',
  'addressKec': 'Cengkareng/Jakarta Barat',
  'zipCode': '11730', # Postal code, e.g.: "11730"
  'homePhone1': '0214', # Area code, e.g. 021 (3 - 4 digit) If not exist, fill with "9999"
  'homePhone2': '7459', # Number after area code (min 4 digit) If not exist, fill with "99999999"
  'officePhone1': '', # Area code, e.g. 021
  'officePhone2': '', # Number after area code
  'mobilePhone1': '0812', # Operator code, e.g. 0812 (4 digit) If not exist, fill with "0899"
  'mobilePhone2': '12348331', # Number after operator code (min 6 digit) If not exist, fill with "999999"
  'faxNum1': '', # Area code, e.g. 021
  'faxNum2': '', # Number after area code
  'email': 'agus.saputra@gmail.com', # Email address
  'monthlyIncome': '8000000',
  'branchOpening': '0259',
  'institutionName': 'PT. BNI SECURITIES', # PT. BNI SECURITIES
  'sid': 'IDD280436215354',  # Single Investor ID
  'employerName': 'Salman',  # Employer Name / Company Name
  'employerAddDet': 'St Baker', # Employer street address / home street address
  'employerAddCity': 'Arrandelle', # Employer city address / home city address
  'jobDesc': 'Pedagang',
  'ownedBankAccNo': '0337109074', # Investor’s owned bank account
  'idIssuingDate': '10122008'
})
```

#### Register Investor Account
```python
# return as Object
registerInvestorAccount = rekening_dana_funder.registerInvestorAccount({
  'companyId': 'SANDBOX',≈
  'parentCompanyId': 'STI_CHS', # optional
  'cifNumber': '9100749959', # CIF number
  'currency': 'IDR', # "IDR" or "USD"
  'openAccountReason': '2', 
  'sourceOfFund': '1', 
  'branchId': '0259',
  'bnisId': '19050813401', # Value = requestUuid.
  'sre': 'NI001CX5U00109' # No. Sub rekening efek, e.g: “NI001CX5U00109”
})
```

#### Inquiry Account Info
```python
# return as Object
inquiryAccountInfo = rekening_dana_funder.inquiryAccountInfo({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```


#### Inquiry Account Balance
```python
# return as Object
inquiryAccountInfo = rekening_dana_funder.inquiryAccountInfo({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```

#### Inquiry Account History
```python
# return as Object
inquiryAccountHistory = rekening_dana_funder.inquiryAccountHistory({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117' # Account number
})
```

#### Payment Using Transfer
```python
# return as Object
inquiryAccountHistory = rekening_dana_funder.paymentUsingTransfer({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', # Account number
  'beneficiaryAccountNumber': '0115471119', # Transfer/payment receiver account number
  'currency': 'IDR', # e.g.: “IDR”
  'amount': '11500', # Total payment/transfer
  'remark': 'Test RDL' # Recommended for the reconciliation purpose
})
```

#### Inquiry Payment Status
```python
# return as Object
inquiryPaymentStatus = rekening_dana_funder.inquiryPaymentStatus({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'requestedUuid': 'E8C6E0027F6E429F'
})
```

#### Payment Using Clearing
```python
# return as Object
paymentUsingClearing = rekening_dana_funder.paymentUsingClearing({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', #  Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAddress1': 'Jakarta', # Receiver address, e.g.: "Jakarta"
  'beneficiaryAddress2': '', # optional
  'beneficiaryBankCode': '140397', 
  'beneficiaryName': 'Panji Samudra', # Receiver name
  'currency': 'IDR', # e.g., “IDR”
  'amount': '15000', # Total payment/transfer
  'remark': 'Test kliring', # Recommended for the reconciliation purpose
  'chargingType': 'OUR'
})
```

#### Payment Using RTGS
```python
# return as Object
paymentUsingRTGS = rekening_dana_funder.paymentUsingRTGS({
  'companyId': 'NI001', # Registered participan id from KSEI
  'parentCompanyId': 'KSEI', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAddress1': 'Jakarta', # Receiver address, e.g.: "Jakarta"
  'beneficiaryAddress2': '', # optional
  'beneficiaryBankCode': 'CENAIDJA',
  'beneficiaryName': 'Panji Samudra', # Receiver name
  'currency': 'IDR', # e.g., “IDR”
  'amount': '150000000', # Total payment/transfer
  'remark': 'Test rtgs', # Recommended for the reconciliation purpose
  'chargingType': 'OUR'
})
```


#### Inquiry Inter Bank Account
```python
# return as Object
inquiryInterbankAccount = rekening_dana_funder.inquiryInterbankAccount({
  'companyId': 'NI001', # Registered participan id from KSEI
  'parentCompanyId': 'KSEI', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryBankCode': '013',
  'beneficiaryAccountNumber': '01300000' # Transfer/payment receiver account number
})
```

#### Payment Using Inter Bank
```python
# return as Object
paymentUsingInterbank = rekening_dana_funder.paymentUsingInterbank({
  'companyId': 'SANDBOX', # Registered participan id from KSEI
  'parentCompanyId': 'STI_CHS', # optional
  'accountNumber': '0115476117', # Transfer/payment provider account number
  'beneficiaryAccountNumber': '3333333333', # Transfer/payment receiver account number
  'beneficiaryAccountName': 'KEN AROK', # Get from Inquiry Interbank Account
  'beneficiaryBankCode': '014', 
  'beneficiaryBankName': 'BANK BCA',  # Get from Inquiry Interbank Account
  'amount': '15000' # Total payment/transfer
})
```

## Get help

* [Digital Services](https://digitalservices.bni.co.id/en/)
* [API documentation](https://digitalservices.bni.co.id/documentation/public/en)
* [Stackoverflow](https://stackoverflow.com/users/19817167/bni-api-management)
* Can't find answer you looking for? email to [apisupport@bni.co.id](mailto:apisupport@bni.co.id)
