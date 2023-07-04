import allure
import pytest
import requests
import json
import sys
from util.excel import Excel
from util.common_methods import *
import util.constants as const
import unit.change_assessment.test_cleaning_assessment as cleaning_assessment
import unit.settings.test_default_unit as default_unit
import unit.production.test_equipment as equipment
import unit.settings.cleaning_limit_policies.test_active_cleaning_limit_policy as active_policy
import unit.settings.cleaning_limit_policies.test_intermediate_cleaning_limit_policy as intermediate_policy
import unit.settings.test_variables as variable
from payload.facility.update_cleaning_limit_policy_for_actives import create_cleaning_limit_policy_active_pyload
from payload.facility.update_cleaning_limit_policy_intermediate import create_cleaning_limit_policy_intermediate_pyload

sys.path.append(".")


@pytest.mark.limits
@pytest.mark.equipment_limits
class TestLimitsOnEquipments:
    get_equipment = equipment.TestEquipment()
    update_active_policy = active_policy.TestActiveCleaningLimitPolicy()
    change_assessment = cleaning_assessment.TestCleaningAssessment()
    update_intermediate_policy = intermediate_policy.TestIntermediateCleaningLimitPolicy()
    update_default_unit = default_unit.TestDefaultUnits()
    update_variable = variable.TestVariables()
    ERROR_MESSAGE = "No. of Production from Excel and Application are not same"

    @staticmethod
    def read_excel_sal(sheet_name, column):
        manually_calculated_limit = Excel.read_excel_columns_name_row_value(const.get_master_data(), sheet_name,
                                                                            column, "minimum")
        lowest_manually_calculated_sal = Excel.read_excel_columns_name_row_value(const.get_master_data(), sheet_name,
                                                                                 column, "minimum_of_all")
        return manually_calculated_limit, lowest_manually_calculated_sal

    @allure.title("This method will setup cleaning limit policy")
    @allure.description("This method will setup cleaning limit policy for actives and intermediates and will be "
                        "execute once before all test cases")
    @pytest.fixture(scope="session", autouse=True)
    def setup_equipment_limits(self):
        global EQUIPMENT_LIST
        EQUIPMENT_LIST = Excel.read_excel_columns(const.get_master_data(), "config", ["equipment_id"])
        data = {}
        columns = ["default_unit_name", "default_unit", "variable_name", "variable_value"]
        excel_data = Excel.read_excel_columns(const.get_master_data(), "config", columns)
        default_units_name = excel_data["default_unit_name"]
        default_unit = excel_data["default_unit"]
        for i, j in zip(default_units_name, default_unit):
            data.update({"default_unit_name": i})
            data.update({"default_unit": j})
            self.update_default_unit.test_update_default_unit(data)

        variables_name = excel_data["variable_name"]
        variables_value = excel_data["variable_value"]
        for i, j in zip(variables_name, variables_value):
            data.update({"variables_name": i})
            data.update({"variable_value": j})
            self.update_variable.test_update_variable_value(data)

        if const.FACILITY_TYPE != "api":
            default_arl = Excel.read_excel_col_name_row_number(const.get_master_data(), "config",
                                                               "formulation_default_arl", 2)
            policy_data = {"arl_value": default_arl, "ignoreCombo": False,
                           "useGlobalRecoveryPercentage": False, "salMassUnit": "mg", "useResidueLimit": False}
            get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
            get_policy = get_policy["policy"]
            arl_value = get_policy["arl"]["value"]
            sal_unit = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
            update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
            data.update({"update_policy_payload": update_policy})
            if get_policy != update_policy["data"] or arl_value != default_arl or sal_unit == "ug":
                self.update_active_policy.test_update_active_policy(data)
                self.change_assessment.test_start_cleaning_assessment(scenario=True)

        if const.FACILITY_TYPE == "api":
            columns = ["api_default_arl", "api_intermediate_default_arl", "intermediate_api_default_arl",
                       "intermediate_intermediate_default_arl"]
            excel_data = Excel.read_excel_columns(const.get_master_data(), "config", columns)
            api_api_default_arl = excel_data["api_default_arl"][0]
            api_intermediate_default_arl = excel_data["api_intermediate_default_arl"][0]
            intermediate_api_default_arl = excel_data["intermediate_api_default_arl"][0]
            intermediate_intermediate_default_arl = excel_data["intermediate_intermediate_default_arl"][0]

            policy_data = {"arl_value": api_api_default_arl, "useFirstAvailableCriteria": False,
                           "intermediateArl": api_intermediate_default_arl, "useResidueLimit": False,
                           "useGlobalRecoveryPercentage": False, "salMassUnit": "mg"}
            get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
            get_policy = get_policy["policy"]
            api_api_arl_value = get_policy["arl"]["value"]
            api_intermediate_arl_value = get_policy["intermediateArl"]
            sal_unit = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
            update_policy_api = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)

            intermediate_policy_data = {"active_arl_value": intermediate_api_default_arl,
                                        "arl_value": intermediate_intermediate_default_arl, "useResidueLimit": False,
                                        "useGlobalRecoveryPercentage": False, "salMassUnit": "mg"}
            get_policy_intermediate = json.loads(
                self.update_intermediate_policy.test_get_intermediate_cleaning_limit_policy())
            get_policy_intermediate = get_policy_intermediate["policy"]
            intermediate_intermediate_arl_value = get_policy_intermediate["arl"]["value"]
            intermediate_api_arl_value = get_policy_intermediate["activesArl"]
            intermediate_sal_unit = get_policy_intermediate["limitRepresentation"]["productAndEquipmentLimits"][
                "salMassUnit"]
            update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                          intermediate_policy_data)

            perform_change_assessment = False
            data.update({"update_policy_payload": update_policy_api,
                         "update_intermediate_policy_payload": update_policy_intermediate})
            if sal_unit == "ug" or get_policy != update_policy_api["data"] or api_api_arl_value != api_api_default_arl \
                    or api_intermediate_arl_value != api_intermediate_default_arl:
                self.update_active_policy.test_update_active_policy(data)
                perform_change_assessment = True

            if intermediate_sal_unit == "ug" or get_policy_intermediate["useGlobalRecoveryPercentage"] is True \
                    or get_policy_intermediate["useResidueLimit"] is True \
                    or intermediate_api_arl_value != intermediate_api_default_arl \
                    or intermediate_intermediate_arl_value != intermediate_intermediate_default_arl:
                self.update_intermediate_policy.test_update_intermediate_policy(data)
                perform_change_assessment = True

            if perform_change_assessment is True:
                self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test ProductWise All Criteria SAL of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when All Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2te94wn")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_sal_all_criteria
    def test_validate_formulation_equipment_sal_productwise_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_mg_sqcm"][0], equipment)

    @allure.title("Test ProductWise Toxicity SAL of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when Toxicity Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2te94wp")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_sal_toxicity
    def test_validate_formulation_equipment_sal_productwise_toxicity(self):
        policy_data = {"useDosage": False, "useToxicity": True, "useProductLimit": True, "useARL": False}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "sal_toxicity_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_toxicity_mg_sqcm"][0], equipment)

    @allure.title("Test ProductWise Dosage SAL of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when Dosage Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2te94wr")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_sal_dosage
    def test_validate_formulation_equipment_sal_productwise_dosage(self):
        policy_data = {"useDosage": True, "useToxicity": False, "useProductLimit": True, "useARL": False}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "sal_dosage_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_dosage_mg_sqcm"][0], equipment)

    @allure.title("Test ProductWise Default SAL of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when Default Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2te94wq")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_sal_default
    def test_validate_formulation_equipment_sal_productwise_default(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useProductLimit": True, "useARL": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "sal_default_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_default_mg_sqcm"][0], equipment)

    @allure.title("Test ProductWise Global Recovery Factor SAL of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when Global Recovery Factor is True"
                        " All Criteria in Policy is selected for each Production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/85zrj1tg4")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_sal_global_recovery
    def test_validate_formulation_equipment_productwise_sal_global_recovery(self):
        global_recovery_percentage = Excel.read_excel_col_name_row_number(const.get_master_data(), "config",
                                                                          "global_recovery_percentage", 2)
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "globalRecoveryPercentage": global_recovery_percentage, "useGlobalRecoveryPercentage": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "global_recovery_percentage_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["global_recovery_percentage_sal_mg_sqcm"][0], equipment)
        policy_data = {"useGlobalRecoveryPercentage": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test ProductWise SAL with ug unit of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when Unit is ug for"
                        " All Criteria in Policy is selected for each Production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/85zrj1tn9")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_sal_unit_ug
    def test_validate_formulation_equipment_productwise_sal_unit_ug(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "salMassUnit": "ug"}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        sal_unit = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"] or sal_unit != "ug":
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "final_sal_ug_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_ug_sqcm"][0], equipment)
        policy_data = {"salMassUnit": "mg"}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test ProductWise Upper Limit SAL of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when Upper Limit is True for"
                        " All Criteria in Policy is selected for each Production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/85zrj1tjt")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_upper_limit
    def test_validate_formulation_equipment_productwise_upper_limit(self):
        upper_limit = Excel.read_excel_col_name_row_number(const.get_master_data(), "config", "upper_limit", 2)
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "useResidueLimit": True, "residueLimit": upper_limit}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        upper_limit_sal = get_policy["residueLimit"]["value"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"] or upper_limit_sal != upper_limit:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "upperlimit_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["upperlimit_mg_sqcm"][0], equipment)
        policy_data = {"useResidueLimit": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test Equipment Wise All Criteria SAL of Productions on Equipments")
    @allure.description("This test case tests Equipment wise SAL when All Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2uayqc1")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_equipmentwise_sal_all_criteria
    def test_validate_formulation_equipment_equipmentwise_sal_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": False, "useARL": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_equipmentwise_sal"
            read_excel_column = ["Equipment ID", "final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_mg_sqcm"][0], equipment)

    @allure.title("Test Equipment Wise Toxicity Criteria SAL of Productions on Equipments")
    @allure.description("This test case tests Equipment wise SAL when Toxicity Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2uayqbz")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_equipmentwise_sal_toxicity
    def test_validate_formulation_equipment_equipmentwise_sal_toxicity(self):
        policy_data = {"useDosage": False, "useToxicity": True, "useProductLimit": False, "useARL": False}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_equipmentwise_sal"
            read_excel_column = ["Equipment ID", "sal_toxicity_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_toxicity_mg_sqcm"][0], equipment)

    @allure.title("Test Equipment Wise Dosage Criteria SAL of Productions on Equipments")
    @allure.description("This test case tests Equipment wise SAL when Dosage Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2uayqbx")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_equipmentwise_sal_dosage
    def test_validate_formulation_equipment_equipmentwise_sal_dosage(self):
        policy_data = {"useDosage": True, "useToxicity": False, "useProductLimit": False, "useARL": False}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_equipmentwise_sal"
            read_excel_column = ["Equipment ID", "sal_dosage_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_dosage_mg_sqcm"][0], equipment)

    @allure.title("Test Equipment Wise Default Criteria SAL of Productions on Equipments")
    @allure.description("This test case tests Equipment wise SAL when Default Criteria in Policy is selected"
                        " for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/2uayqc0")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_equipmentwise_sal_default
    def test_validate_formulation_equipment_equipmentwise_sal_default(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useProductLimit": False, "useARL": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_equipmentwise_sal"
            read_excel_column = ["Equipment ID", "sal_default_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_default_mg_sqcm"][0], equipment)

    @allure.title("Test ProductWise SAL when Same API to Same API Limits is OFF")
    @allure.description("This test case tests Production wise SAL when All Criteria and Same API to Same API Limits is"
                        " OFF in Policy is selected for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/85zrj1u2v")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_productwise_same_api_sal_all_criteria
    def test_validate_formulation_equipment_sal_productwise_same_api_all_criteria(self, login):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "ignoreCombo": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_productwise_sal"
            read_excel_column = ["Equipment ID", "same_api_final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["same_api_final_sal_mg_sqcm"][0], equipment)

    @allure.title("Test Equipment Wise SAL when Same API to Same API Limits is OFF")
    @allure.description("This test case tests Equipment wise SAL when All Criteria and Same API to Same API Limits is "
                        "OFF in Policy is selected for all production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/85zrj1u39")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_equipment_equipmentwise_same_api_sal_all_criteria
    def test_validate_formulation_equipment_equipmentwise_same_api_sal_all_criteria(self, login):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": False, "useARL": True,
                       "ignoreCombo": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment + "_equipmentwise_sal"
            read_excel_column = ["Equipment ID", "same_api_final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["same_api_final_sal_mg_sqcm"][0], equipment)

    @allure.title("Test SAL of Production on Equipments for Default Criteria in API Facility")
    @allure.description("This test case tests SAL when Default Criteria in Policy is selected"
                        " for all production mapped to Equipment in API Facility")
    @allure.link("https://app.clickup.com/t/85zrj1u9g")
    @pytest.mark.active
    @pytest.mark.validate_api_equipment_sal_default
    def test_validate_api_equipment_sal_default(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useARL": True, "useLD50": False}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "sal_default_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_default_mg_sqcm"][0], equipment)

    @allure.title("Test SAL of Production on Equipments for All Criteria in API Facility")
    @allure.description("This test case tests SAL when All Criteria in Policy is selected"
                        " for all production mapped to Equipment in API Facility")
    @allure.link("https://app.clickup.com/t/85zrj1u9d")
    @pytest.mark.active
    @pytest.mark.validate_api_equipment_sal_all_criteria
    def test_validate_api_equipment_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useARL": True, "useLD50": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_mg_sqcm"][0], equipment)

    @allure.title("Test SAL of Production on Equipments for Dosage Criteria in API Facility")
    @allure.description("This test case tests SAL when Dosage Criteria in Policy is selected"
                        " for all production mapped to Equipment in API Facility")
    @allure.link("https://app.clickup.com/t/85zrj1u9f")
    @pytest.mark.active
    @pytest.mark.validate_api_equipment_sal_dosage
    def test_validate_api_equipment_sal_dosage(self):
        policy_data = {"useDosage": True, "useToxicity": False, "useARL": False, "useLd50": False}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "sal_dosage_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_dosage_mg_sqcm"][0], equipment)

    @allure.title("Test SAL of Production on Equipments for LD50 Criteria in API Facility")
    @allure.description("This test case tests SAL when LD50 Criteria in Policy is selected"
                        " for all production mapped to Equipment in API Facility")
    @allure.link("https://app.clickup.com/t/85zrj1v0j")
    @pytest.mark.validate_api_equipment_sal_ld50
    @pytest.mark.active
    @pytest.mark.v41x
    def test_validate_api_equipment_sal_ld50(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useARL": False, "useLd50": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "sal_ld50_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_ld50_mg_sqcm"][0], equipment)

    @allure.title("Test SAL of Production on Equipments for Toxicity Criteria in API Facility")
    @allure.description("This test case tests SAL when Toxicity Criteria in Policy is selected"
                        " for all production mapped to Equipment in API Facility")
    @allure.link("https://app.clickup.com/t/85zrj1u9e")
    @pytest.mark.active
    @pytest.mark.validate_api_equipment_sal_toxicity
    def test_validate_api_equipment_sal_toxicity(self):
        policy_data = {"useDosage": False, "useToxicity": True, "useARL": False, "useLd50": False}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data = {"update_policy_payload": update_policy}
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)
        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "sal_toxicity_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_toxicity_mg_sqcm"][0], equipment)

    @allure.title("Test SAL of Production on Equipments for Global Recovery Factor in API Facility")
    @allure.description("This test case tests SAL when Global Recovery Factor and All Criteria in Policy is selected"
                        " for all production mapped to Equipment in API Facility")
    @allure.link("https://app.clickup.com/t/85zrj1u9p")
    @pytest.mark.active
    @pytest.mark.validate_api_equipment_sal_global_recovery
    def test_validate_api_equipment_global_recovery(self):
        global_recovery_percentage_api = Excel.read_excel_col_name_row_number(const.get_master_data(), "config",
                                                                              "global_recovery_percentage", 2)
        global_recovery_percentage_intermediate = Excel.read_excel_col_name_row_number(const.get_master_data(), "config",
                                                                        "intermediate_global_recovery_percentage", 2)
        policy_data_api = {"useDosage": True, "useToxicity": True, "useARL": True, "useLd50": True,
                           "globalRecoveryPercentage": global_recovery_percentage_api,
                           "useGlobalRecoveryPercentage": True}
        policy_data_intermediate = {"globalRecoveryPercentage": global_recovery_percentage_intermediate,
                                    "useGlobalRecoveryPercentage": True}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data_api)
        data = {"update_policy_payload": update_policy}
        get_policy_intermediate = json.loads(
            self.update_intermediate_policy.test_get_intermediate_cleaning_limit_policy())
        get_policy_intermediate = get_policy_intermediate["policy"]
        update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                      policy_data_intermediate)
        perform_change_assessment = False
        data.update({"update_intermediate_policy_payload": update_policy_intermediate})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            perform_change_assessment = True

        if get_policy_intermediate["useGlobalRecoveryPercentage"] is True \
                or get_policy_intermediate["globalRecoveryPercentage"] != global_recovery_percentage_intermediate:
            self.update_intermediate_policy.test_update_intermediate_policy(data)
            perform_change_assessment = True

        if perform_change_assessment is True:
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "global_recovery_percentage_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["global_recovery_percentage_sal_mg_sqcm"][0], equipment)
        policy_data_api = {"useGlobalRecoveryPercentage": False}
        policy_data_intermediate = {"useGlobalRecoveryPercentage": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data_api)
        update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                      policy_data_intermediate)
        data = {"update_policy_payload": update_policy}
        data.update({"update_intermediate_policy_payload": update_policy_intermediate})
        self.update_active_policy.test_update_active_policy(data)
        self.update_intermediate_policy.test_update_intermediate_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test SAL of Production on Equipments for Upper Limit in API Facility")
    @allure.description("This test case tests SAL when Upper Limit and All Criteria in Policy is selected"
                        " for all production mapped to Equipment in API Facility")
    @allure.link("https://app.clickup.com/t/85zrj1u9u")
    @pytest.mark.active
    @pytest.mark.validate_api_equipment_sal_upper_limit
    def test_validate_api_equipment_sal_upper_limit(self):
        upper_limit = Excel.read_excel_col_name_row_number(const.get_master_data(), "config", "upper_limit", 2)
        policy_data_api = {"useDosage": True, "useToxicity": True, "useARL": True, "useLd50": True,
                           "useResidueLimit": True, "residueLimit": upper_limit}
        policy_data_intermediate = {"useResidueLimit": True, "residueLimit": upper_limit}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data_api)
        data = {"update_policy_payload": update_policy}
        get_policy_intermediate = json.loads(
            self.update_intermediate_policy.test_get_intermediate_cleaning_limit_policy())
        get_policy_intermediate = get_policy_intermediate["policy"]
        update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                      policy_data_intermediate)
        perform_change_assessment = False
        data.update({"update_intermediate_policy_payload": update_policy_intermediate})
        if get_policy["useResidueLimit"] is False \
                or get_policy["residueLimit"]["value"] != upper_limit:
            self.update_active_policy.test_update_active_policy(data)
            perform_change_assessment = True

        if get_policy_intermediate["useResidueLimit"] is False \
                or get_policy_intermediate["residueLimit"]["value"] != upper_limit:
            self.update_intermediate_policy.test_update_intermediate_policy(data)
            perform_change_assessment = True

        if perform_change_assessment is True:
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "upperlimit_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["upperlimit_mg_sqcm"][0], equipment)
        policy_data_api = {"useResidueLimit": False}
        policy_data_intermediate = {"useResidueLimit": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data_api)
        update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                      policy_data_intermediate)
        data = {"update_policy_payload": update_policy}
        data.update({"update_intermediate_policy_payload": update_policy_intermediate})
        self.update_active_policy.test_update_active_policy(data)
        self.update_intermediate_policy.test_update_intermediate_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test ProductWise SAL with ug unit of Productions on Equipments")
    @allure.description("This test case tests Production wise SAL when Unit is ug for"
                        " All Criteria in Policy is selected for each Production mapped to Equipment")
    @allure.link("https://app.clickup.com/t/85zrj1u9q")
    @pytest.mark.active
    @pytest.mark.validate_api_sal_unit_ug
    def test_validate_api_equipment_sal_unit_ug(self):
        policy_data_api = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                           "useLd50": True, "salMassUnit": "ug"}
        policy_data_intermediate = {"salMassUnit": "ug"}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        sal_unit_api = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data_api)
        data = {"update_policy_payload": update_policy}
        get_policy_intermediate = json.loads(
            self.update_intermediate_policy.test_get_intermediate_cleaning_limit_policy())
        get_policy_intermediate = get_policy_intermediate["policy"]
        sal_unit_intermediate = get_policy_intermediate["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
        update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                      policy_data_intermediate)
        perform_change_assessment = False
        data.update({"update_intermediate_policy_payload": update_policy_intermediate})
        if sal_unit_api != "ug":
            self.update_active_policy.test_update_active_policy(data)
            perform_change_assessment = True

        if sal_unit_intermediate != "ug":
            self.update_intermediate_policy.test_update_intermediate_policy(data)
            perform_change_assessment = True

        if perform_change_assessment is True:
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        for equipment in EQUIPMENT_LIST["equipment_id"]:
            data.update({"equipment": equipment})
            sheet_name = equipment
            read_excel_column = ["Equipment ID", "final_sal_ug_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.read_excel_sal(sheet_name,
                                                                                            read_excel_column)
            sal = self.get_equipment.get_production_sal_each_equipment(data)
            lowest_sal = self.get_equipment.get_equipment_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, read_excel_column, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_ug_sqcm"][0], equipment)
        policy_data_api = {"salMassUnit": "mg"}
        policy_data_intermediate = {"salMassUnit": "mg"}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data_api)
        update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                      policy_data_intermediate)
        data = {"update_policy_payload": update_policy}
        data.update({"update_intermediate_policy_payload": update_policy_intermediate})
        self.update_active_policy.test_update_active_policy(data)
        self.update_intermediate_policy.test_update_intermediate_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)