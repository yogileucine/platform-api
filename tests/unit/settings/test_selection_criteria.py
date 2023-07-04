from payload.facility.update_selection_criteria_payload import create_update_selection_criteria_payload
from util import constants as const
from util.validate_response import *
from util.api_requests import Request
import allure
import pytest
import sys
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.selection_criteria
class TestSelectionCriteria:

    @staticmethod
    def get_selection_criteria_payload(data):
        if data is None:
            return create_update_selection_criteria_payload()["payload"]
        else:
            return data

    @allure.title("Get Worst Product Selection Criteria Details")
    @allure.description("This test case tests API to get details of worst production selection criteria")
    @allure.link("https://app.clickup.com/t/2k600gp")
    @pytest.mark.get_selection_criteria
    def test_get_selection_criteria(self):
        url = const.WORST_CASE_SELECTION
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Add Worst Product Selection Criteria Details")
    @allure.description("This test case tests API to add worst production selection criteria")
    @allure.link("https://app.clickup.com/t/2k600j4")
    @pytest.mark.update_selection_criteria
    def test_update_selection_criteria(self, data=None):
        payload = self.get_selection_criteria_payload(data)
        url = const.WORST_CASE_SELECTION
        response = Request.post(url, data=payload, use_facility_url=True)
        status_200(response)
        return {"response": response.text}
