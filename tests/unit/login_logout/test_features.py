import pytest
import sys
import allure
from util.api_requests import Request
from util import constants as const
from util.validate_response import *
from util.env_property import Env
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.features
class TestFeatures:

    @staticmethod
    def get_specific_feature_url(data):
        if data is None:
            return Env.get_base_url(const.ENV) + "/features/showOnDemand"
        return Env.get_base_url(const.ENV) + "/features/" + data["feature"]

    @allure.title("Get All Features of CLEEN Application")
    @allure.description("This test case Gets All Features of CLEEN Application")
    @allure.link("https://app.clickup.com/t/2v1pbtb")
    def test_get_features(self):
        url = Env.get_base_url(const.ENV) + const.FEATURES
        response = Request.get(url)
        status_200(response)
        return response.text

    @allure.title("Get Any One Features of CLEEN Application")
    @allure.description("This test case Gets Any One Features of CLEEN Application")
    @allure.link("https://app.clickup.com/t/2v1pbun")
    def test_get_specific_feature(self, data=None):
        url = self.get_specific_feature_url(data)
        response = Request.get(url)
        status_200(response)
        return response.text
