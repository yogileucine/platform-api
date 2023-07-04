import sys
import requests
from .constants import *
from util import constants as const

sys.path.append(".")


class Request:

    @staticmethod
    def get(url, use_facility_url=False):
        if use_facility_url:
            facility_url = const.FACILITY_URL + url
            return requests.request("GET", facility_url, cookies=const.COOKIES, headers=HEADERS)
        return requests.request("GET", url, cookies=const.COOKIES, headers=HEADERS)

    @staticmethod
    def post(url, data, files=None, use_facility_url=False):
        if use_facility_url:
            facility_url = const.FACILITY_URL + url
            if files is not None:
                return requests.request("POST", facility_url, data=data, files=files, cookies=const.COOKIES)
            return requests.request("POST", facility_url, data=json.dumps(data), cookies=const.COOKIES,
                                    headers=HEADERS)
        return requests.request("POST", url, data=json.dumps(data), cookies=const.COOKIES, headers=HEADERS)

    @staticmethod
    def put(url, data, use_facility_url=False):
        if use_facility_url:
            facility_url = const.FACILITY_URL + url
            return requests.request("PUT", facility_url, data=json.dumps(data), cookies=const.COOKIES, headers=HEADERS)
        return requests.request("PUT", url, data=json.dumps(data), cookies=const.COOKIES, headers=HEADERS)

    @staticmethod
    def delete(url, data, use_facility_url=False):
        if use_facility_url:
            facility_url = const.FACILITY_URL + url
            return requests.request("DELETE", facility_url, data=json.dumps(data), cookies=const.COOKIES, headers=HEADERS)
        return requests.request("DELETE", url, data=json.dumps(data), cookies=const.COOKIES, headers=HEADERS)

