import allure
import sys
from util.excel import Excel
import unit.settings.test_default_unit as default_unit
import unit.settings.cleaning_limit_policies.test_additional_cleaning_criteria as additional_cleaning_criteria
import unit.settings.sampling_location_assessment.test_sampling_location_assessment as sampling_location_assessment
from util.common_methods import *
from util import constants as const
from util.validate_response import *
from util.api_requests import Request
sys.path.append(".")


@pytest.mark.unit
@pytest.mark.import_data
class TestFileImport:
    update_default_unit = default_unit.TestDefaultUnits()
    additional_cleaning = additional_cleaning_criteria.TestAdditionalCleaningCriteria()
    sampling_loc_assessment = sampling_location_assessment.TestSamplingLocationAssessment()

    @allure.title("Import Master Data")
    @allure.description("This test case tests API to import master data in facility")
    @allure.link("https://app.clickup.com/t/2k600yj")
    @allure.link("https://app.clickup.com/t/2ngga7c")
    @pytest.mark.upload_data
    def test_import_master_data(self):
        default_data = {}
        columns = ["default_unit_name", "default_unit"]
        excel_data = Excel.read_excel_columns(const.get_master_data(), "config", columns)
        default_units = excel_data["default_unit"]
        default_units_name = excel_data["default_unit_name"]
        for (i, j) in zip(default_units_name, default_units):
            default_data.update({"default_unit_name": i})
            default_data.update({"default_unit": j})
            self.update_default_unit.test_update_default_unit(default_data)
        self.additional_cleaning.test_update_additional_cleaning_criteria(None)
        self.sampling_loc_assessment.test_update_assessment_attribute()
        self.sampling_loc_assessment.test_update_auto_selection_policies()
        form = {'title': 'Initial production import', 'reason': 'Initial production import', 'simulate': 'false'}
        files = {'master': ('test_data/data/master_data.xlsx', open(const.get_master_data(), 'rb'))}
        response = Request.post(const.MASTER, data=form, files=files, use_facility_url=True)
        status_200(response)
