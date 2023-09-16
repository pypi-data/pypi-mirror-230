import json
from typing import Dict
import requests
from requests.adapters import HTTPAdapter

class identitytoolkit:
    
    def __init__(self, app: str, client_sig: str) -> None:
        self.requests   = requests.Session()
        self.base_url   = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty'
        
        adapter = HTTPAdapter(max_retries=3)

        for scheme in ('http://', 'https://'):
            self.requests.mount(scheme, adapter)
        
        self.requests.headers = {
                'Content-Type': 'application/json',
                'X-Android-Package': app,
                'X-Android-Cert': client_sig.upper(),
                'Accept-Language': 'in-ID, en-US',
                'X-Client-Version': 'Android/Fallback/X22001000/FirebaseCore-Android'
            }
    
    def send(self, url: str, data: dict):
        res = self.requests.post(url, json=data, verify=True).text
        try: return dict(json.loads(res))
        except: return res
    
    def verifyAssertion(self, idToken: str, apiKey: str) -> Dict[str, str]:
        data    = dict(
            autoCreate          = True,
            returnSecureToken   = True,
            postBody            = f'id_token={idToken}&providerId=google.com',
            requestUri          = 'http://localhost',
            returnIdpCredential = True
        )
        return self.send(f'{self.base_url}/verifyAssertion?key={apiKey}', data)
        
    def getAccountInfo(self, idToken: str, apiKey: str) -> Dict[str, str]:
        return self.send(f'{self.base_url}/getAccountInfo?key={apiKey}', dict(idToken = idToken))