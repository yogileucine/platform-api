import pytest
import allure
from http.cookies import SimpleCookie
from util.api_requests import Request
from util import constants as const
from util.validate_response import *
from util.env_property import Env


@pytest.mark.unit
class TestLoginLogout:

    @staticmethod
    def get_credential_payload(data):
        if data is None:
            return {
                "username": Env.get_env_data("ADMIN_USERNAME"),
                "password": Env.get_env_data("ADMIN_PASSWORD")
            }
        return {
            "username": data["username"],
            "password": data["password"]
        }

    @allure.title("Login into CLEEN Application")
    @allure.description("This test case Login into CLEEN Application")
    @allure.link("https://app.clickup.com/t/2v1pbmq")
    @pytest.mark.login
    def test_login_user_id(self, data=None):
        payload = self.get_credential_payload(data)
        url = Env.get_login_url(const.ENV)
        response = Request.post(url, data=payload)
        status_200(response)
        raw_cookie = response.headers['Set-Cookie']
        cookie = SimpleCookie()
        cookie.load(raw_cookie)
        cookies = {k: v.value for k, v in cookie.items()}
        const.COOKIES = cookies

    @allure.title("Logout of CLEEN Application")
    @allure.description("This test case Logout of CLEEN Application")
    @allure.link("https://app.clickup.com/t/2v1pbqa")
    @pytest.mark.order("last")
    def test_logout(self):
        url = Env.get_logout_url(const.ENV)
        payload = {"headers": {}}
        response = Request.post(url, data=payload)
        status_200(response)
        const.COOKIES = None
