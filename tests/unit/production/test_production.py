import allure
import pytest
import json
import sys
from util.api_requests import Request
from util import constants as const
from util.validate_response import *
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.production
class TestProduction:

    @staticmethod
    def get_production_page_number(data):
        if data is None:
            page_number = "1"
        else:
            if "page_number" in data:
                page_number = data["page_number"]
            else:
                page_number = "1"
        return page_number

    @staticmethod
    def get_production_id(data):
        if data is None:
            production_id = PRODUCTIONS["productions"][0]["production_id"]
        else:
            production_id = data["production"]
        return production_id

    def find_production_data(self, total_page, production_id):
        data = {}
        global PRODUCTIONS
        for j in range(2, total_page + 2):
            for i in range(len(PRODUCTIONS["productions"])):
                if PRODUCTIONS["productions"][i]["production_id"] == production_id:
                    return PRODUCTIONS["productions"][i]
            else:
                data.update({"page_number": str(j)})
                response = self.test_get_productions(data)["response"]
                PRODUCTIONS = json.loads(response)

    @allure.title("Get All Productions")
    @allure.description("This test case gets details of all Productions present in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2vy8")
    @pytest.mark.get_productions
    def test_get_productions(self, data=None):
        page_number = self.get_production_page_number(data)
        url = const.PRODUCTIONS + page_number + const.PAGE_LIMIT_10
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    @allure.title("Get ID on any one Productions")
    @allure.description("This test case get ID of any one Production by ProductionID in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2w08")
    @pytest.mark.get_production
    def test_get_production(self, data=None):
        global PRODUCTIONS
        PRODUCTIONS = self.test_get_productions(None)["response"]
        PRODUCTIONS = json.loads(PRODUCTIONS)
        total_record = PRODUCTIONS["totalRecords"]
        total_page = round((total_record + 5) / 10)
        production_id = self.get_production_id(data)
        production_data = self.find_production_data(total_page, production_id)
        production_internal_id = (production_data["id"])
        url = const.PRODUCTION + str(production_internal_id)
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return {"response": response.text}

    # This method returns the lowest SAL on a Production
    def get_production_lowest_sal(self, data):
        global PRODUCTIONS
        PRODUCTIONS = self.test_get_productions(None)["response"]
        PRODUCTIONS = json.loads(PRODUCTIONS)
        total_record = PRODUCTIONS["totalRecords"]
        total_page = round((total_record + 5) / 10)
        sal = "#N/A"
        production_id = data["production"]
        production_data = self.find_production_data(total_page, production_id)
        if "sal" in production_data:
            sal = production_data["sal"]["value"]
        return sal

    # This method return the sal of each equipment
    def get_production_sal_each_equipment(self, data):
        production_details = self.test_get_production(data)["response"]
        production_details = json.loads(production_details)
        equipment_details = production_details["productions"]["equipmentDetails"]
        sal = {}
        for i in range(len(equipment_details)):
            equipment = equipment_details[i]["externalId"]
            if 'sal' in equipment_details[i]:
                limit = equipment_details[i]["sal"]["value"]
            else:
                limit = "#N/A"
            sal.update({equipment: limit})
        return sal
