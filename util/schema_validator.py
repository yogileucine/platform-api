from cgi import test

import jsonschema
import pytest
import requests
import os
import json
from jsonschema import Draft6Validator, validate

from jsonschema import validate


def get_schema(file):
    """This function loads the given schema available"""

    with open(file, 'r') as f:
        schema = json.load(f)
    return schema


def assert_valid_schema(json_data, json_schema_file):
    schema = get_schema(json_schema_file)
    validate(instance=json_data, schema=schema)
