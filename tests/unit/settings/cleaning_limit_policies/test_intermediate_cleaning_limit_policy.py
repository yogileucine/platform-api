import allure
import json
import sys
from util import constants as const
from util.validate_response import *
from util.api_requests import Request
from util.common_methods import *
from random import *
sys.path.append(".")


@allure.title("Cleaning Limit Policy for Intermediates")
@allure.description("These test cases test API to Get and Update Cleaning Limit Policy for Actives")
@pytest.mark.intermediate_cleaning_limit_policy
@pytest.mark.active
@pytest.mark.unit
class TestIntermediateCleaningLimitPolicy:

    @staticmethod
    def get_intermediate_policy_data(data):
        if data is None:
            response = json.loads(INTERMEDIATE_POLICY)
            policy = response["policy"]
            policy["activesArl"] = {
                "value": (randint(1, 100)),
                "unit": "ppm"
            }
            policy["arl"] = {
                "value": (randint(1, 100)),
                "unit": "ppm"
            }
            return {"data": policy, "reason": "test"}
        return data["update_intermediate_policy_payload"]

    @allure.title("Get Cleaning Limit Policy for Actives")
    @allure.description("This test case Gets details of intermediate Cleaning Limit Policy for Actives")
    @allure.link("https://app.clickup.com/t/85zrh2182")
    @pytest.mark.get_intermediate_cleaning_limit_policy
    def test_get_intermediate_cleaning_limit_policy(self):
        response = Request.get(const.INTERMEDIATE_CLEANING_LIMIT_POLICY, use_facility_url=True)
        status_200(response)
        return response.text

    @allure.title("Update Cleaning Limit Policy for Actives")
    @allure.description("This test case Updates intermediate Cleaning Limit Policy for Actives")
    @allure.link("https://app.clickup.com/t/85zrh21cv")
    @pytest.mark.update_intermediate_cleaning_limit_policy
    def test_update_intermediate_policy(self, data=None):
        global INTERMEDIATE_POLICY
        INTERMEDIATE_POLICY = self.test_get_intermediate_cleaning_limit_policy()
        payload = self.get_intermediate_policy_data(data)
        response = Request.post(const.INTERMEDIATE_CLEANING_LIMIT_POLICY, data=payload, use_facility_url=True)
        status_200(response)
