import json
import uuid

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from mend_images_vuln._version import __version__, __tool_name__

CONN_TIMEOUT = 1800
API_URL_SUFFIX = 'api/v2.0'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
WS_HEADERS = {'content-type': 'application/json'}
DEFAULT_REMOTE_URL = ""
INVALID_FS_CHARS = [':', '*', '\\', '<', '>', '/', '"', '?', '|']
JAVA_BIN = "java"

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "POST", "OPTIONS"],
    backoff_factor=10
)


class Entities:
    ORGANIZATION = "orgs"
    PRODUCTS = "products"
    PROJECTS = "projects"
    LIBS = "types"
    LICS = "licensies"
    PROFILE = "profile"


class ScopeTypes:
    PROJECT = 'project'
    PRODUCT = 'product'
    ORGANIZATION = 'organization'
    GLOBAL = 'globalOrganization'
    SCOPE_TYPES = [PROJECT, PRODUCT, ORGANIZATION, GLOBAL]


def extract_url(url: str) -> str:
    url_ = url if url.startswith("https://") else f"https://{url}"
    url_ = url_.replace("http://", "")
    if "https://api-" not in url_:
        url_ = url_.replace("https://", "https://api-")
    pos = url_.find("/", 8)  # Not using any suffix, just direct url
    return url_[0:pos] if pos > -1 else url_


def create_proxyuri(proxyurl, proxyuser, proxypsw):
    is_https = "https://" in proxyurl
    proxy_ = proxyurl.replace("https://", "").replace("http://", "")
    if "@" not in proxy_ and proxyuser and proxypsw:
        proxy_ = f"{proxyuser}:{proxypsw}@" + proxy_
    proxy = proxy_ if proxyurl else ""
    if is_https:
        proxies = {"https": f"https://{proxy}", "http": f"http://{proxy}"} if proxy else {}
    else:
        proxies = {"http": f"http://{proxy}"} if proxy else {}
    return proxies


class MendAPI:
    def __init__(self,
                 user_key: str,
                 user_login : str,
                 token: str,
                 url: str = None,
                 token_type: str = ScopeTypes.ORGANIZATION,
                 timeout: int = CONN_TIMEOUT,
                 resp_format: str = "json",
                 proxy_url: str = "",
                 proxyuser: str = "",
                 proxypsw: str = "",
                 tool_details: tuple = (f"ps-{__tool_name__.replace('_','-')}", __version__),
                 **kwargs
                 ):
        """
            Mend Python API class
            :api_url: URL for the API to access (e.g. saas.whitesourcesoftware.com)
            :user_key: User Key to use
            :token: Token of scope
            :token_type: Scope Type (organization, product, project)
            :tool_details Tool name and version to include in Body and Header of API requests
        """
        def login(cls, u_login: str, u_key: str, u_token: str) -> tuple:
            url_ = cls.api_url + "/login"
            payload = json.dumps({
                "email": u_login,
                "userKey": u_key,
                "orgToken": u_token
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url_, headers=headers, data=payload, proxies=cls.proxies)
            try:
                jwt_token = json.loads(response.text)['retVal']['jwtToken']
                orguuid = json.loads(response.text)['retVal']['orgUuid']
            except:
                return "",""
            return jwt_token, orguuid

        self.user_login = user_login
        self.user_key = user_key
        self.token = token
        self.token_type = token_type
        self.timeout = timeout
        self.resp_format = resp_format
        self.session = requests.session()
        adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry_strategy)
        self.session.mount(prefix='https://', adapter=adapter)
        self.proxies = create_proxyuri(proxyurl=proxy_url, proxyuser=proxyuser, proxypsw=proxypsw)
        self.session.proxies.update(self.proxies)
        # Update the session's proxy settings
        self.url = extract_url(url)
        self.api_url = f"{self.url}/{API_URL_SUFFIX}"
        self.header_tool_details = {"agent": tool_details[0], "agentVersion": tool_details[1]}
        self.headers = {**WS_HEADERS,
                        **self.header_tool_details,
                        'ctxId': uuid.uuid1().__str__()}
        self.scope_contains = set()

        self.jwt_token, self.orguuid = login(self, user_login, user_key, token)

    def call_mend_api(self,
                      api_type : str,
                      token : str,
                      entity : str = None,
                      sub_entity : str = None,
                      cloud_native : bool = False,
                      kv_dict: dict = None) -> dict:

        if entity:
            cn = "cn/" if cloud_native else ""
            url = f"{self.url}/{cn}{API_URL_SUFFIX}/{entity}/{token}/{sub_entity}" if sub_entity else f"{self.url}/{cn}{API_URL_SUFFIX}/{entity}/{token}"

            payload = json.dumps(kv_dict) if kv_dict else '{}'
            status_code = 401
            while status_code == 401:
                headers = {
                    'Authorization': f'Bearer {self.jwt_token}',
                    'Content-Type': 'application/json'
                }
                response = requests.request(api_type, url, headers=headers, data=payload, proxies=self.proxies)
                status_code = response.status_code
                if status_code == 200:
                    return json.loads(response.text)
                elif status_code == 401:
                    self.jwt_token = self.login(self.user_login, self.user_key, self.token)
                else:
                    return {
                        "error" : json.loads(response.text)['retVal']['errorMessage'],
                        "error_code" : response.status_code
                    }
        else:
            return {
                "error": "Syntax error",
                "error_code" : 1
            }

