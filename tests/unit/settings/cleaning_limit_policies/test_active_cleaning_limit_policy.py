from util.api_requests import Request
from util import constants as const
from util.validate_response import *
from test_data.data import unit_test_data as unit_data
import allure
import pytest
import json
import sys
sys.path.append("..")


@allure.title("Cleaning Limit Policy for Actives")
@allure.description("These test cases test API to Get and Update Cleaning Limit Policy for Actives")
@pytest.mark.active_cleaning_limit_policy
@pytest.mark.unit
class TestActiveCleaningLimitPolicy:

    @staticmethod
    def get_update_policy_data(data):
        if data is None:
            response = json.loads(ACTIVE_POLICY)
            policy = response["policy"]
            criteria = unit_data.ACTIVE_POLICY["criteria"]
            if policy[criteria] is False:
                policy[criteria] = True
            else:
                policy[criteria] = False
            return {"data": policy, "reason": "test"}
        return data["update_policy_payload"]

    @allure.title("Get Cleaning Limit Policy for Actives")
    @allure.description("This test case Gets details of Cleaning Limit Policy for Actives")
    @allure.link("https://app.clickup.com/t/2ngg9uj")
    @pytest.mark.get_active_cleaning_limit_policy
    def test_get_active_cleaning_limit_policy(self):
        response = Request.get(const.CLEANING_LIMIT_POLICY+const.CHEMICAL, use_facility_url=True)
        status_200(response)
        return response.text

    @allure.title("Update Cleaning Limit Policy for Actives")
    @allure.description("This test case Updates Cleaning Limit Policy for Actives")
    @allure.link("https://app.clickup.com/t/2ngg9wu")
    @pytest.mark.update_active_cleaning_limit_policy
    def test_update_active_policy(self, data=None):
        global ACTIVE_POLICY
        ACTIVE_POLICY = self.test_get_active_cleaning_limit_policy()
        payload = self.get_update_policy_data(data)
        url = const.CLEANING_LIMIT_POLICY
        response = Request.post(url, data=payload, use_facility_url=True)
        status_200(response)
