import allure
import pytest
import json
import sys
from payload.facility.update_additional_cleaning_criteria_payload import \
    create_update_additional_cleaning_criteria_payload
from util.api_requests import Request
from util import constants as const
from util.validate_response import *
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.additional_cleaning_criteria
class TestAdditionalCleaningCriteria:

    @staticmethod
    def get_additional_cleaning_criteria_data(data):
        if data is None:
            return create_update_additional_cleaning_criteria_payload(ADDITIONAL_CLEANING_CRITERIA)["payload"]
        else:
            return data

    @allure.title("Get Additional Test Details")
    @allure.description("This test case tests API to get details of Additional Test in Cleaning Limit Policy")
    @allure.link("https://app.clickup.com/t/2k600kt")
    @pytest.mark.get_additional_cleaning_criteria
    def test_get_additional_cleaning_criteria(self):
        response = Request.get(const.ADDITIONAL_CLEANING_CRITERIA, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Update Additional Test Details")
    @allure.description("This test case tests API to update details of Additional Test in Cleaning Limit Policy")
    @allure.link("https://app.clickup.com/t/2k600na")
    @pytest.mark.update_additional_cleaning_criteria
    def test_update_additional_cleaning_criteria(self, data=None):
        global ADDITIONAL_CLEANING_CRITERIA
        get_additional_cleaning_criteria = self.test_get_additional_cleaning_criteria()["response"]
        ADDITIONAL_CLEANING_CRITERIA = json.loads(get_additional_cleaning_criteria)
        payload = self.get_additional_cleaning_criteria_data(data)
        response = Request.put(const.ADDITIONAL_CLEANING_CRITERIA, data=payload, use_facility_url=True)
        status_200(response)
        response = json.loads(response.text)
        assert response["result"] == {}
