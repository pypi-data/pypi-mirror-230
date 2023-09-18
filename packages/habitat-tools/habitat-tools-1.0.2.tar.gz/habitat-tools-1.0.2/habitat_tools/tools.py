from habitat_tools import APIRenderer, utils

from dotenv import load_dotenv
from typing import Union
import requests
import json
import os

load_dotenv()


class HabitatTools:
    API_URL = os.environ.get("API_URL", "http://127.0.0.1:8080/api")

    def __init__(self, *args, **kwargs):
        if self.API_URL is None:
            raise ValueError("An API URL must be provided in your .env file!")

        self.active = utils.test_connection(self.API_URL)

    def _request(self, method: str, endpoint: str, data: dict = {}, params: dict = {}):
        METHODS = {
            "get": requests.get,
            "post": requests.post,
            "patch": requests.patch,
        }
        req_method = METHODS.get(method)
        if req_method is not None:
            data = json.dumps(data, default=str)
            return req_method(f"{self.API_URL}/{endpoint}", data=data, params=params)

    def _response(self, response):
        data = {}
        message = "ok"

        resp_data = response.json()
        if response.status_code == 200:
            data = resp_data
        else:
            message = resp_data["detail"]
        return Response(response.status_code, data, message)

    def _api(self, method: str, endpoint: str, data: dict = {}, params: dict = {}):
        # If the init connection test failed, try again and return 503 if still not connected
        if not self.active:
            self.active = utils.test_connection(self.API_URL)
            if not self.active:
                return Response(503, {}, f"No connection to API at {self.API_URL}")

        resp = self._request(method, endpoint, data, params)
        return self._response(resp)

    def get_readings(self, data: dict = {}):
        return self._api("get", "readings", params=data)

    def create_reading(self, data: dict = {}):
        return self._api("post", "readings/create", data=data)

    def get_current_reading(self):
        return self._api("get", "readings/current")

    def filter_readings(self, data: dict = {}):
        return self._api("get", "readings/filter", data=data)

    def get_all_configs(self):
        return self._api("get", "environment/config")

    def get_default_config(self):
        return self._api("get", "environment/config/default")

    def get_active_config(self):
        return self._api("get", "environment/config/active")

    def get_config(self, config_id: int):
        return self._api("get", f"environment/config/{config_id}")

    def activate_config(self, config_id: int):
        return self._api("post", f"environment/config/{config_id}")

    def update_config(self, config_id: int, data: dict = {}):
        return self._api("patch", f"environment/config/{config_id}", data=data)

    def get_stats(self):
        return self._api("get", "environment/stats")


class Response(APIRenderer):
    def __init__(self, code: int, data: Union[dict, list], message: str = ""):
        self._code = code
        self._data = self.render(data)
        self._message = message

    @property
    def code(self):
        return self._code

    @property
    def data(self):
        return self._data

    @property
    def message(self):
        return self._message

    def __repr__(self):
        return f"{self.code} - {self.message}"


if __name__ == "__main__":
    HabitatTools()
