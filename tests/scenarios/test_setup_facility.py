import sys
import allure
import unit.settings.test_selection_criteria as selection_criteria
import unit.change_assessment.test_cleaning_assessment as cleaning_assessment
import unit.migrate_data.test_file_import as file_import
from util.common_methods import *
from util import constants as const
sys.path.append(".")


@allure.title("On Demand Protocol")
@allure.description("These test cases test API of on demand protocol")
@pytest.mark.scenario
@pytest.mark.order("first")
class TestSetupFacility:
    criteria_selection = selection_criteria.TestSelectionCriteria()
    change_assessment = cleaning_assessment.TestCleaningAssessment()
    master_data_import = file_import.TestFileImport()

    @allure.title("Setup a Facility")
    @allure.description("This test case setup a facility by importing data, adding worst selection "
                        "criteria, making all additional test as true and submitting, approving change assessment")
    @allure.link("https://app.clickup.com/t/2uw2y2m")
    @pytest.mark.setup_facility
    def test_setup_facility(self):
        if const.FACILITY_TYPE != "api":
            self.criteria_selection.test_update_selection_criteria(None)
        self.master_data_import.test_import_master_data()
        self.change_assessment.test_start_cleaning_assessment(scenario=True)
        self.change_assessment.test_submit_approve_cleaning_assessment()

