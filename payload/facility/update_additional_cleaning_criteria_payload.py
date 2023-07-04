import random

def create_update_additional_cleaning_criteria_payload(response):
    result = response["result"]
    result["TOC"]["isActive"] = "true"
    result["pH"]["isActive"] = "true"
    result["Conductivity"]["isActive"] = "true"
    result["AA"]["isActive"] = "true"
    result["Odour"]["isActive"] = "true"
    result["RC"]["isActive"] = "true"
    result["TOC"]["swabAcceptanceCriterion"] = {
        "type": "GreaterThan",
        "value": {
          "value": 2,
          "unit": "ppb"
        }
      }
    result["TOC"]["rinseAcceptanceCriterion"] = {
        "type": "GreaterThan",
        "value": {
          "value": random.random(),
          "unit": "ppb"
        }
      }

    result["pH"]["swabAcceptanceCriterion"] = {
        "type": "GreaterThan",
        "value": {
          "value": 20,
          "unit": ""
        }
      }
    result["pH"]["rinseAcceptanceCriterion"] = {
        "type": "GreaterThan",
        "value": {
          "value": 30,
          "unit": ""
        }
      }

    result["Conductivity"]["swabAcceptanceCriterion"] = {
        "type": "GreaterThan",
        "value": {
          "value": 2,
          "unit": "uS/cm"
        }
      }
    result["Conductivity"]["rinseAcceptanceCriterion"] = {
        "type": "GreaterThan",
        "value": {
          "value": 2,
          "unit": "uS/cm"
        }
      }

    result["AA"]["swabAcceptanceCriterion"]= {
        "type": "GreaterThan",
        "value": {
          "value": 2,
          "unit": ""
        }
      }
    result["AA"]["rinseAcceptanceCriterion"] = {
        "type": "GreaterThan",
        "value": {
          "value": 3,
          "unit": ""
        }
      }
    result["Odour"]["swabAcceptanceCriterion"]= {
        "type": "EqualTo",
        "value": {
          "value": 1,
          "unit": ""
        }
      }
    result["Odour"]["rinseAcceptanceCriterion"] = {
        "type": "EqualTo",
        "value": {
          "value": 1,
          "unit": ""
        }
      }
    result["RC"]["swabAcceptanceCriterion"] = {
        "type": "EqualTo",
        "value": {
            "value": 1,
            "unit": ""
        }
    }
    result["RC"]["rinseAcceptanceCriterion"] = {
        "type": "EqualTo",
        "value": {
            "value": 1,
            "unit": ""
        }
    }
    payload ={"criteria":result,"reason":"test"}
    return {"payload":payload}

