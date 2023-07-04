import sys
import os
import json
import pytest

sys.path.append(".")

COOKIES = None
ENV = None
FACILITY_URL = None
FACILITY_TYPE = None
HEADERS = {'Content-Type': 'application/json'}
MASTER_DATA = None

FEATURES = "/features"
ADDITIONAL_CLEANING_CRITERIA = "/additional-cleaning-criteria"
CLEANING_LIMIT_POLICY = "/cleaning_limit_policies"
CHEMICAL = "/Chemical"
INTERMEDIATE_CLEANING_LIMIT_POLICY = "/intermediate-cleaning-limit-policies"
WORST_CASE_SELECTION = "/selection-criteria"
DEFAULT_UNITS = "/default_units/"
MASTER = "/master"
CLEANING_ASSESSMENT = "/cleaning-assessments"
QUALIFICATION_TASK_EVALUATION = "/qualification-task?evaluationId="
QUALIFICATION_TASK = "/qualification-task/task/"
PRODUCTIONS = "/productions?table=true&pageNumber="
PRODUCTION = "/productions/"
VARIABLES = "/variables/"
EQUIPMENTS = "/equipments?pageNumber="
EQUIPMENT = "/equipments/"
PAGE_LIMIT_10 = "&pageLimit=10"
PAGE_LIMIT_20 = "&pageLimit=20"
ATTRIBUTE = "/attributes/"
SAMPLING_POLICY = "/sampling-policy/"
UNARCHIVE = "?unarchive=true"


def get_master_data():
    return "test_data/master_data/" + ENV.lower() + "/master_data_" + FACILITY_TYPE + ".xlsx"
