import allure
import pytest
import json
import sys
from util.api_requests import Request
from util import constants as const
from util.validate_response import *
from util.env_property import Env
from unit.login_logout import test_login_logout
from unit.settings.cleaning_limit_policies import test_active_cleaning_limit_policy
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.cleaning_assessment
class TestCleaningAssessment:
    login_logout = test_login_logout.TestLoginLogout()
    active_policy = test_active_cleaning_limit_policy.TestActiveCleaningLimitPolicy()

    def perform_changes(self, scenario):
        if scenario is False:
            self.active_policy.test_update_active_policy(None)

    @allure.title("Start Cleaning Assessment")
    @allure.description("This test case tests API to start cleaning assessment")
    @allure.link("https://app.clickup.com/t/2k600q4")
    @pytest.mark.start_cleaning_assessment
    def test_start_cleaning_assessment(self, scenario=False):
        self.perform_changes(scenario)
        payload = {"title": "CE1", "reason": "Some reason"}
        response = Request.post(const.CLEANING_ASSESSMENT, payload, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Get All Cleaning Assessment")
    @allure.description("This test case tests API to get details of all cleaning assessment")
    @allure.link("https://app.clickup.com/t/2k600rn")
    @pytest.mark.get_cleaning_assessment
    def test_get_cleaning_assessment(self):
        response = Request.get(const.CLEANING_ASSESSMENT, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Get Qualification Task")
    @allure.description("This test case tests API to get details of qualification task")
    @allure.link("https://app.clickup.com/t/2k600ub")
    @pytest.mark.get_qualification_task
    def test_get_qualification_task(self):
        response = self.test_get_cleaning_assessment()["response"]
        cleaning_assessment = json.loads(response)
        cleaning_assessment_id = str(cleaning_assessment["cleaningEvaluation"][0]["id"])
        response = Request.get(const.QUALIFICATION_TASK_EVALUATION + cleaning_assessment_id, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Approve Cleaning Assessment")
    @allure.description("This test case tests API to submit, review and approved cleaning assessment")
    @allure.link("https://app.clickup.com/t/2k600vp")
    @pytest.mark.submit_approve_cleaning_assessment
    def test_submit_approve_cleaning_assessment(self):
        response = self.test_get_qualification_task()["response"]
        cleaning_assessment = json.loads(response)
        lwcr_id = str(cleaning_assessment["qualification_tasks"]["facilityTasks"][1]["id"])
        car_id = str(cleaning_assessment["qualification_tasks"]["facilityTasks"][0]["id"])
        payload = {"input": {"password": Env.get_env_data("ADMIN_PASSWORD"), "meaningOfSignature": "Submit"},
                   "reason": ""}
        lwcr_submit = Request.post(const.QUALIFICATION_TASK + lwcr_id, payload, use_facility_url=True)
        status_200(lwcr_submit)
        car_submit = Request.post(const.QUALIFICATION_TASK + car_id, payload, use_facility_url=True)
        status_200(car_submit)
        self.login_logout.test_logout()

        login_data = {"username": Env.get_env_data("QA_USERNAME"), "password": Env.get_env_data("QA_PASSWORD")}
        self.login_logout.test_login_user_id(login_data)
        payload = {"input": {"password": Env.get_env_data("QA_PASSWORD"), "meaningOfSignature": "Review"}, "reason": ""}
        lwcr_submit = Request.post(const.QUALIFICATION_TASK + lwcr_id, payload, use_facility_url=True)
        status_200(lwcr_submit)
        car_submit = Request.post(const.QUALIFICATION_TASK + car_id, payload, use_facility_url=True)
        status_200(car_submit)

        payload = {"input": {"password": Env.get_env_data("QA_PASSWORD"), "meaningOfSignature": "Approve"},
                   "reason": ""}
        lwcr_submit = Request.post(const.QUALIFICATION_TASK + lwcr_id, payload, use_facility_url=True)
        status_200(lwcr_submit)
        car_submit = Request.post(const.QUALIFICATION_TASK + car_id, payload, use_facility_url=True)
        status_200(car_submit)
        self.login_logout.test_logout()

        self.login_logout.test_login_user_id(None)
