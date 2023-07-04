import pytest
from math import floor, log10


# This method is used to compare two values and take input parameters as sal_application in key value pair,
# sal_sheet in key and value as a list, columns as list of columns and error msg
def compare_sal(sal_application, sal_sheet, columns, error_message):
    assert len(sal_application) == len(sal_sheet[columns[0]]), error_message + str(
        len(sal_application)) + str(len(sal_sheet[columns[0]]))

    entity = sal_sheet[columns[0]]
    sal_limit = sal_sheet[columns[1]]
    keys = list(sal_application.keys())
    for i in keys:
        for (k, n) in zip(entity, sal_limit):
            if i == k and n != "#N/A":
                compare(sal_application[i], n, i)


# This method is used to compare the two different sal value and can compare upto 3 decimal
def compare(sal1, sal2, error_message):
    if sal1 != "#N/A" and sal2 != "#N/A":
        if sal1 < 1:
            length = (floor(log10(sal1)) - 1)
        else:
            length = 15 - len(str(int(sal1)))
        if length < 0:
            sal1 = (round(sal1, -length + 3))
            sal2 = (round(sal2, -length + 3))
            assert sal1 == sal2, error_message + " " + str(sal1) + " Not Equal " + str(sal2)
        else:
            sal1 = round(sal1, 3)
            sal2 = round(sal2, 3)
            assert sal1 == sal2, error_message + " " + str(sal1) + " Not Equal " + str(sal2)
    else:
        assert sal1 == sal2, error_message + " " + str(sal1) + " Not Equal " + str(sal2)


def skip_test_same_condition(condition1, condition2, message):
    if condition1 == condition2:
        pytest.skip(message)


def skip_test_different_condition(condition1, condition2, message):
    if condition1 != condition2:
        pytest.skip(message)
