import pandas as pd
import requests
import time

class AuthError(Exception): pass

__username__ = None
__password__ = None
__token__    = None
__auth__     = None

restApiURL = 'https://restapi.ivolatility.com'

class Auth(requests.auth.AuthBase):
    def __init__(self, apiKey):
        self.apiKey = apiKey
    def __call__(self, r):
        r.headers["apiKey"] = self.apiKey
        return r

def setRestApiURL(url):
    global restApiURL
    restApiURL = url

def getToken(username, password):
    return requests.get(restApiURL + '/token/get', params={'username':username, 'password':password}).text

def createApiKey(nameKey, username, password):
    return requests.post(restApiURL + '/keys?nameKey={}'.format(nameKey), json={'username':username, 'password':password}).json()['key']
    
def deleteApiKey(nameKey, username, password):
    return requests.delete(restApiURL + '/keys?nameKey={}'.format(nameKey), json={'username':username, 'password':password}).status_code == 200
    
def setLoginParams(username = None, password = None, token = None, apiKey = None):
    global __username__
    global __password__
    global __token__
    global __auth__
    
    __username__ = username
    __password__ = password
    __token__    = token
    __auth__     = None
    if apiKey is not None:
        __auth__ = Auth(apiKey)

def setMethod(endpoint):
    loginParams = {}
    if __auth__ is not None:
        pass
    elif __token__ is not None:
        loginParams = {'token': __token__}
    elif __username__ is not None and __password__ is not None:
        loginParams = {'username':__username__, 'password':__password__}

    URL = restApiURL + endpoint
    
    def getMarketDataFromFile(urlForDetails):
        pause = 0.25

        isNotComplete = True
        while(isNotComplete):
            try:
                response = requests.get(urlForDetails, auth=__auth__).json()
                isNotComplete = response[0]['meta']['status'] != 'COMPLETE'
            except IndexError as e:
                time.sleep(pause)

        while True:
            try:
                urlForDownload = response[0]['data'][0]['urlForDownload']
                fileName = response[0]['data'][0]['fileName']
                break
            except IndexError as e:
                time.sleep(pause)
                response = requests.get(urlForDetails, auth=__auth__).json()
                
        while True:
            try:
                fileResponse = requests.get(urlForDownload, auth=__auth__)
                if fileResponse.status_code != 200:
                    print(fileResponse.status_code, fileResponse.text)
                    marketData = pd.DataFrame()
                    break
                fo = open(fileName, "wb")
                fo.write(fileResponse.content)
                fo.close()
                marketData = pd.read_csv(fileName, compression='gzip')
                if marketData.empty:
                    time.sleep(pause)
                    continue
                break
            except Exception as e:
                time.sleep(pause)

        return marketData

    def requestMarketData(params):
        marketData = pd.DataFrame()

        req = requests.get(URL, auth=__auth__, params=params)

        if req.status_code in [200, 400]:
            if endpoint in ['/quotes/options', '/equities/rtdl/options-rawiv']:
                fo = open(params['symbol']+'.csv', "wb")
                fo.write(req.content)
                fo.close()
                return pd.read_csv(params['symbol']+'.csv')
            
            try:
                req_json = req.json()
            except:
                print(req.status_code)
                return pd.DataFrame()

            exceptionEndpoints = ['/proxy/option-series', '/futures/prices/options', '/futures/market-structure', '/equities/option-series', '/futures/rt/single-fut-opt-rawiv','/futures/fut-opt-market-structure','/equities/eod/option-series-on-date']
            if endpoint in exceptionEndpoints:
                marketData = pd.DataFrame(req_json)
            elif 'status' in req_json and req_json['status']['code'] == 'PENDING':
                marketData = getMarketDataFromFile(req_json['status']['urlForDetails'])
            else:
                try:
                    print(req.status_code, req_json['message'])
                except:
                    pass
                
                try:
                    marketData = pd.DataFrame(req_json['data'])
                except:
                    marketData = pd.DataFrame()
        
        elif req.status_code == 401:
            print(req.status_code)
            raise AuthError(f"{req.status_code} Invalid password for username {__username__}")

        else:
            try:
                print(req.status_code, eval(req.text)['error'])
            except:
                print(req.status_code, req.text)
                
        return marketData

    def factory(**kwargs):
        params = dict(loginParams, **kwargs)
        if 'from_' in params.keys(): params['from'] = params.pop('from_')
        elif '_from' in params.keys(): params['from'] = params.pop('_from')
        elif '_from_' in params.keys(): params['from'] = params.pop('_from_')
        return requestMarketData(params)

    return factory
