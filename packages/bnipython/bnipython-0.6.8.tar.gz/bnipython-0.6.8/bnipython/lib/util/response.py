def responseOGP(params={'res', 'resObj'}):
    try:
        if (params['res'][params['resObj']]['parameters']['responseCode'] != '0001'):
            code = params['res'][params['resObj']]['parameters']['responseCode']
            responseMessage = params['res'][params['resObj']]['parameters']['responseMessage']
            errorMessage = params['res'][params['resObj']]['parameters']['errorMessage']
            raise ValueError(f'\033[91m errorMessage: {errorMessage}, responseMessage: {responseMessage}, code: {code} \033[0m')
        else:
            return params['res']
    except Exception:
        code = params['res']['Response']['parameters']['responseCode']
        message = params['res']['Response']['parameters']['responseMessage']
        raise ValueError(f'\033[91m {code}:{message} \033[0m')

def responseSnapBI(params={'res'}):
    statusCodeSuccess = [
        '2000000',
        '2001100',
        '2001400',
        '2001500',
        '2001600',
        '2001700',
        '2001800',
        '2002200',
        '2002300',
        '2003600',
        '2007300'
    ]
    if not params['res']['responseCode'] in statusCodeSuccess:
        raise ValueError(
            f"\033[91m {params['res']['responseCode']} : {params['res']['responseMessage']} \033[0m")
    return params['res']

def responseRDN(params={'res', 'resObj'}):
    try:
        if (params['resObj'] == 'checkSIDResponse'):
            return params['res']   
        elif (params['resObj'] == 'sendDataStaticResponse'):
            return params['res'] 
        elif (params['res']['response']['responseCode'] != '0001'):
            code = params['res']['response']['responseCode']
            responseMessage = params['res']['response']['responseMessage']
            errorMessage = params['res']['response']['errorMessage']
            raise ValueError(f'\033[91m errorMessage: {errorMessage}, responseMessage: {responseMessage}, code: {code} \033[0m')
        else:
            return params['res']
    except Exception as e:
        code = params['res']['Response']['parameters']['responseCode']
        message = params['res']['Response']['parameters']['responseMessage']
        raise ValueError(f'\033[91m {code}:{message} \033[0m')
    
def responseRDL(params={'res', 'resObj'}):
    try:
        if (params['resObj'] == 'checkSIDResponse'):
            return params['res']    
        elif (params['resObj'] == 'sendDataStaticResponse'):
            return params['res'] 
        elif (params['res']['response']['responseCode'] != '0001'):
            code = params['res']['response']['responseCode']
            responseMessage = params['res']['response']['responseMessage']
            errorMessage = params['res']['response']['errorMessage']
            raise ValueError(f'\033[91m errorMessage: {errorMessage}, responseMessage: {responseMessage}, code: {code} \033[0m')
        else:
            return params['res']
    except Exception as e:
        code = params['res']['Response']['parameters']['responseCode']
        message = params['res']['Response']['parameters']['responseMessage']
        raise ValueError(f'\033[91m {code}:{message} \033[0m')

def responseRDF(params={'res'}):
    try:
        if (params['res']['response']['responseCode'] != '0001'):
            code = params['res']['response']['responseCode']
            responseMessage = params['res']['response']['responseMessage']
            errorMessage = params['res']['response']['errorMessage']
            raise ValueError(f'\033[91m errorMessage: {errorMessage}, responseMessage: {responseMessage}, code: {code} \033[0m')
        else:
            return params['res']
    except Exception as e:
        code = params['res']['Response']['parameters']['responseCode']
        message = params['res']['Response']['parameters']['responseMessage']
        raise ValueError(f'\033[91m {code}:{message} \033[0m')
