import allure
import pytest
import requests
import json
import os
import sys

sys.path.append(".")
import unit.settings.test_selection_criteria as selection_criteria
import unit.settings.cleaning_limit_policies.test_additional_cleaning_criteria as additional_cleaning_criteria
import unit.change_assessment.test_cleaning_assessment as cleaning_assessment
import unit.migrate_data.test_file_import as file_import
import unit.settings.test_default_unit as default_unit
from util.schema_validator import assert_valid_schema
from dotenv import load_dotenv, find_dotenv
from payload.on_demand_protocol.update_additional_test_payload import create_additional_test_payload
from payload.on_demand_protocol.update_active_payload import *
from payload.on_demand_protocol.update_equipment_entities_payload import *
from payload.on_demand_protocol.update_intermediate_payload import (
    create_update_intermediate_payload,
)
from payload.on_demand_protocol.update_cleaning_agent_payload import *
import unit.production.test_production as production
import conftest as conf

load_dotenv(find_dotenv())

context = None


@allure.title("On Demand Protocol")
@allure.description("These test cases test API of on demand protocol")
@pytest.mark.v40x
@pytest.mark.skip
@pytest.mark.on_demand_protocol
@pytest.mark.usefixtures("login")
class TestOnDemandProtocol:


    @allure.title("Create On Demand Protocol")
    @allure.description("This test case tests API to create a new on demand protocol")
    @allure.link("https://app.clickup.com/t/27hztya")
    @pytest.fixture(scope="session", autouse=True)
    def test_create_protocol(self, login):
        url = login["formualtion_facility_url"] + os.environ.get("ON_DEMAND_PROTOCOL")
        criteria_selection = selection_criteria.Test_Selection_Criteria()
        additional_cleaning = additional_cleaning_criteria.Test_Additional_Cleaning_Criteria()
        change_assessment = cleaning_assessment.Test_Cleaning_Assessment()
        master_data_import = file_import.Test_File_Import()
        get_production = production.Test_Production()
        data = {"url": login["formualtion_facility_url"], "cookies": login["cookies"],
                "facility_type": login["facility_type"], "production": "Pr2"}
        criteria_selection.test_update_selection_criteria(login, data)
        additional_cleaning.test_update_additional_cleaning_criteria(login, data)
        master_data_import.test_import_master_data(login, data)
        change_assessment.test_start_cleaning_assessment(login, data)
        change_assessment.test_submit_approve_cleaning_assessment(login, data)
        production_id = get_production.test_get_production_id(login, data)

        payload = {
            "protocolType": "validation",
            "name": "p",
            "productionId": production_id,
            "reason": "r",
            "externalId": "p",
            "authorId": 3,
            "description": None,
        }
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
        }
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=json.dumps(payload),
            cookies=login["cookies"],
        )
        with open("./tests/response/on_demand_protocol/create_protocol.json", "w") as f:
            f.write(response.text)
        assert response.status_code == 200
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/create_protocol_schema.json",
        )
        ids = json.loads(response.text)
        ids = ids["result"]["onDemandVerificationId"]
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
        }
        assert (result, True), "Assertion Failed"

        return {
            "login": login,
            "response": response,
            "ids": ids,
            "headers": headers,
            "url": url
        }

    @allure.title("Update Description of an On Demand Protocol")
    @allure.description("This test case tes API to update description of an on demand protocol")
    @allure.link("https://app.clickup.com/t/28zzrnb")
    @pytest.mark.update_protocol_description
    def test_update_protocol_description(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = test_create_protocol["url"] + str(id1)
        payload = {"description": "testing description"}
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        with open(
                "./tests/response/on_demand_protocol/update_protocol_description.json", "w"
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_protocol_description_schema.json",
        )
        assert (result, True), "Assertion Failed"
        assert response.status_code == 200

    @allure.title("Get Equipment Entities of an On Demand Protocol")
    @allure.description("This test case test API get all equipment entities of an on demand protocol")
    @allure.link("https://app.clickup.com/t/27j0u9j")
    @pytest.mark.get_protocol_equipment_entities
    def test_get_protocol_equipment_entities(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        ids = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(ids)
                + "/equipment"
        )
        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )

        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_protocol_equipment_entities.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_protocol_equipment_entities_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Update Equipment Entities of an On Demand Protocol")
    @allure.description("This test case test API for updating equipment entities of an on demand protocol")
    @allure.link("https://app.clickup.com/t/27j0vaz")
    @pytest.mark.update_protocol_equipment_entities
    def test_update_equipment_entities(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        equipment_entities = self.test_get_protocol_equipment_entities(test_create_protocol)["response"]
        payload = create_update_equipment_entities_payload(json.loads(equipment_entities))["payload"]
        ids = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(ids)
                + "/equipment"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        with open(
                "./tests/response/on_demand_protocol/update_equipment_entities.json",
                "w",
        ) as f:
            f.write(response.text)
        assert response.status_code == 200
        js = json.loads(response.text)
        if js["result"] is None:
            assert True
        else:
            assert False, "Response is not null"

    @allure.title("Deselecting All Equipment Entities in an On Demand Protocol")
    @allure.description(
        "This test case test API error response when all equipment entities are deselected in an on demand protocol")
    @allure.link("https://app.clickup.com/t/29wdf26")
    @pytest.mark.deselect_all_protocol_equipment_entities
    def test_deselect_all_protocol_equipment_entities(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        ids = test_create_protocol["ids"]
        equipment_entities = self.test_get_protocol_equipment_entities(test_create_protocol)["response"]
        payload = create_diselect_all_protocol_equipment_entites_payload(json.loads(equipment_entities))["payload"]
        url = (
                test_create_protocol["url"]
                + str(ids)
                + "/equipment"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        assert response.status_code == 400
        with open(
                "./tests/response/on_demand_protocol/deselect_all_protocol_equipment_entities.json", "w"
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/deselect_all_protocol_equipment_entities_schema.json")
        assert (result, True), "Assertion Failed"

    @allure.title("Empty cleaning procedure id")
    @allure.description("This test case test API error response when CP_ID is not passed in an on demand protocol")
    @allure.link("https://app.clickup.com/t/28zruu7")
    @pytest.mark.empty_cleaning_procedure_id
    def test_empty_cleaning_procedure_id(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        ids = test_create_protocol["ids"]
        equipment_entities = self.test_get_protocol_equipment_entities(test_create_protocol)["response"]
        js = json.loads(equipment_entities)

        id = js["result"][0]["equipment"]["id"]
        url = (
                test_create_protocol["url"]
                + str(ids)
                + "/equipment"
        )
        payload = {
            "disableIds": [],
            "enableIds": [id],
            "eqDetails": {str(id): {"cpId": ""}},
        }
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        assert response.status_code == 400
        with open(
                "./tests/response/on_demand_protocol/empty_cleaning_procedure_id.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/deselect_all_protocol_equipment_entities_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Production SAL of Direct Active Residue Verification")
    @allure.description(
        "This test case test API to get Production SAL of Direct Active Residue Verification in an on demand protocol")
    @allure.link("https://app.clickup.com/t/27j0wvy")
    @pytest.mark.get_active_direct_production_sal
    @pytest.mark.smoke
    def test_get_active_direct_production_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives/productWise/Direct"
        )
        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200

        with open(
                "./tests/response/on_demand_protocol/active_direct_production_sal.json", "w"
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/active_direct_production_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Production Group SAL of Direct Active Residue Verification")
    @allure.description(
        "This test case test API to get Production Group SAL of Direct Active Residue Verification in an on demand protocol")
    @allure.link("https://app.clickup.com/t/28zrt50")
    @pytest.mark.smoke
    @pytest.mark.get_active_direct_production_group_sal
    def test_get_active_direct_production_group_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives/equipmentWise/Direct"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/active_direct_production_group_sal.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/active_direct_production_group_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Custom SAL of Direct Active Residue Verification")
    @allure.description(
        "This test case test API to get Custom SAL of Direct Active Residue Verification in an on demand protocol")
    @allure.link("https://app.clickup.com/t/28zruxh")
    @pytest.mark.smoke
    @pytest.mark.get_active_direct_custom_sal
    def test_get_active_direct_custom_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives/custom/Direct"
        )
        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/active_direct_custom_sal.json", "w"
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/active_direct_custom_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Custom SAL of Indirect Active Residue Verification")
    @allure.description(
        "This test case test API to get Custom SAL of Indirect Active Residue Verification in an on demand protocol")
    @allure.link("https://app.clickup.com/t/28zrxb4")
    @pytest.mark.get_active_indirect_custom_sal
    def test_get_active_indirect_custom_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives/custom/Indirect"
        )
        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )

        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/active_indirect_custom_sal.json", "w"
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/active_indirect_custom_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Based on Policy SAL of Indirect Active Residue Verification")
    @allure.description("This test case test API to get Based On Policy SAL of Indirect Active Residue Verification "
                        "in an on demand protocol")
    @allure.link("https://app.clickup.com/t/28zrxep")
    @pytest.mark.get_active_indirect_based_on_policy_sal
    def test_get_active_indirect_based_on_policy_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives/policyBased/Indirect"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/active_indirect_based_on_policy_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/active_indirect_based_on_policy_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Update and save Policy for Active Residue Verification")
    @allure.description(
        "This test case test API to Update and save Policy for Active Residue Verification in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2a7yh7r")
    @pytest.mark.smoke
    @pytest.mark.active_update_limit
    def test_active_update_limit(self, test_create_protocol):
        active_direct = self.test_get_active_direct_production_sal(test_create_protocol)["response"]
        active_indirect = self.test_get_active_indirect_based_on_policy_sal(test_create_protocol)["response"]
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]
        payload = create_update_active_payload(json.loads(active_direct), json.loads(active_indirect))["payload"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )

        with open(
                "./tests/response/on_demand_protocol/active_update_limit.json", "w"
        ) as f:
            f.write(response.text)
        assert response.status_code == 200

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/active_update_limit_schema.json",
        )

        assert (result, True), "Assertion Failed"

    @allure.title("Get Error when empty custom limits passed for Direct Active Residue Verification")
    @allure.description(
        "This test case test API to to give error when empty custom limit is saved for direct Active Residue "
        "Verification in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2at5237")
    @pytest.mark.active_direct_update_empty_limit
    def test_active_direct_update_empty_limit(self, test_create_protocol):
        active_direct_custom = self.test_get_active_direct_custom_sal(test_create_protocol)["response"]
        active_indirect_based_on_policy = self.test_get_active_indirect_based_on_policy_sal(test_create_protocol)[
            "response"]
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]
        payload = create_active_direct_update_empty_limit_payload(json.loads(active_direct_custom),
                                                                  json.loads(active_indirect_based_on_policy))[
            "payload"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        with open(
                "./tests/response/on_demand_protocol/active_direct_update_empty_limit.json", "w"
        ) as f:
            f.write(response.text)
        assert response.status_code == 400
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/active_update_empty_limit_schema.json",
        )

        assert (result, True), "Assertion Failed"

    @allure.title("Get Error when empty custom limits passed for Indirect Active Residue Verification")
    @allure.description(
        "This test case test API to to give error when empty custom limit is saved for Indirect Active Residue "
        "Verification in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2cja8ju")
    @pytest.mark.active_indirect_update_empty_limit
    def test_active_indirect_update_empty_limit(self, test_create_protocol):
        active_direct_product_wise = self.test_get_active_direct_production_sal(test_create_protocol)["response"]
        active_indirect_custom = self.test_get_active_indirect_custom_sal(test_create_protocol)["response"]
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]
        payload = create_active_indirect_update_empty_limit_payload(json.loads(active_direct_product_wise),
                                                                    json.loads(active_indirect_custom))["payload"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        with open(
                "./tests/response/on_demand_protocol/active_indirect_update_empty_limit.json", "w"
        ) as f:
            f.write(response.text)
        assert response.status_code == 400

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/active_update_empty_limit_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("No Policy selected for Indirect Active Residue Verification")
    @allure.description(
        "This test case test API to update and save Active Residue Verification when no policy for Indirect is "
        "selected in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2cja9d9")
    @pytest.mark.active_update_only_direct_limit
    def test_active_update_only_direct_limit(self, test_create_protocol):
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]

        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/actives"
        )

        active_direct_product_wise = self.test_get_active_direct_production_sal(test_create_protocol)["response"]
        active_indirect_custom = self.test_get_active_indirect_custom_sal(test_create_protocol)["response"]
        payload = create_active_update_only_direct_limit_payload(json.loads(active_direct_product_wise),
                                                                 json.loads(active_indirect_custom))["payload"]

        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        assert response.status_code == 200

        with open(
                "./tests/response/on_demand_protocol/active_update_only_direct_limit.json", "w"
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/active_update_only_direct_limit_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Get Based on Policy Rule and Acceptable value for PH")
    @allure.description(
        "This test case test API get rule and acceptable based on polciy for PH in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2cr5h4h")
    @pytest.mark.additional_test
    @pytest.mark.get_ph_based_on_policy
    def test_get_ph_based_on_policy(self, test_create_protocol):
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/pH/policyBased"
        )
        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_ph_based_on_policy.json", "w"
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_ph_based_on_policy_schema.json",
            )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Custom Rule and Acceptable value for PH")
    @allure.description(
        "This test case test API get rule and acceptable custom for PH in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2cr5hcu")
    @pytest.mark.additional_test
    @pytest.mark.get_ph_custom
    def test_get_ph_custom(self, test_create_protocol):
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/pH/custom"
        )
        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_ph_custom.json", "w"
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_ph_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Update Empty Acceptable value for PH")
    @allure.description(
        "This test case test API to give error when empty acceptable value is updated for PH in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2cr5ktb")
    @pytest.mark.additional_test
    @pytest.mark.ph_update_empty_custom
    def test_ph_update_empty_custom(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        ph_custom = self.test_get_ph_custom(test_create_protocol)["response"]
        response_json = json.loads(ph_custom)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(ph_custom, "custom")["payload"]
            url = (
                    test_create_protocol["url"]
                    + str(id1)
                    + "/inspection/"
                    + str(id1)
                    + "/additional/pH"
            )
            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            assert response.status_code == 400
            with open(
                    "./tests/response/on_demand_protocol/ph_update_empty_custom.json",
                    "w",
            ) as f:
                f.write(response.text)
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/ph_update_empty_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Update Rule and Acceptable value for PH")
    @allure.description(
        "This test case test API to update rule and acceptable value for PH in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82urz")
    @pytest.mark.additional_test
    @pytest.mark.ph_update_based_on_policy
    def test_ph_update_based_on_policy(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]

        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/pH"
        )
        ph_based_on_policy = self.test_get_ph_based_on_policy(test_create_protocol)["response"]
        response_json = json.loads(ph_based_on_policy)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(ph_based_on_policy, "policyBased")["payload"]

            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            assert response.status_code == 200
            with open(
                    "./tests/response/on_demand_protocol/ph_update_based_on_policy.json",
                    "w",
            ) as f:
                f.write(response.text)
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/ph_update_based_on_policy_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Create On demand Protocol with Production type Intermediate")
    @allure.description(
        "This test case test API to create a new on demand protocol with Production type Intermediate")
    @allure.link("https://app.clickup.com/t/2e5txhj")
    @pytest.fixture(scope="session", autouse=True)
    def test_create_protocol_intermediate(self, login):
        url = login["api_facility_url"] + os.environ.get("ON_DEMAND_PROTOCOL")
        additional_cleaning = additional_cleaning_criteria.Test_Additional_Cleaning_Criteria()
        change_assessment = cleaning_assessment.Test_Cleaning_Assessment()
        master_data_import = file_import.Test_File_Import()
        get_production = production.Test_Production()
        data = {"url": login["api_facility_url"], "cookies": login["cookies"],
                "facility_type": "api", "production": "PRD-Pd2/2/Erythromycin"}
        # additional_cleaning.test_update_additional_cleaning_criteria(login, data)
        master_data_import.test_import_master_data(login, data)
        change_assessment.test_start_cleaning_assessment(login, data)
        change_assessment.test_submit_approve_cleaning_assessment(login, data)
        production_id = get_production.test_get_production_id(login, data)

        payload = {
            "protocolType": "validation",
            "name": "p",
            "productionId": production_id,
            "reason": "r",
            "externalId": "p",
            "authorId": 3,
            "description": None,
        }
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
        }
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=json.dumps(payload),
            cookies=login["cookies"],
        )
        with open(
                "./tests/response/on_demand_protocol/create_protocol_intermediate.json",
                "w",
        ) as f:
            f.write(response.text)
        assert response.status_code == 200
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/create_protocol_intermediate_schema.json",
        )
        ids = json.loads(response.text)
        ids = ids["result"]["onDemandVerificationId"]

        headers = {
            "Content-Type": "application/json;charset=UTF-8",
        }
        assert (result, True), "Assertion Failed"
        return {
            "login": login,
            "response": response,
            "ids": ids,
            "headers": headers,
            "url": url
        }

    @allure.title("Get Production Group SAL for Intermediate in On Demand Protocol")
    @allure.description(
        "This test case test API to get Production Group SAL for Intermediate in an On Demand Protocol")
    @allure.link("https://app.clickup.com/t/2cjag6v")
    @pytest.mark.smoke
    @pytest.mark.get_intermediate_production_group_sal
    def test_get_intermediate_production_group_sal(self, test_create_protocol_intermediate):
        cookies = test_create_protocol_intermediate["login"]["cookies"]
        id1 = test_create_protocol_intermediate["ids"]
        url = (
                test_create_protocol_intermediate["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/intermediates/equipmentWise/Direct"
        )
        response = requests.request(
            "GET", url, headers=test_create_protocol_intermediate["headers"], cookies=cookies
        )
        assert response.status_code == 200

        with open(
                "./tests/response/on_demand_protocol/intermediate_production_group_sal.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/intermediate_production_group_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Get Production SAL for Intermediate in On Demand Protocol")
    @allure.description(
        "This test case test API to get Production SAL for Intermediate in an On Demand Protocol")
    @allure.link("https://app.clickup.com/t/2cjag6w")
    @pytest.mark.smoke
    @pytest.mark.get_intermediate_production_sal
    def test_get_intermediate_production_sal(self, test_create_protocol_intermediate):
        cookies = test_create_protocol_intermediate["login"]["cookies"]
        id1 = test_create_protocol_intermediate["ids"]
        url = (
                test_create_protocol_intermediate["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/intermediates/productWise/Direct"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol_intermediate["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200

        with open(
                "./tests/response/on_demand_protocol/intermediate_production_sal.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/intermediate_production_sal_schema.json")
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Custom SAL for Intermediate in On Demand Protocol")
    @allure.description(
        "This test case test API to get custom SAL for Intermediate in an On Demand Protocol")
    @allure.link("https://app.clickup.com/t/2cjag6x")
    @pytest.mark.smoke
    @pytest.mark.get_intermediate_custom_sal
    def test_get_intermediate_custom_sal(self, test_create_protocol_intermediate):
        cookies = test_create_protocol_intermediate["login"]["cookies"]
        id1 = test_create_protocol_intermediate["ids"]
        url = (
                test_create_protocol_intermediate["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/intermediates/custom/Direct"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol_intermediate["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/intermediate_custom_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/intermediate_custom_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Save policy and SAL for Intermediate in On Demand Protocol")
    @allure.description(
        "This test case test API save policy and SAL for Intermediate in an On Demand Protocol")
    @allure.link("https://app.clickup.com/t/2cjag6y")
    @pytest.mark.smoke
    @pytest.mark.update_intermediate_limit
    def test_update_intermediate_limit(self, test_create_protocol_intermediate):
        cookies = test_create_protocol_intermediate["login"]["cookies"]
        id1 = test_create_protocol_intermediate["ids"]
        intermediate_production_sal_limit = \
            self.test_get_intermediate_production_sal(test_create_protocol_intermediate)["response"]
        url = (
                test_create_protocol_intermediate["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/intermediates"
        )
        payload = create_update_intermediate_payload(
            json.loads(intermediate_production_sal_limit), "productWise"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol_intermediate["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/update_intermediate_limit.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_intermediate_limit_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Save policy and blank SAL for Intermediate in On Demand Protocol")
    @allure.description(
        "This test case test API to give error when custom policy and blank SAL for Intermediate in an On Demand "
        "Protocol")
    @allure.link("https://app.clickup.com/t/2cjag72")
    @pytest.mark.update_intermediate_empty_limit
    def test_update_intermediate_empty_limit(self, test_create_protocol_intermediate):
        cookies = test_create_protocol_intermediate["login"]["cookies"]
        id1 = test_create_protocol_intermediate["ids"]
        intermediate_production_direct_custom = self.test_get_intermediate_custom_sal(
            test_create_protocol_intermediate
        )["response"]

        url = (
                test_create_protocol_intermediate["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/intermediates"
        )

        payload = create_update_intermediate_payload(
            json.loads(intermediate_production_direct_custom), "custom"
        )

        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol_intermediate["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        assert response.status_code == 400
        with open(
                "./tests/response/on_demand_protocol/update_intermediate_empty_limits.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_intermediate_empty_limits_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Get Cleaning Agent SAL in On Demand Protocol")
    @allure.description(
        "This test case test API to get cleaning agent sal in an On Demand Protocol")
    @allure.link("https://app.clickup.com/t/2cjaqyq")
    @pytest.mark.smoke
    @pytest.mark.get_cleaning_agent_direct_sal
    def test_get_cleaning_agent_direct_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca/cleaningAgentSal/Direct"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_cleaning_agent_direct_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_cleaning_agent_direct_sal_schema.json")
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Direct Cleaning Agent Custom SAL in an On Demand Protocol")
    @allure.description(
        "This test case tests API used to get blank SAL for Cleaning Agent Direct when Custom is selected in an on "
        "demand protocol "
    )
    @allure.link("https://app.clickup.com/t/2cjaqyx")
    @pytest.mark.smoke
    @pytest.mark.get_cleaning_agent_direct_custom_sal
    def test_get_cleaning_agent_direct_custom_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca/custom/Direct"
        )

        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )

        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_cleaning_agent_direct_custom_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_cleaning_agent_direct_custom_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"

        return {"response": response.text}

    @allure.title("Get Indirect Cleaning Agent SAL in On Demand Protocol")
    @allure.description(
        "This test case test API to get indirect cleaning agent sal in an On Demand Protocol")
    @allure.link("https://app.clickup.com/t/2cjaqz2")
    @pytest.mark.get_cleaning_agent_sal_indirect
    def test_get_cleaning_agent_sal_indirect(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca/policyBased/Indirect"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_cleaning_agent_sal_indirect.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_cleaning_agent_sal_indirect_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Blank SAL for  Cleaning Agent indirect Custom in an On Demand Protocol")
    @allure.description(
        "This test case tests API used to get custom SAL for cleaning agent indirect in an on demand protocol"
    )
    @allure.link("https://app.clickup.com/t/2cjaqz0")
    @pytest.mark.get_cleaning_agent_indirect_custom_sal
    def test_get_cleaning_agent_indirect_custom_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca/custom/Indirect"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )

        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_cleaning_agent_indirect_custom_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_cleaning_agent_indirect_custom_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"

        return {"response": response.text}

    @allure.title("Update and Save Limits for  Cleaning Agent Residue Verification in On Demand Protocol")
    @allure.description(
        "This test case tests API used to update and save sal of cleaning agent in an on demand protocol "
    )
    @allure.link("https://app.clickup.com/t/2cjaqz3")
    @pytest.mark.update_cleaning_agent_sal
    def test_update_cleaning_agent_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        cleaning_agent_direct_sal = self.test_get_cleaning_agent_direct_sal(test_create_protocol)["response"]
        cleaning_agent_indirect_sal = self.test_get_cleaning_agent_sal_indirect(test_create_protocol)["response"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca"
        )
        cleaning_agent_update_sal_payload = create_update_cleaning_agent_payload(json.loads(cleaning_agent_direct_sal),
                                                                                 json.loads(
                                                                                     cleaning_agent_indirect_sal))[
            "payload"]
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(cleaning_agent_update_sal_payload),
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/update_cleaning_agent_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_cleaning_agent_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Update Cleaning Agent Residue Verification without Indirect")
    @allure.description(
        "This test case tests API used to update Limits for  Cleaning Agent Residue Verification even when no policy "
        "is selected for Indirect Contact Surfaces "
    )
    @allure.link("https://app.clickup.com/t/2cjaqza")
    @pytest.mark.update_cleaning_agent_sal_only_direct
    def test_update_cleaning_agent_sal_only_direct(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        cleaning_agent_direct_sal = self.test_get_cleaning_agent_direct_sal(test_create_protocol)["response"]
        cleaning_agent_indirect_custom_sal = self.test_get_cleaning_agent_indirect_custom_sal(test_create_protocol)[
            "response"]
        update_cleaning_agent_payload = \
            create_update_cleaning_agent__direct_only_payload(json.loads(cleaning_agent_direct_sal),
                                                              json.loads(cleaning_agent_indirect_custom_sal))["payload"]

        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca"
        )

        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(update_cleaning_agent_payload),
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/update_cleaning_agent_sal_only_direct.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_cleaning_agent_sal_only_direct_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Update and Save Custom Policy for Direct Cleaning Agent with Blank Limit")
    @allure.description(
        "This test case tests APIto give error when empty custom limits are saved for direct cleaning agent in an on demand protocol"
    )
    @allure.link("https://app.clickup.com/t/2cjaqz5")
    @pytest.mark.update_cleaning_agent_direct_empty_custom_sal
    def test_update_cleaning_agent_direct_empty_custom_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        cleaning_agent_direct_custom = self.test_get_cleaning_agent_direct_custom_sal(test_create_protocol)["response"]
        cleaning_agent_indirect_policy_based = self.test_get_cleaning_agent_sal_indirect(test_create_protocol)[
            "response"]
        update_cleaning_agent_payload = \
            create_cleaning_agent_direct_update_empty_limit_payload(json.loads(cleaning_agent_direct_custom),
                                                                    json.loads(cleaning_agent_indirect_policy_based))[
                "payload"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(update_cleaning_agent_payload),
            cookies=cookies,
        )
        assert response.status_code == 400
        with open(
                "./tests/response/on_demand_protocol/update_cleaning_agent_direct_empty_custom_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_cleaning_agent_direct_empty_custom_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Update and Save Custom Policy for Indirect Cleaning Agent with Blank Limit")
    @allure.description(
        "This test case tests APIto give error when empty custom limits are saved for Indirect cleaning agent in an "
        "on demand protocol "
    )
    @allure.link("https://app.clickup.com/t/2cjaqz8")
    @pytest.mark.update_cleaning_agent_indirect_empty_custom_sal
    def test_update_cleaning_agent_indirect_empty_custom_sal(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        cleaning_agent_direct_policy_based = self.test_get_cleaning_agent_direct_sal(test_create_protocol)["response"]
        cleaning_agent_indirect_custom_sal = self.test_get_cleaning_agent_indirect_custom_sal(test_create_protocol)[
            "response"]
        update_cleaning_agent_payload = \
            create_cleaning_agent_indirect_update_empty_limit_payload(json.loads(cleaning_agent_direct_policy_based),
                                                                      json.loads(cleaning_agent_indirect_custom_sal))[
                "payload"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/ca"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(update_cleaning_agent_payload),
            cookies=cookies,
        )
        assert response.status_code == 400
        with open(
                "./tests/response/on_demand_protocol/update_cleaning_agent_indirect_empty_custom_sal.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_cleaning_agent_indirect_empty_custom_sal_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Update On Demand Protocol Name")
    @allure.description("This test case tests API used to update the protocol name ")
    @allure.link("https://app.clickup.com/t/28zztm9")
    @pytest.mark.update_protocol_name
    def test_update_protocol_name(self, test_create_protocol):
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]
        payload = {"name": "Name Change"}
        url = (
                test_create_protocol["url"]
                + str(id1)
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        with open(
                "./tests/response/on_demand_protocol/update_protocol_name.json", "w"
        ) as f:
            f.write(response.text)
        assert response.status_code == 200

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/update_protocol_name_schema.json",
        )

        assert (result, True), "Assertion Failed"

    @allure.title("Add new Artefacts in an On Demand Protocol")
    @allure.description(
        "This test case tests API used to verify that user is able to add new artifacts, responsibilities and people "
        "Involved in an on demand protocol "
    )
    @allure.link("https://app.clickup.com/t/27j11tr")
    @pytest.mark.update_artefacts
    def test_update_artefacts(self, test_create_protocol):
        id1 = test_create_protocol["ids"]
        cookies = test_create_protocol["login"]["cookies"]
        payload = {
            "artefacts": [
                {
                    "artefactName": "artefact",
                    "externalId": "id",
                    "additionalInfo": "info",
                    "key": "6132ae63-3537-4878-92c0-b5d542eb1462",
                }
            ],
            "responsibilities": [
                {
                    "key": "99e5e2f2-88a0-4813-9567-14df24d70527",
                    "department": "department",
                    "activity": "activity",
                }
            ],
            "people": [
                {
                    "key": "3ef1f6eb-bd5c-4c57-9a54-d9ffebfa7dd4",
                    "employeeId": "empid",
                    "name": "empname",
                    "role": "emprole",
                    "trainingRecordDetails": "emptraining",
                }
            ],
        }

        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/artefacts"
        )
        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        with open(
                "./tests/response/on_demand_protocol/update_artefacts.json", "w"
        ) as f:
            f.write(response.text)
        assert response.status_code == 200

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/update_artefacts_schema.json",
        )

        assert (result, True), "Assertion Failed"

    @allure.title("GEt all Verification available in On Demand Protocol")
    @allure.description(
        "This test case tests API used to get all available Verification in an on demand protool in formulation "
        "facility "
    )
    @allure.link("https://app.clickup.com/t/28mfh31")
    @pytest.mark.smoke
    @pytest.mark.get_all_verification
    def test_get_all_verification_formulation_facility(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection"
        )

        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_all_verification_formulation_facility.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_all_verification_formulation_facility_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("GEt all Verification available in On Demand Protocol")
    @allure.description(
        "This test case tests API used to get all available Verification in an on demand protool in API facility"
    )
    @allure.link("https://app.clickup.com/t/28mfh31")
    @pytest.mark.smoke
    @pytest.mark.get_all_verification
    def test_get_all_verification_api_facility(self, test_create_protocol_intermediate):
        cookies = test_create_protocol_intermediate["login"]["cookies"]
        id1 = test_create_protocol_intermediate["ids"]
        url = (
                test_create_protocol_intermediate["url"]
                + str(id1)
                + "/inspection"
        )

        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol_intermediate["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_all_verification_api_facility.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_all_verification_api_facility_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Select/Deselect Verification in an On Demand Protocol")
    @allure.description(
        "This test case tests API used to  update select/deselect Verification on verification page in an on demand protocol"
    )
    @allure.link("https://app.clickup.com/t/28u2p62")
    @pytest.mark.smoke
    @pytest.mark.update_verifications
    def test_update_verifications(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection"
        )
        verification_data = json.loads(
            self.test_get_all_verification_formulation_facility(test_create_protocol)["response"]
        )
        payload = verification_data["result"]
        payload.update({"cleaningAgent": False, "visual": False})

        response = requests.request(
            "PUT",
            url,
            headers=test_create_protocol["headers"],
            data=json.dumps(payload),
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/update_verifications.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_verifications_schema.json",
        )
        assert (result, True), "Assertion Failed"

    @allure.title("Get All Verification Details in an On Demand Protocol")
    @allure.description(
        "This test case tests API used to get all verification on acceptance criteria page in an on demand Protocol"
    )
    @allure.link("https://app.clickup.com/t/28zrd24")
    @pytest.mark.smoke
    @pytest.mark.verify_all_verification
    def test_verify_all_verification(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/all"
        )

        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        with open(
                "./tests/response/on_demand_protocol/verify_all_verification.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/verify_all_verification_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Create Protocol with production not assessed")
    @allure.description(
        "This test case tests API used to  create an on demand protocol with production which is not assessed "
    )
    @allure.link("https://app.clickup.com/t/29wdeuu")
    @pytest.mark.create_protocol_unassessed_production
    def test_create_protocol_unassessed_production(self, login):
        url = url = login["formualtion_facility_url"] + os.environ.get("ON_DEMAND_PROTOCOL")

        payload = {
            "protocolType": "validation",
            "name": "p",
            "productionId": 1124,
            "reason": "r",
            "externalId": "p",
            "authorId": 3,
            "description": None,
        }
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
        }
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=json.dumps(payload),
            cookies=login["cookies"],
        )
        assert response.status_code == 400
        with open(
                "./tests/response/on_demand_protocol/create_protocol_unassessed_production.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="test_data/validation_schemas/on_demand_protocol/create_protocol_unassessed_production_schema.json",
        )

        assert (result, True), "Assertion Failed"

    @allure.title("Get TOC Custom Policy ")
    @allure.description(
        "This test case tests API used to get custom rule and acceptance value for TOC in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82x2e")
    @pytest.mark.additional_test
    @pytest.mark.get_toc_custom
    def test_get_toc_custom(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/TOC/custom"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_toc_custom.json",
                "w",
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_toc_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get TOC Based on Policy in an On Demand Protocol")
    @allure.description(
        "This test case tests API used to get based On policy rule and acceptance value for TOC in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82x2d")
    @pytest.mark.additional_test
    @pytest.mark.get_toc_based_on_policy
    def test_get_toc_based_on_policy(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/TOC/policyBased"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_toc_based_on_policy.json",
                "w",
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_toc_based_on_policy_schema.json", )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Update and Save Based on Policy for TOC in On Demand Protocol  ")
    @allure.description(
        "This test case tests API used to update and save based on policy rule and acceptance value for toc in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82x2g")
    @pytest.mark.additional_test
    @pytest.mark.update_toc_based_on_policy
    def test_update_toc_based_on_policy(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        toc_based_on_policy = self.test_get_toc_based_on_policy(test_create_protocol)["response"]
        response_json = json.loads(toc_based_on_policy)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(toc_based_on_policy, "policyBased")["payload"]
            url = (
                    test_create_protocol["url"]
                    + str(id1)
                    + "/inspection/"
                    + str(id1)
                    + "/additional/TOC"
            )
            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            assert response.status_code == 200
            with open(
                    "./tests/response/on_demand_protocol/update_toc_based_on_policy.json",
                    "w",
            ) as f:
                f.write(response.text)
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_toc_based_on_policy_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Update and Save Empty TOC Custom Policy ")
    @allure.description(
        "This test case tests API to give error when empty custom acceptance value is saved for TOC in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82x2f")
    @pytest.mark.additional_test
    @pytest.mark.update_toc_empty_custom
    def test_update_toc_empty_custom(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        toc_custom_sal = self.test_get_toc_custom(test_create_protocol)["response"]
        response_json = json.loads(toc_custom_sal)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(toc_custom_sal, "custom")["payload"]
            url = (
                    test_create_protocol["url"]
                    + str(id1)
                    + "/inspection/"
                    + str(id1)
                    + "/additional/TOC"
            )
            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            assert response.status_code == 400
            with open(
                    "./tests/response/on_demand_protocol/update_toc_empty_custom.json", "w"
            ) as f:
                f.write(response.text)
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_toc_empty_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Get Cutstom rule and acceptance value for Conductivity in On Demand Protocol ")
    @allure.description(
        "This test case tests API used to get custom rule and acceptance value for Conductivity in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82xwq")
    @pytest.mark.additional_test
    @pytest.mark.get_conductivity_custom
    def test_get_conductivity_custom(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/Conductivity/custom"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_conductivity_custom.json",
                "w",
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_conductivity_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Based on Policy rule and acceptance value for Conductivity  in On Demand Protocol")
    @allure.description(
        "This test case tests API used to get Based on Policy rule and acceptance value for Conductivity in on demand protocol"
    )
    @allure.link("https://app.clickup.com/t/2f82xwp")
    @pytest.mark.additional_test
    @pytest.mark.get_conductivity_based_on_policy
    def test_get_conductivity_based_on_policy(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/Conductivity/policyBased"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_conductivity_based_on_policy.json",
                "w",
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_conductivity_based_on_policy_schema.json",
            )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Save Empty Custom Acceptance Value for Conductivity in an On Demand Protocol ")
    @allure.description(
        "This test case tests API to give error when empty custom acceptance value is saved for conductivity in an on demand protocol")
    @pytest.mark.additional_test
    @allure.link("https://app.clickup.com/t/2f82xwk")
    @pytest.mark.update_conductivity_empty_custom
    def test_update_conductivity_empty_custom(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        get_conductivity_custom = self.test_get_conductivity_custom(test_create_protocol)["response"]
        response_json = json.loads(get_conductivity_custom)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(get_conductivity_custom, "custom")["payload"]
            url = (
                    test_create_protocol["url"]
                    + str(id1)
                    + "/inspection/"
                    + str(id1)
                    + "/additional/Conductivity"
            )
            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            assert response.status_code == 400
            with open(
                    "./tests/response/on_demand_protocol/update_conductivity_empty_custom.json",
                    "w",
            ) as f:
                f.write(response.text)
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_conductivity_empty_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Update and Save Based on Policy for Conductivity in On Demand Protocol  ")
    @allure.description(
        "This test case tests API used to update and save based on policy rule and acceptance value for conductivity in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82xwn")
    @pytest.mark.additional_test
    @pytest.mark.update_conductivity_based_on_policy
    def test_update_conductivity_based_on_policy(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        get_conductivity_based_on_policy = self.test_get_conductivity_based_on_policy(test_create_protocol)["response"]
        response_json = json.loads(get_conductivity_based_on_policy)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(get_conductivity_based_on_policy, "policyBased")["payload"]
            url = (
                    test_create_protocol["url"]
                    + str(id1)
                    + "/inspection/"
                    + str(id1)
                    + "/additional/Conductivity"
            )
            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            assert response.status_code == 200
            with open(
                    "./tests/response/on_demand_protocol/update_conductivity_based_on_policy.json",
                    "w",
            ) as f:
                f.write(response.text)
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_conductivity_based_on_policy_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Get Based on Policy rule and acceptance value for Atomic Adsorption  in On Demand Protocol")
    @allure.description(
        "This test case tests API used to get Based on Policy rule and acceptance value for atomic adsorption in on demand protocol"
    )
    @allure.link("https://app.clickup.com/t/2f82y99")
    @pytest.mark.additional_test
    @pytest.mark.get_atomic_adsorption_based_on_policy
    def test_get_atomic_absorption_based_on_policy(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/AA/policyBased"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_atomic_adsorption_based_on_policy.json",
                "w",
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_atomic_adsorption_based_on_policy_schema.json",
            )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Custom rule and acceptance value for Atomic Adsorption  in On Demand Protocol")
    @allure.description(
        "This test case tests API used to get Custom rule and acceptance value for atomic adsorption in on demand protocol"
    )
    @allure.link("https://app.clickup.com/t/2f82y9c")
    @pytest.mark.additional_test
    @pytest.mark.get_atomic_adsorption_custom
    def test_get_atomic_absorption_custom(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/additional/AA/custom"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_atomic_adsorption_custom.json",
                "w",
        ) as f:
            f.write(response.text)
        response_json = json.loads(response.text)
        if response_json["result"] != {}:
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_atomic_adsorption_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Update and Save Based on Policy for Atomic Adsorption in On Demand Protocol  ")
    @allure.description(
        "This test case tests API used to update and save based on policy rule and acceptance value for Atomic Adsorption in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82y97")
    @pytest.mark.additional_test
    @pytest.mark.update_atomic_adsorption_based_on_policy
    def test_update_atomic_adsorption_based_on_policy(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        atomic_adsorption_based_on_policy = self.test_get_atomic_absorption_based_on_policy(test_create_protocol)[
            "response"]
        response_json = json.loads(atomic_adsorption_based_on_policy)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(atomic_adsorption_based_on_policy, "policyBased")["payload"]
            url = (
                    test_create_protocol["url"]
                    + str(id1)
                    + "/inspection/"
                    + str(id1)
                    + "/additional/AA"
            )
            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            assert response.status_code == 200
            with open(
                    "./tests/response/on_demand_protocol/update_atomic_adsorption_based_on_policy.json",
                    "w",
            ) as f:
                f.write(response.text)
            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_atomic_adsorption_based_on_policy_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Save Empty Custom Acceptance Value for Atomic Adsorption in an On Demand Protocol ")
    @allure.description(
        "This test case tests API to give error when empty custom acceptance value is saved for Atomic Adsorption in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f82y96")
    @pytest.mark.additional_test
    @pytest.mark.update_atomic_adsorption_empty_custom
    def test_update_atomic_adsorption_empty_custom(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        atomic_adsorption_custom = self.test_get_atomic_absorption_custom(test_create_protocol)["response"]
        response_json = json.loads(atomic_adsorption_custom)
        if response_json["result"] != {}:
            payload = create_additional_test_payload(atomic_adsorption_custom, "custom")["payload"]
            url = (
                    test_create_protocol["url"]
                    + str(id1)
                    + "/inspection/"
                    + str(id1)
                    + "/additional/AA"
            )
            response = requests.request(
                "PUT",
                url,
                headers=test_create_protocol["headers"],
                data=json.dumps(payload),
                cookies=cookies,
            )
            with open(
                    "./tests/response/on_demand_protocol/update_atomic_adsorption_empty_custom.json",
                    "w",
            ) as f:
                f.write(response.text)
            assert response.status_code == 400

            result = assert_valid_schema(
                json_data=json.loads(response.text),
                json_schema_file="./test_data/validation_schemas/on_demand_protocol/update_atomic_adsorption_empty_custom_schema.json",
            )
            assert (result, True), "Assertion Failed"

    @allure.title("Get Based on Policy limits for direct Microbial in On Demand Protocol")
    @allure.description(
        "This test case tests API used to get basd on policy limits for direct Microbial in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f84bmz")
    @pytest.mark.microbial
    @pytest.mark.get_direct_microbial_based_on_policy_limit
    def test_get_direct_microbial_based_on_policy_limit(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/microbial/policyBased/Direct"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_direct_microbial_based_on_policy_limit.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_direct_microbial_based_on_policy_limit_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Custom limits for direct Microbial in an On Demand Protocol ")
    @allure.description(
        "This test case tests API used to get custom limits for direct Microbial in an on demand protocol")
    @allure.link("https://app.clickup.com/t/2f84hwa")
    @pytest.mark.get_microbial_direct_custom_limit
    def test_get_microbial_direct_custom_limit(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/microbial/custom/Direct"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_microbial_direct_custom_limit.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_microbial_direct_custom_limit_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Custom Limit for Indirect Microbial in an On Demand Protocol ")
    @allure.description(
        "This test case tests API used to get custom limit for Indirect Microbial in anon demand protocol")
    @allure.link("https://app.clickup.com/t/2f84azr")
    @pytest.mark.get_microbial_indirect_custom_limit
    def test_get_microbial_indirect_custom_limit(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/microbial/custom/Indirect"
        )
        response = requests.request(
            "GET",
            url,
            headers=test_create_protocol["headers"],
            cookies=cookies,
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_microbial_indirest_custom_limit.json",
                "w",
        ) as f:
            f.write(response.text)

        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_microbial_indirect_custom_limit_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}

    @allure.title("Get Based on Policy limit for Indirect Microbial Residue ")
    @allure.description(
        "This test case tests API used to get based on policy limit for Indirect Microbial in an on demand protocol"
    )
    @allure.link("https://app.clickup.com/t/2f84aqd")
    @pytest.mark.get_microbial_indirect_based_on_policy_limit
    def test_get_microbial_indirect_based_on_policy_limit(self, test_create_protocol):
        cookies = test_create_protocol["login"]["cookies"]
        id1 = test_create_protocol["ids"]
        url = (
                test_create_protocol["url"]
                + str(id1)
                + "/inspection/"
                + str(id1)
                + "/microbial/policyBased/Indirect"
        )

        response = requests.request(
            "GET", url, headers=test_create_protocol["headers"], cookies=cookies
        )
        assert response.status_code == 200
        with open(
                "./tests/response/on_demand_protocol/get_microbial_indirect_based_on_policy_limit.json",
                "w",
        ) as f:
            f.write(response.text)
        result = assert_valid_schema(
            json_data=json.loads(response.text),
            json_schema_file="./test_data/validation_schemas/on_demand_protocol/get_microbial_indirect_based_on_policy_limit_schema.json",
        )
        assert (result, True), "Assertion Failed"
        return {"response": response.text}
