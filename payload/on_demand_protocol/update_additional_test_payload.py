import json


def create_additional_test_payload(response,policy):
    result = json.loads(response)["result"]
    result["policy"]=policy
    payload = {
        "additionalTestVerification": result
    }
    return {"payload":payload}