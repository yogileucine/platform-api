from util.api_requests import Request
from util import constants as const
from util.validate_response import *
from test_data.data import unit_test_data as unit_data
from payload.facility.update_default_unit_payload import create_update_default_unit_payload
import allure
import pytest
import json
import sys
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.default_units
class TestDefaultUnits:

    @staticmethod
    def get_default_unit_id(data):
        unit_id = 0
        if data is None:
            for i in DEFAULT_UNITS_DATA:
                if i["shortName"] == unit_data.DEFAULT_UNIT["name"]:
                    unit_id = i["id"]
        else:
            for i in DEFAULT_UNITS_DATA:
                if i["shortName"] == data["default_unit_name"]:
                    unit_id = i["id"]
        return unit_id

    @staticmethod
    def get_default_unit_payload(data):
        if data is None:
            if DEFAULT_UNIT_DATA["unit"] == unit_data.DEFAULT_UNIT["unit1"]:
                unit = unit_data.DEFAULT_UNIT["unit2"]
            else:
                unit = unit_data.DEFAULT_UNIT["unit1"]
            return create_update_default_unit_payload(DEFAULT_UNIT_DATA, unit)
        else:
            unit = data["default_unit"]
            if DEFAULT_UNIT_DATA["unit"] != unit:
                return create_update_default_unit_payload(DEFAULT_UNIT_DATA, unit)
            else:
                return None

    @allure.title("Get All Default Unit")
    @allure.description("This test case gets details of all Default unit in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2qja")
    @pytest.mark.get_default_units
    def test_get_default_units(self):
        response = Request.get(const.DEFAULT_UNITS, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    # TO DO - Find way to not pass data as none because reading this method means to get details of particular entity,
    # but it returns details of fixed data when data is None
    @allure.title("Get One Default Unit")
    @allure.description("This test case gets detail of One Default unit in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2qm3")
    @pytest.mark.get_default_unit
    def test_get_default_unit(self, data=None):
        defaults_units = self.test_get_default_units()["response"]
        defaults_units = json.loads(defaults_units)
        global DEFAULT_UNITS_DATA
        DEFAULT_UNITS_DATA = defaults_units["default_units"]
        unit_id = self.get_default_unit_id(data)
        url = const.DEFAULT_UNITS + str(unit_id)
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Update One Default Unit")
    @allure.description("This test case updates details of One Default unit in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2qmv")
    @pytest.mark.update_default_unit
    def test_update_default_unit(self, data=None):
        global DEFAULT_UNIT_DATA
        defaults_unit = self.test_get_default_unit(data)["response"]
        defaults_unit = json.loads(defaults_unit)
        DEFAULT_UNIT_DATA = defaults_unit["default_units"]
        unit_id = DEFAULT_UNIT_DATA["id"]
        payload = self.get_default_unit_payload(data)
        if payload is not None:
            url = const.DEFAULT_UNITS + str(unit_id)
            response = Request.post(url, data=payload, use_facility_url=True)
            status_200(response)
            return {"response": response.text}
