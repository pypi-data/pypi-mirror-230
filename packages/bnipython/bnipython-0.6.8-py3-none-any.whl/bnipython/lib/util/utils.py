import base64
import hmac
import hashlib
import json
import pytz
import random
import math
import string
from OpenSSL import crypto
from datetime import datetime

def generateSignature(params):
    # generate JWT header
    header = escape(base64.b64encode(
        '{"alg":"HS256","typ":"JWT"}'.encode('utf-8')).decode())
    # generate JWT payload
    payload = escape(base64.b64encode(json.dumps(
        params['body'], separators=(',', ':')).encode('utf-8')).decode())
    encript = header+'.'+payload
    # generate JWT signature
    jwtSignature = escape(base64.b64encode(hmac.new(str(params['apiSecret']).encode('utf-8'),
                                                    encript.encode('utf-8'), hashlib.sha256).digest()).decode())
    return f"{header}.{payload}.{jwtSignature}"


def generateClientId(appName):
    clientId = base64.b64encode(appName.encode('utf-8'))
    return f"IDBNI{clientId.decode()}"


def escape(string):
    return string.replace('+', '-').replace('/', '_').replace('=', '')

def getTimestamp():
    return datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%Y-%m-%dT%H:%M:%S+07:00')


def generateTokenSignature(params={'privateKeyPath', 'clientId', 'timeStamp'}):
    privateKeyPath = params['privateKeyPath']
    rsaPrivate = privateKeyPath.replace('./', '')
    keyFile = open(f'{rsaPrivate}', 'rb')
    key = keyFile.read()
    keyFile.close()

    pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key)
    clienId = params['clientId']
    times = params['timeStamp']
    data = f"{clienId}|{times}"

    dataBytes = bytes(data, encoding='utf-8')
    signature = base64.b64encode(crypto.sign(pkey, dataBytes, "sha256"))
    return signature.decode()


def generateSignatureServiceSnapBI(params={'body', 'method', 'url', 'accessToken', 'timeStamp', 'apiSecret'}):
    minify = json.dumps(params['body'], separators=(',', ':'))
    shaHex = hashlib.sha256(minify.encode('utf-8')).hexdigest()
    lower = shaHex.lower()

    stringToSign = f"{params['method']}:{params['url']}:{params['accessToken']}:{lower}:{params['timeStamp']}"

    gen_hmac = hmac.new(str(params['apiSecret']).encode(
        'utf-8'), stringToSign.encode('utf-8'), hashlib.sha512)
    data = base64.b64encode(gen_hmac.digest())
    return data.decode()

def randomNumber():
    randomNumber = random.randint(100000000, 999999999)
    unixTimeStamp = math.floor(datetime.timestamp((datetime.now())))
    return f'{randomNumber}{unixTimeStamp}'

def generateUUID(length=16):
    characters = string.ascii_uppercase + string.digits
    uuid = ''.join(random.choice(characters) for _ in range(length))
    return uuid