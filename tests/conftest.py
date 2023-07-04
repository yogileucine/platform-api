import time
import pytest
import json
import sys

sys.path.append(".")
from dotenv import load_dotenv, find_dotenv
from http.cookies import SimpleCookie
from util.env_property import Env
from util import constants as const
from util.api_requests import Request
from util.validate_response import *


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="QA")
    parser.addoption("--ver", action="store", default="v4.1.x")
    parser.addoption("--facility", action="store")
    parser.addoption("--type", action="store")


# TO DO - Improve marker to skip test
def pytest_collection_modifyitems(config, items):
    if config.getoption("--ver") == "v4.1.x":
        # --runslow given in cli: do not skip slow tests
        skip_no_on_demand = pytest.mark.skip(reason="v4.0.x environment doesn't have on demand")
        for item in items:
            if "v40x" in item.keywords:
                item.add_marker(skip_no_on_demand)
    if config.getoption("--ver") == "v4.0.x":
        # --runslow given in cli: do not skip slow tests
        skip_qa_cleen = pytest.mark.skip(reason="v4.0.x environment doesn't have LD50")
        for item in items:
            if "v41x" in item.keywords:
                item.add_marker(skip_qa_cleen)
    if config.getoption("--type") == "formulation":
        # --runslow given in cli: do not skip slow tests
        skip_active = pytest.mark.skip(reason="test case for formulation only")
        for item in items:
            if "active" in item.keywords:
                item.add_marker(skip_active)
    if config.getoption("--type") == "active":
        # --runslow given in cli: do not skip slow tests
        skip_active = pytest.mark.skip(reason="test case for formulation only")
        for item in items:
            if "formulation" in item.keywords:
                item.add_marker(skip_active)
    return


@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv(find_dotenv())


@pytest.fixture(scope='session', autouse=True)
def login(request):
    Env.get_data()
    env = request.config.getoption("--env")
    const.ENV = env
    url = Env.get_login_url(env)
    payload = {
        "username": Env.get_env_data("ADMIN_USERNAME"),
        "password": Env.get_env_data("ADMIN_PASSWORD")
    }
    response = Request.post(data=payload, url=url)
    status_200(response)
    raw_cookie = response.headers['Set-Cookie']
    cookie = SimpleCookie()
    cookie.load(raw_cookie)
    cookies = {k: v.value for k, v in cookie.items()}
    const.COOKIES = cookies


@pytest.fixture(scope='session', autouse=True)
def get_facility(request, login):
    env = const.ENV
    facility = request.config.getoption("--facility")
    facilities_url = Env.get_facilities_url(env)
    get_facility = Request.get(facilities_url)
    get_facility_json = json.loads(get_facility.text)
    facilities = list(get_facility_json["facilities"])
    facility_id = None
    facility_type = None
    facility_url = None
    for i in range(len(facilities)):
        if facilities[i]["name"] == facility:
            facility_id = facilities[i]["id"]
            facility_type = facilities[i]["productType"]
            facility_url = Env.get_facilities_url(env) + facility_id
            break
    if facility_id is None:
        pytest.fail("Facility " + facility + " not found")
    const.FACILITY_URL = facility_url
    const.FACILITY_TYPE = facility_type


def pytest_terminal_summary(terminalreporter):
    passed = 0
    failed = 0
    deselected = 0
    skipped = 0
    try:
        passed = len(terminalreporter.stats['passed'])
        print('passed amount:', passed)
    except KeyError:
        print('passed amount:', passed)
    try:
        failed = len(terminalreporter.stats['failed'])
        print('failed amount:', failed)
    except KeyError:
        print('failed amount:', failed)
    try:
        deselected = len(terminalreporter.stats['deselected'])
        print('deselected amount:', deselected)
    except KeyError:
        print('deselected amount:', deselected)
    try:
        skipped = len(terminalreporter.stats['skipped'])
        print('skipped amount:', skipped)
    except KeyError:
        print('skipped amount:', skipped)
    with open(
            "./test_summary.txt", "w"
    ) as f:
        f.write(
            'passed amount:' + str(passed) + '\n' + 'failed amount:' + str(failed) + '\n' + 'deselected amount:' + str(
                deselected))
    duration = time.time() - terminalreporter._sessionstarttime
    print('duration:', duration, 'seconds')
