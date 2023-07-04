import allure
import pytest
import json
import sys
from util.api_requests import Request
from util import constants as const
from util.validate_response import *
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.equipments
class TestEquipment:

    @staticmethod
    def get_page_number(data):
        if data is None:
            return "1"
        return data["page_number"]

    @staticmethod
    def get_equipment_external_id(data):
        if data is None:
            return EQUIPMENTS["equipments"][0]["externalId"]
        return data["equipment"]

    # To find data of one Equipment from data of all the Equipments
    def find_equipment_data(self, total_page, equipment_id):
        data = {}
        equipments = self.test_get_equipments(None)
        equipments = json.loads(equipments)
        for j in range(2, total_page + 2):
            for i in range(len(equipments["equipments"])):
                if equipments["equipments"][i]["externalId"] == equipment_id:
                    return equipments["equipments"][i]
            else:
                data.update({"page_number": str(j)})
                equipments = self.test_get_equipments(data)
                equipments = json.loads(equipments)

    @allure.title("Get All Equipments")
    @allure.description("This test case gets details of all Equipments present in a Facility page wise")
    @allure.link("https://app.clickup.com/t/2uw2udn")
    @pytest.mark.get_equipments
    def test_get_equipments(self, data=None):
        page_number = self.get_page_number(data)
        url = const.EQUIPMENTS + page_number + const.PAGE_LIMIT_10
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return response.text

    @allure.title("Get Equipment Data")
    @allure.description("This test case get Equipment Data when ExternalID in a Facility")
    @allure.link("https://app.clickup.com/t/2uw2uf0")
    @pytest.mark.get_equipment
    def test_get_equipment(self, data=None):
        global EQUIPMENTS
        EQUIPMENTS = self.test_get_equipments(None)
        EQUIPMENTS = json.loads(EQUIPMENTS)
        total_record = EQUIPMENTS["totalRecords"]
        total_page = round((int(total_record) + 5) / 10)
        equipment_external_id = self.get_equipment_external_id(data)
        equipment = self.find_equipment_data(total_page, equipment_external_id)
        if equipment is None:
            pytest.fail(equipment_external_id + " Not Found")
        equipment_id = (equipment["id"])
        url = const.EQUIPMENT + str(equipment_id)
        response = Request.get(url, use_facility_url=True)
        status_200(response)
        return response.text

    # This method returns the lowest SAL on an Equipment
    def get_equipment_lowest_sal(self, data):
        global EQUIPMENTS
        EQUIPMENTS = self.test_get_equipments(None)
        EQUIPMENTS = json.loads(EQUIPMENTS)
        total_record = EQUIPMENTS["totalRecords"]
        total_page = round((int(total_record) + 5) / 10)
        equipment_external_id = self.get_equipment_external_id(data)
        equipment = self.find_equipment_data(total_page, equipment_external_id)
        if equipment is None:
            pytest.fail(equipment_external_id + " Not Found")
        sal = "#N/A"
        if "sal" in equipment:
            sal = equipment["sal"]["value"]
        return sal

    # This method returns the production and sal on an Equipment
    def get_production_sal_each_equipment(self, data):
        equipment_details = self.test_get_equipment(data)
        equipment_details = json.loads(equipment_details)
        production_details = equipment_details["equipments"]["productions"]
        sal = {}
        for i in range(len(production_details)):
            production = production_details[i]["externalId"]
            if 'sal' in production_details[i]:
                limit = production_details[i]["sal"]["value"]
            else:
                limit = "#N/A"
            sal.update({production: limit})
        return sal
