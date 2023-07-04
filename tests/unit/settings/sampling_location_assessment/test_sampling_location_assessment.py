import json
import sys
import allure
import pytest
from payload.facility.archive_unarchive_payload import archive_payload, unarchive_payload
from payload.facility.update_sampling_location_payload import create_update_auto_selection_policies_payload_for_post
from payload.facility.update_sampling_location_payload import create_update_new_assessment_attribute
from test_data.data import unit_test_data as unit_data
from util import constants as const
from util.api_requests import Request
from util.validate_response import *

sys.path.append(".")


@pytest.mark.unit
@pytest.mark.sampling_location_assessment
class TestSamplingLocationAssessment:

    # This method is used to get all sampling id
    @staticmethod
    def get_sampling_id():
        sampling_id_list = []
        for i in SAMPLING_SELECTION["policy"]:
            sampling_id = i["id"]
            sampling_id_list.append(sampling_id)
        return sampling_id_list

    # This method is used to get all the attribute ID
    @staticmethod
    def get_attribute_id():
        for i in ASSESSMENT_ATTRIBUTE_ID:
            if unit_data.ASSESSMENT_ATTRIBUTE_NAME["name"] == i["name"]:
                attribute_id = i["id"]
                return attribute_id
        return None

    # This method is used to get sampling location assessment attribute payload
    @staticmethod
    def get_assessment_attribute_payload(data):
        assess_atr = ASSESSMENT_ATTRIBUTE_ID
        attribute_name = unit_data.ASSESSMENT_ATTRIBUTE_NAME["name"]
        atr_name = []
        for i in assess_atr:
            atr_name.append(i["name"])
        if data is None:
            if attribute_name not in atr_name:
                return create_update_new_assessment_attribute(attribute_name)["payload"]
            else:
                return None
        else:
            return data["sampling_assessment_attribute"]

    # This method is used to get the sampling location Auto Selection policies payload
    @staticmethod
    def get_auto_selection_policies_payload(data, contact_type):
        atr_id = ATTRIBUTE_ID
        atr_property_id = ATTRIBUTE_PROPERTY_ID
        if data is None:
            return create_update_auto_selection_policies_payload_for_post(contact_type, atr_id, atr_property_id)[
                "payload"]
        else:
            return data["auto_selection_policies"]

    @allure.title("Get Sampling location Assessment attribute Details")
    @allure.description("This test case tests API to get details of Sampling location Assessment attribute")
    @allure.link("https://app.clickup.com/t/85zrg88xw")
    @pytest.mark.get_assessment_attribute
    def test_get_assessment_attribute(self):
        url = const.ATTRIBUTE
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Add New Sampling location Assessment attribute Details")
    @allure.description("This test case tests API to add new Sampling location Assessment attribute")
    @allure.link("https://app.clickup.com/t/85zrg7ww2")
    @pytest.mark.update_assessment_attribute
    def test_update_assessment_attribute(self, data=None):
        global ASSESSMENT_ATTRIBUTE_ID
        assess_atr = self.test_get_assessment_attribute()["response"]
        assess_atr = json.loads(assess_atr)
        ASSESSMENT_ATTRIBUTE_ID = assess_atr["result"]
        payload = self.get_assessment_attribute_payload(data)
        if payload is not None:
            url = const.ATTRIBUTE
            response = Request.post(url, data=payload, use_facility_url=True)
            status_200(response)
            return {"response": response.text}

    @allure.title("Delete the auto selection policy")
    @allure.description("This method is used to delete the auto selection policy")
    @allure.link("https://app.clickup.com/t/85zrjm4vj")
    @pytest.mark.delete_auto_selection_policy
    def test_delete_auto_selection_policy(self):
        global SAMPLING_SELECTION
        auto_selection_policy = self.test_get_auto_selection_policies()["response"]
        auto_selection_policy = json.loads(auto_selection_policy)
        SAMPLING_SELECTION = auto_selection_policy["result"]
        sampling_id = self.get_sampling_id()
        payload = archive_payload()
        for i in range(len(sampling_id)):
            url = const.SAMPLING_POLICY + str(sampling_id[i])
            response = Request.delete(url, data=payload, use_facility_url=True)
            status_200(response)

    @allure.title("Archive the assessment attribute")
    @allure.description("This method is used to archive the assessment attribute in sampling location assessment")
    @allure.link("https://app.clickup.com/t/85zrjm4y7")
    @pytest.mark.archive_assessment_attribute
    def test_archive_assessment_attribute(self):
        global ASSESSMENT_ATTRIBUTE_ID
        assess_atr = self.test_get_assessment_attribute()["response"]
        assess_atr = json.loads(assess_atr)
        ASSESSMENT_ATTRIBUTE_ID = assess_atr["result"]
        attribute_id = self.get_attribute_id()
        payload = archive_payload()
        if attribute_id is not None:
            url = const.ATTRIBUTE + str(attribute_id)
            response = Request.delete(url, data=payload, use_facility_url=True)
            status_200(response)
            return {"response": response.text}

    @allure.title("Unarchive the assessment attribute")
    @allure.description("This method is used to unarchive the the assessment attribute in sampling location assessment")
    @allure.link("https://app.clickup.com/t/85zrjm51f")
    @pytest.mark.unarchive_assessment_attribute
    def test_unarchive_assessment_attribute(self):
        global ASSESSMENT_ATTRIBUTE_ID
        assess_atr = self.test_get_assessment_attribute()["response"]
        assess_atr = json.loads(assess_atr)
        ASSESSMENT_ATTRIBUTE_ID = assess_atr["result"]
        attribute_id = self.get_attribute_id()
        payload = unarchive_payload()
        if attribute_id is not None:
            url = const.ATTRIBUTE + str(attribute_id) + const.UNARCHIVE
            response = Request.put(url, data=payload, use_facility_url=True)
            status_200(response)
            return {"response": response.text}

    @allure.title("Get Sampling location Assessment auto-selection policies Details")
    @allure.description("This test case tests API to get details of Sampling location Assessment auto-selection "
                        "policies")
    @allure.link("https://app.clickup.com/t/85zrg8fjq")
    @pytest.mark.get_auto_selection_policies
    def test_get_auto_selection_policies(self):
        url = const.SAMPLING_POLICY
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Add New Sampling location Assessment auto-selection policies Details")
    @allure.description("This test case tests API to add new Sampling location Assessment auto-selection policies")
    @allure.link("https://app.clickup.com/t/85zrg8fqg")
    @pytest.mark.update_auto_selection_policies
    def test_update_auto_selection_policies(self, data=None):
        global ATTRIBUTE_ID, ATTRIBUTE_PROPERTY_ID, SAMPLING_SELECTION
        attribute_id = self.test_get_assessment_attribute()["response"]
        attribute_id = json.loads(attribute_id)
        auto_selection_policy = self.test_get_auto_selection_policies()["response"]
        auto_selection_policy = json.loads(auto_selection_policy)
        SAMPLING_SELECTION = auto_selection_policy["result"]
        sampling_id = self.get_sampling_id()
        if len(sampling_id) == 0:
            ATTRIBUTE_ID = attribute_id["result"][0]["id"]
            ATTRIBUTE_PROPERTY_ID = attribute_id["result"][0]["properties"][0]["id"]
            payload = self.get_auto_selection_policies_payload(data, contact_type="Direct")
            url = const.SAMPLING_POLICY
            response = Request.post(url, data=payload, use_facility_url=True)
            status_200(response)
            payload = self.get_auto_selection_policies_payload(data, contact_type="Indirect")
            url = const.SAMPLING_POLICY
            response = Request.post(url, data=payload, use_facility_url=True)
            status_200(response)
