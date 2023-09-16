import requests
from requests.adapters import HTTPAdapter
from oauth2client.service_account import ServiceAccountCredentials

from .AuthHTTPAdapter import AuthHTTPAdapter
from .Authentication import Authentication
from .Database import Database
from .Storage import Storage

class Firebase:
    """ Firebase Interface """
    def __init__(self, config: dict):
        self.api_key = config["apiKey"]
        self.auth_domain = config["authDomain"]
        self.database_url = config["databaseURL"]
        self.storage_bucket = config["storageBucket"]
        self.credentials = None
        self.requests = requests.Session()
        if config.get("serviceAccount"):
            scopes = [
                'https://www.googleapis.com/auth/firebase.database',
                'https://www.googleapis.com/auth/userinfo.email',
                "https://www.googleapis.com/auth/cloud-platform"
            ]
            service_account_type = type(config["serviceAccount"])
            if service_account_type is str:
                self.credentials = ServiceAccountCredentials.from_json_keyfile_name(config["serviceAccount"], scopes)
            if service_account_type is dict:
                self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(config["serviceAccount"], scopes)
        #if is_appengine_sandbox():
            # Fix error in standard GAE environment
            # is releated to https://github.com/kennethreitz/requests/issues/3187
            # ProtocolError('Connection aborted.', error(13, 'Permission denied'))
        #adapter = appengine.AppEngineAdapter(max_retries=3)
        #else:
        adapter = HTTPAdapter(max_retries=3)

        for scheme in ('http://', 'https://'):
            self.requests.mount(scheme, adapter)

    def Authentication(self) -> 'Authentication':
        return Authentication(self.api_key, self.requests, self.credentials)

    def Database(self) -> 'Database':
        return Database(self.credentials, self.api_key, self.database_url, self.requests)

    def Storage(self) -> Storage:
        return Storage(self.credentials, self.storage_bucket, self.requests)
