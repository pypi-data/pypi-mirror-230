# MIT License

# Copyright (c) 2022 Sharashchandra

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
import logging.config
import requests
import pkgutil

_logger = logging.getLogger(__name__)


class TikTokBusinessClient:
    """

    The main class that is used to interact with the TikTok Business API.

    """

    _session = None
    BUSINESS_URL = "https://business-api.tiktok.com/open_api"
    SANDBOX_URL = "https://sandbox-ads.tiktok.com/open_api"
    VERSION = "v1.3"
    DEFAULT_CRED_PATH = os.path.join(os.path.expanduser("~"), "work", ".secrets", "tiktok_credentials.json")

    def __init__(self, access_token, advertiser_id, sandbox=False):
        self.__access_token = access_token
        self.advertiser_id = advertiser_id
        self.base_url = self.SANDBOX_URL if sandbox else self.BUSINESS_URL
        self.base_url = self.build_url(self.base_url, self.VERSION)

        if not self._session:
            self._create_session()

        self.discover_services()

    ###########################################################################
    #                          CLASS METHODS                                  #
    ###########################################################################
    @classmethod
    def from_json_file(cls,
                       advertiser_id: str,
                       json_file_path: str = DEFAULT_CRED_PATH,
                       sandbox: bool = False) -> 'TikTokBusinessClient':
        """

        Creates a TikTokBusinessClient instance from the json file containing the credentials.

        Args:
            advertiser_id: Advertiser id to be used.
            json_file_path: Path to the json file containing the credentials.
            sandbox: Whether to use sandbox or not.

        Returns:
            TikTokBusinessClient instance.

        """
        if not os.path.exists(json_file_path):
            raise Exception(f"File not found at {json_file_path}")
        with open(json_file_path, "r") as f:
            data = json.load(f)
        access_token = data["access_token"]

        return cls(access_token, advertiser_id, sandbox)

    @classmethod
    def from_dict(cls, data: dict) -> 'TikTokBusinessClient':
        """

        Creates a TikTokBusinessClient instance from the dictionary containing the credentials.

        Args:
            data: Dictionary containing the credentials.

        Returns:
            TikTokBusinessClient instance.

        """
        return cls(data["access_token"], data["advertiser_id"], data.get("sandbox"))

    ###########################################################################
    #                          STATIC METHODS                                 #
    ###########################################################################
    @staticmethod
    def get_advertiser_ids(json_file_path: str = DEFAULT_CRED_PATH) -> list[str]:
        """

        Fetches all the advertiser ids associated with the access token.

        Args:
            json_file_path: Path to the json file containing the credentials.

        Returns:
            List of advertiser ids.

        """
        if not os.path.exists(json_file_path):
            raise Exception(f"File not found at {json_file_path}")
        with open(json_file_path, "r") as f:
            creds = json.load(f)

        url = f'{TikTokBusinessClient.BUSINESS_URL}/{TikTokBusinessClient.VERSION}/oauth2/advertiser/get/'
        params = {
            "secret": creds["secret"],
            "app_id": creds["app_id"],
        }
        with requests.Session() as session:
            session.headers.update(
                {
                    "Content-Type": "application/json",
                    "Access-Token": creds["access_token"]
                }
            )
            response = session.get(url, params=params)
            if not response.ok:
                raise Exception(f"Error fetching advertiser ids: {response.content}")
            response = response.json()
            data_list = response["data"]["list"]
            return [data["advertiser_id"] for data in data_list]

    @staticmethod
    def _sanitize_params(params):
        def cast_to_dtype(dictionary):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    cast_to_dtype(value)
                else:
                    if isinstance(value, list):
                        dictionary[key] = json.dumps(value)
                    else:
                        dictionary[key] = str(value)

        cast_to_dtype(params)
        return params

    @staticmethod
    def __get_module_cls(module_name, module):
        module_name = module_name.title().replace("_", "")
        if hasattr(module, module_name):
            return getattr(module, module_name)

    @staticmethod
    def build_url(base_url, service_endpoint):
        base_url = (base_url + "/") if not base_url.endswith("/") else base_url
        service_endpoint = service_endpoint[1:] if service_endpoint.startswith("/") else service_endpoint
        service_endpoint = (service_endpoint + "/") if not service_endpoint.endswith("/") else service_endpoint

        return base_url + service_endpoint

    ###########################################################################
    #                          INSTANCE METHODS                               #
    ###########################################################################
    def _create_session(self):
        self._session = requests.Session()
        self._session.hooks['response'].append(self.__request_response_hook)
        self.__set_headers({"Access-Token": self.__access_token})

    def __set_headers(self, values):
        self._session.headers.update(values)

    def __request_response_hook(self, *args, **kwargs):
        self._session.headers.pop("Content-Type") if "Content-Type" in self._session.headers else None

    def discover_services(self):
        """

        Discovers all the services and loads them as attributes of the client instance.

        """
        cwd = os.path.dirname(os.path.realpath(__file__))
        services_path = os.path.join(cwd, "services")
        for importer, modname, ispkg in pkgutil.iter_modules([services_path]):
            module = importer.find_module(modname).load_module(modname)
            cls_instance = self.__get_module_cls(modname, module)
            if cls_instance:
                setattr(self, modname, cls_instance(client=self))
                _logger.debug(f"{modname} module loaded successfully")
        _logger.debug("Finished loading modules")

    def make_request(self, method, url, params={}, files=None):
        params.update({"advertiser_id": self.advertiser_id}) if "advertiser_id" not in params else None
        self.__set_headers({"Content-Type": "application/json"}) if not files else None
        params = self._sanitize_params(params)
        _logger.debug(method, url, params)
        if files:
            response = self._session.request(method, url, params=params, files=files)
        else:
            response = self._session.request(method, url, params=params)
        if not response.ok:
            return {"code": response.status_code, "message": response.content}

        response = response.json()
        return response

    def make_chunked_request(self, url, params={}, files=None):
        params.update({"advertiser_id": self.advertiser_id}) if "advertiser_id" not in params else None
        params = self._sanitize_params(params)
        _logger.debug("POST", url, params)
        if files:
            response = self._session.post(url, params=params, files=files)
        else:
            response = self._session.post(url, params=params)
        if not response.ok:
            return {"code": response.status_code, "message": response.content}

        response = response.json()
        return response

    def make_paginated_request(self, method, url, params={}, files=None):
        params.update({"page_size": 1000}) if "page_size" not in params else None
        initial_response = self.make_request(method, url, params, files)
        if initial_response["code"] == 0:
            total_pages = initial_response["data"]["page_info"]["total_page"]
            if total_pages > 1:
                for i in range(2, total_pages + 1):
                    params["page"] = i
                    response = self.make_request(method, url, params, files)
                    if response["code"] != 0:
                        return response
                    initial_response["data"]["list"].extend(response["data"]["list"])
                    initial_response["request_id"] = response["request_id"]
            initial_response["data"].pop("page_info")
            return initial_response
