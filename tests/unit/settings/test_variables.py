import allure
import pytest
import json
import sys
from random import *
from payload.facility.update_variable_payload import create_update_variable_payload
from util.api_requests import Request
from util import constants as const
from util.validate_response import *
from test_data.data import unit_test_data as unit_data
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.variables
class TestVariables:

    @staticmethod
    def get_variable_unit_id(data):
        variables_id = 0
        if data is None:
            for i in VARIABLE_DATA:
                if i["shortName"] == unit_data.VARIABLES["name"]:
                    variables_id = i["id"]
        else:
            for i in VARIABLE_DATA:
                if i["shortName"] == data["variables_name"]:
                    variables_id = i["id"]
        return variables_id

    @staticmethod
    def get_variable_payload(data):
        if data is None:
            variable_value = randint(1, 100)
            return create_update_variable_payload(VARIABLE_DATA, variable_value)
        else:
            variable_value = data["variable_value"]
            if VARIABLE_DATA["defaultValue"] != variable_value:
                return create_update_variable_payload(VARIABLE_DATA, variable_value)
            else:
                return None

    @allure.title("Get All Variable")
    @allure.description("This test case gets details of all Variables in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2yxb")
    @pytest.mark.get_variables
    def test_get_variables(self):
        response = Request.get(const.VARIABLES, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Get One Variable")
    @allure.description("This test case gets detail of One Variable in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2yxe")
    @pytest.mark.get_variable
    def test_get_variable(self, data=None):
        variables = self.test_get_variables()["response"]
        variables = json.loads(variables)
        global VARIABLE_DATA
        VARIABLE_DATA = variables["variables"]
        variables_id = self.get_variable_unit_id(data)
        url = const.VARIABLES + str(variables_id)
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Update One Variable")
    @allure.description("This test case updates details of One Variable in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2yxh")
    @pytest.mark.update_variable_value
    def test_update_variable_value(self, data=None):
        global VARIABLE_DATA
        variable = self.test_get_variable(data)["response"]
        variable = json.loads(variable)
        VARIABLE_DATA = variable["variables"]
        variable_id = VARIABLE_DATA["id"]
        payload = self.get_variable_payload(data)

        if payload is not None:
            url = const.VARIABLES + str(variable_id)
            response = Request.post(url, data=payload, use_facility_url=True)
            status_200(response)
            return {"response": response.text}
