def create_update_variable_payload(data, new_value):
    payload = {
        "name": data["name"],
        "shortName": data["shortName"],
        "unit": data["unit"],
        "description": data["description"],
        "defaultValue": str(new_value),
        "defaultValueReason": data["defaultValueReason"],
        "facilityId": data["facilityId"],
        "id": data["id"],
        "reason": "Test Automation"
    }
    return payload
