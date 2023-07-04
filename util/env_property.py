import os
import sys
from .constants import *

sys.path.append(".")


class Env:

    DATA = None

    def __init__(self):
        self.DATA = dict(os.environ)

    @staticmethod
    def get_data():
        global DATA
        DATA = dict(os.environ)
        return DATA

    @staticmethod
    def get_env_data(key):
        return DATA.get(key)

    @staticmethod
    def get_login_url(env):
        return DATA.get(env) + DATA.get("BASE_URL") + DATA.get("LOGIN_URL")

    @staticmethod
    def get_logout_url(env):
        return DATA.get(env) + DATA.get("BASE_URL") + "/auth/logout"

    @staticmethod
    def get_facilities_url(env):
        return DATA.get(env) + DATA.get("BASE_URL") + DATA.get("FACILITIES")

    @staticmethod
    def get_base_url(env):
        return DATA.get(env) + DATA.get("BASE_URL")
