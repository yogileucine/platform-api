def create_update_default_unit_payload(data, new_unit):
    payload = {
        "shortName": data["shortName"],
        "name": data["name"],
        "unit": [
            new_unit
        ],
        "facilityId": data["facilityId"],
        "id": [
            data["id"]
        ],
        "reason": "Automation Test"
    }
    return payload
