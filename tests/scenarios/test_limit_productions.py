import json
import sys
import allure
from util.excel import Excel
from util.common_methods import *
from util import constants as const
import unit.change_assessment.test_cleaning_assessment as cleaning_assessment
import unit.settings.test_default_unit as default_unit
import unit.production.test_production as production
import unit.settings.cleaning_limit_policies.test_active_cleaning_limit_policy as active_policy
import unit.settings.cleaning_limit_policies.test_intermediate_cleaning_limit_policy as intermediate_policy
import unit.settings.test_variables as variable
from payload.facility.update_cleaning_limit_policy_for_actives import create_cleaning_limit_policy_active_pyload
from payload.facility.update_cleaning_limit_policy_intermediate import create_cleaning_limit_policy_intermediate_pyload
sys.path.append(".")


@pytest.mark.scenario
@pytest.mark.production_limits
class TestLimitOnProduction:
    get_production = production.TestProduction()
    update_active_policy = active_policy.TestActiveCleaningLimitPolicy()
    change_assessment = cleaning_assessment.TestCleaningAssessment()
    update_intermediate_policy = intermediate_policy.TestIntermediateCleaningLimitPolicy()
    update_default_unit = default_unit.TestDefaultUnits()
    update_variable = variable.TestVariables()

    ERROR_MESSAGE = "No. of Equipment from Excel and Application are not same"

    @staticmethod
    def calculated_sal_excel(sheet_name, columns):
        manually_calculated_limit = Excel.read_excel_columns_name_row_value(const.get_master_data(),
                                                                            sheet_name, columns, "minimum")
        lowest_manually_calculated_sal = Excel.read_excel_columns_name_row_value(const.get_master_data(),
                                                                                 sheet_name, columns,
                                                                                 "minimum_of_all")
        return manually_calculated_limit, lowest_manually_calculated_sal

    @allure.title("This method will setup the cleaning limit policy for actives")
    @pytest.fixture(scope="session", autouse=True)
    def setup_production_limits(self):
        data = {}
        global PRODUCTION_LIST
        columns_prod = ["production_id", "api_production_id", "intermediate_production_id"]
        PRODUCTION_LIST = Excel.read_excel_columns(const.get_master_data(), "config", columns_prod)
        columns = ["default_unit_name", "default_unit", "formulation_default_arl", "variable_name", "variable_value"]

        excel_data = Excel.read_excel_columns(const.get_master_data(), "config", columns)
        default_unit_name = excel_data["default_unit_name"]
        default_unit = excel_data["default_unit"]
        for (i, j) in zip(default_unit_name, default_unit):
            data.update({"default_unit_name": i})
            data.update({"default_unit": j})
            self.update_default_unit.test_update_default_unit(data)

        variable_name = excel_data["variable_name"]
        variable_value = excel_data["variable_value"]
        for (i, j) in zip(variable_name, variable_value):
            data.update({"variables_name": i})
            data.update({"variable_value": j})
            self.update_variable.test_update_variable_value(data)

        if const.FACILITY_TYPE != "api":
            formulation_default_arl = excel_data["formulation_default_arl"][0]
            policy_data = {"arl_value": formulation_default_arl, "ignoreCombo": False,
                           "useGlobalRecoveryPercentage": False, "salMassUnit": "mg", "useResidueLimit": False}
            data = {}
            get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
            get_policy = get_policy["policy"]
            arl_value = get_policy["arl"]["value"]
            sal_unit = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
            update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
            data.update({"update_policy_payload": update_policy})

            if get_policy != update_policy["data"] or arl_value != formulation_default_arl or sal_unit != "mg":
                self.update_active_policy.test_update_active_policy(data)
                self.change_assessment.test_start_cleaning_assessment(scenario=True)

        else:
            columns = ["api_default_arl", "api_intermediate_default_arl",
                       "intermediate_api_default_arl", "intermediate_intermediate_default_arl"]

            excel_data = Excel.read_excel_columns(const.get_master_data(), "config", columns)
            excel_api_api_default_arl = excel_data["api_default_arl"][0]
            excel_api_intermediate_default_arl = excel_data["api_intermediate_default_arl"][0]
            excel_intermediate_api_default_arl = excel_data["intermediate_api_default_arl"][0]
            excel_intermediate_intermediate_default_arl = excel_data["intermediate_intermediate_default_arl"][0]

            api_policy_data = {"arl_value": excel_api_api_default_arl, "useFirstAvailableCriteria": False,
                               "intermediateArl": excel_api_intermediate_default_arl, "useResidueLimit": False,
                               "useGlobalRecoveryPercentage": False, "salMassUnit": "mg"}
            intermediate_policy_data = {"active_arl_value": excel_intermediate_api_default_arl,
                                        "arl_value": excel_intermediate_intermediate_default_arl,
                                        "useResidueLimit": False,
                                        "useGlobalRecoveryPercentage": False, "salMassUnit": "mg"}
            get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
            get_policy = get_policy["policy"]
            api_api_arl_value = get_policy["arl"]["value"]
            sal_unit = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
            get_policy_intermediate = json.loads(
                self.update_intermediate_policy.test_get_intermediate_cleaning_limit_policy())
            get_policy_intermediate = get_policy_intermediate["policy"]
            intermediate_intermediate_arl_value = get_policy_intermediate["arl"]["value"]
            intermediate_api_arl_value = get_policy_intermediate["activesArl"]
            intermediate_sal_unit = get_policy_intermediate["limitRepresentation"]["productAndEquipmentLimits"][
                "salMassUnit"]
            update_policy_intermediate = create_cleaning_limit_policy_intermediate_pyload(get_policy_intermediate,
                                                                                          intermediate_policy_data)
            update_policy_api = create_cleaning_limit_policy_active_pyload(get_policy, api_policy_data)
            perform_change_assessment = False
            data.update({"update_policy_payload": update_policy_api,
                         "update_intermediate_policy_payload": update_policy_intermediate})

            if get_policy != update_policy_api["data"] or api_api_arl_value != excel_api_api_default_arl \
                    or sal_unit == "ug":
                self.update_active_policy.test_update_active_policy(data)
                perform_change_assessment = True
            if intermediate_sal_unit == "ug" or intermediate_api_arl_value != excel_intermediate_api_default_arl \
                    or intermediate_intermediate_arl_value != excel_intermediate_intermediate_default_arl:
                self.update_intermediate_policy.test_update_intermediate_policy(data)
                perform_change_assessment = True

            if perform_change_assessment is True:
                self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test Production wise SAL for All Criteria")
    @allure.description("This test case tests Production wise SAL when All Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2nggbt7")
    @pytest.mark.formulation
    @pytest.mark.validate_production_sal_productwise_all_criteria
    def test_validate_formulation_production_sal_productwise_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production_id": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_mg_sqcm"][0], prod)

    @allure.title("Test Production wise SAL for Toxicity Criteria")
    @allure.description("This test case Validates Production wise SAL when Toxicity Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2nggbvq")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_productwise_toxicity
    def test_validate_formulation_production_sal_productwise_toxicity(self):
        policy_data = {"useDosage": False, "useToxicity": True, "useProductLimit": True, "useARL": False}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "sal_toxicity_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_toxicity_mg_sqcm"][0], prod)

    @allure.title("Test Production wise SAL for Dosage Criteria")
    @allure.description("This test case tests Production wise SAL when Dosage Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2nggbxp")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_productwise_dosage
    def test_validate_formulation_production_sal_productwise_dosage(self):
        policy_data = {"useDosage": True, "useToxicity": False, "useProductLimit": True, "useARL": False}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "sal_dosage_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_dosage_mg_sqcm"][0], prod)

    @allure.title("Test Production wise SAL for Default Criteria")
    @allure.description("This test case tests Production wise SAL when Default Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2nggby0")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_productwise_default
    def test_validate_formulation_production_sal_productwise_default(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useProductLimit": True, "useARL": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "sal_default_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_default_mg_sqcm"][0], prod)

    @allure.title("Test Equipment wise SAL for All Criteria")
    @allure.description("This test case tests Equipment wise SAL when All Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2rbyrv9")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_equipmentwise_all_criteria
    def test_validate_formulation_production_sal_equipmentwise_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": False, "useARL": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_equipmentwise_sal"
            columns = ["Equipment ID", "final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_mg_sqcm"][0], prod)

    @allure.title("Test Equipment wise SAL for Toxicity Criteria")
    @allure.description("This test case tests Equipment wise SAL when Toxicity Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2rbyrtn")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_equipmentwise_toxicity
    def test_validate_formulation_production_sal_equipmentwise_toxicity(self):
        policy_data = {"useDosage": False, "useToxicity": True, "useProductLimit": False, "useARL": False}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_equipmentwise_sal"
            columns = ["Equipment ID", "sal_toxicity_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_toxicity_mg_sqcm"][0], prod)

    @allure.title("Test Equipment wise SAL for Dosage Criteria")
    @allure.description("This test case tests Equipment wise SAL when Dosage Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2rbyrtq")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_equipmentwise_dosage
    def test_validate_formulation_production_sal_equipmentwise_dosage(self):
        policy_data = {"useDosage": True, "useToxicity": False, "useProductLimit": False, "useARL": False}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_equipmentwise_sal"
            columns = ["Equipment ID", "sal_dosage_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_dosage_mg_sqcm"][0], prod)

    @allure.title("Test Equipment wise SAL for Default Criteria")
    @allure.description("This test case tests Equipment wise SAL when Default Criteria in Policy is selected"
                        " for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2rbyrtr")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_equipmentwise_default
    def test_validate_formulation_production_sal_equipmentwise_default(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useProductLimit": False, "useARL": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_equipmentwise_sal"
            columns = ["Equipment ID", "sal_default_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_default_mg_sqcm"][0], prod)

    @allure.title("Test Production wise SAL for All Criteria with Global Recovery Factor")
    @allure.description("This test case tests Production wise SAL when Global Recovery Factor when"
                        " All Criteria in Policy is selected for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2te95kw")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_productwise_global_recovery_all_criteria
    def test_validate_formulation_production_sal_productwise_global_recovery_all_criteria(self):
        global_recovery_percentage = Excel.read_excel_col_name_row_number(const.get_master_data(),
                                                                          "config",
                                                                          "global_recovery_percentage",
                                                                          2)
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "globalRecoveryPercentage": global_recovery_percentage,
                       "useGlobalRecoveryPercentage": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "global_recovery_percentage_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["global_recovery_percentage_sal_mg_sqcm"][0], prod)
        policy_data = {"useGlobalRecoveryPercentage": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test Production wise SAL for All Criteria with Global Recovery Factor")
    @allure.description("This test case tests Production wise SAL when SAL unit is ug/sqcm for"
                        " All Criteria in Policy is selected for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2uayjxb")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_productwise_sal_unit_ug_all_criteria
    def test_validate_formulation_production_productwise_sal_unit_ug_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "salMassUnit": "ug"}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        sal_unit = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"] or sal_unit != "ug":
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "final_sal_ug_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_ug_sqcm"][0], prod)
        policy_data = {"salMassUnit": "mg"}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test Production wise SAL for All Criteria with Global Recovery Factor")
    @allure.description("This test case tests Production wise SAL when Upper Limit on SAL is True for"
                        " All Criteria in Policy is selected for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2uayjrj")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_productwise_upper_limit_all_criteria
    def test_validate_formulation_production_productwise_upper_limit_all_criteria(self):
        upper_limit = Excel.read_excel_col_name_row_number(const.get_master_data(),
                                                           "config", "upper_limit", 2)
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "useResidueLimit": True, "residueLimit": upper_limit}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        upper_limit_sal = get_policy["residueLimit"]["value"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"] or upper_limit_sal != policy_data["residueLimit"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "upperlimit_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["upperlimit_mg_sqcm"][0], prod)
        policy_data = {"useResidueLimit": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test Production wise SAL when Same API to Same API Limits is OFF")
    @allure.description("This test case tests Production wise SAL when All Criteria Same API to Same API Limits is OFF"
                        " in Policy is selected for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2vyfdh5")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_productwise_same_api_all_criteria
    def test_validate_formulation_production_sal_productwise_same_api_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": True, "useARL": True,
                       "ignoreCombo": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_productwise_sal"
            columns = ["Equipment ID", "same_api_final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["same_api_final_sal_mg_sqcm"][0], prod)

    @allure.title("Test Equipment wise SAL when Same API to Same API Limits is OFF")
    @allure.description(
        "This test case tests Equipment wise SAL when All Criteria and Same API to Same API Limits is "
        "OFF in Policy is selected for each Equipment mapped to Production")
    @allure.link("https://app.clickup.com/t/2vyfdhj")
    @pytest.mark.formulation
    @pytest.mark.validate_formulation_production_sal_equipmentwise_same_api_all_criteria
    def test_validate_formulation_production_sal_equipmentwise_same_api_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useProductLimit": False, "useARL": True,
                       "ignoreCombo": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower() + "_equipmentwise_sal"
            columns = ["Equipment ID", "same_api_final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["same_api_final_sal_mg_sqcm"][0], prod)

    @allure.title("Test SAL of Production for Toxicity Criteria in API Facility")
    @allure.description("This test case tests SAL when Toxicity Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2qfcg4u")
    @pytest.mark.active
    @pytest.mark.validate_api_production_sal_toxicity
    def test_validate_api_production_sal_toxicity(self):
        policy_data = {"useDosage": False, "useToxicity": True, "useARL": False, "useLd50": False}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "sal_toxicity_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_toxicity_mg_sqcm"][0], prod)

    @allure.title("Test SAL of Production for LD50 Criteria in API Facility")
    @allure.description("This test case tests SAL when LD50 Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2nggc57")
    @pytest.mark.validate_api_production_sal_ld50
    @pytest.mark.v41x
    @pytest.mark.active
    def test_validate_api_production_sal_ld50(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useARL": False, "useLd50": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "sal_ld50_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_ld50_mg_sqcm"][0], prod)

    @allure.title("Test SAL of Production for Default Criteria in API Facility")
    @allure.description("This test case tests SAL when Default Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2qfch4t")
    @pytest.mark.active
    @pytest.mark.validate_api_production_sal_default
    def test_validate_api_production_sal_default(self):
        policy_data = {"useDosage": False, "useToxicity": False, "useARL": True, "useLd50": False}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "sal_default_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_default_mg_sqcm"][0], prod)

    @allure.title("Test SAL of Production for Dosage Criteria in API Facility")
    @allure.description("This test case tests SAL when Dosage Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2qfcg8f")
    @pytest.mark.active
    @pytest.mark.validate_api_production_sal_dosage
    def test_validate_api_production_sal_dosage(self):
        policy_data = {"useDosage": True, "useToxicity": False, "useARL": False, "useLd50": False}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "sal_dosage_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["sal_dosage_mg_sqcm"][0], prod)

    @allure.title("Test SAL of Production(API) for All Criteria in API Facility")
    @allure.description("This test case tests SAL when All Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2nggc79")
    @pytest.mark.active
    @pytest.mark.validate_api_production_sal_all_criteria
    def test_validate_api_production_sal_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useARL": True, "useLd50": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_mg_sqcm"][0], prod)

    @allure.title("Test SAL of Production(Intermediate) for Default Criteria in API Facility")
    @allure.description("This test case tests SAL when Default Criteria in Policy is selected"
                        " for each Equipment mapped to Production(Intermediate) in API Facility")
    @allure.link("https://app.clickup.com/t/2rbyuy9")
    @pytest.mark.active
    @pytest.mark.validate_intermediate_production_sal
    def test_validate_intermediate_production_sal(self):
        data = {}
        production_id = PRODUCTION_LIST["intermediate_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["final_sal_mg_sqcm", "final_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_mg_sqcm"][0], prod)

    @allure.title("Test SAL of Production(API) for All Criteria in API Facility")
    @allure.description("This test case tests SAL when All Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2uaynye")
    @pytest.mark.active
    @pytest.mark.validate_api_production_sal_global_recovery_all_criteria
    def test_validate_api_production_sal_global_recovery_all_criteria(self):
        global_recovery_percentage = Excel.read_excel_col_name_row_number(const.get_master_data(),
                                                                          "config", "global_recovery_percentage", 2)
        policy_data = {"useDosage": True, "useToxicity": True, "useARL": True, "useLd50": True,
                       "globalRecoveryPercentage": global_recovery_percentage, "useGlobalRecoveryPercentage": True}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "global_recovery_percentage_sal_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["global_recovery_percentage_sal_mg_sqcm"][0], prod)
        policy_data = {"useGlobalRecoveryPercentage": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test SAL of Production(API) for All Criteria in API Facility")
    @allure.description("This test case tests SAL when All Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2uayp01")
    @pytest.mark.active
    @pytest.mark.validate_api_production_sal_unit_ug_all_criteria
    def test_validate_api_production_sal_unit_ug_all_criteria(self):
        policy_data = {"useDosage": True, "useToxicity": True, "useARL": True, "useLd50": True, "salMassUnit": "ug"}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        sal_unit = get_policy["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"] or sal_unit != "ug":
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "final_sal_ug_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["final_sal_ug_sqcm"][0], prod)
        policy_data = {"salMassUnit": "mg"}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)

    @allure.title("Test SAL of Production(API) for All Criteria in API Facility")
    @allure.description("This test case tests SAL when All Criteria in Policy is selected"
                        " for each Equipment mapped to Production in API Facility")
    @allure.link("https://app.clickup.com/t/2uayp19")
    @pytest.mark.active
    @pytest.mark.validate_api_production_sal_upper_limit_all_criteria
    def test_validate_api_production_sal_upper_limit_all_criteria(self):
        upper_limit_sal = Excel.read_excel_col_name_row_number(const.get_master_data(),
                                                               "config", "upper_limit", 2)
        policy_data = {"useDosage": True, "useToxicity": True, "useARL": True, "useLd50": True, "useResidueLimit": True,
                       "residueLimit": upper_limit_sal}
        data = {}
        get_policy = json.loads(self.update_active_policy.test_get_active_cleaning_limit_policy())
        get_policy = get_policy["policy"]
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        if get_policy != update_policy["data"] or upper_limit_sal != policy_data["residueLimit"]:
            self.update_active_policy.test_update_active_policy(data)
            self.change_assessment.test_start_cleaning_assessment(scenario=True)

        production_id = PRODUCTION_LIST["api_production_id"]
        for prod in production_id:
            data.update({"production": prod})
            sheet_name = prod.lower()
            columns = ["Equipment ID", "upperlimit_mg_sqcm"]
            manually_calculated_limit, lowest_manually_calculated_sal = self.calculated_sal_excel(sheet_name, columns)
            data.update({"production": prod})
            sal = self.get_production.get_production_sal_each_equipment(data)
            lowest_sal = self.get_production.get_production_lowest_sal(data)
            compare_sal(sal, manually_calculated_limit, columns, self.ERROR_MESSAGE)
            compare(lowest_sal, lowest_manually_calculated_sal["upperlimit_mg_sqcm"][0], prod)
        policy_data = {"useResidueLimit": False}
        update_policy = create_cleaning_limit_policy_active_pyload(get_policy, policy_data)
        data.update({"update_policy_payload": update_policy})
        self.update_active_policy.test_update_active_policy(data)
        self.change_assessment.test_start_cleaning_assessment(scenario=True)
