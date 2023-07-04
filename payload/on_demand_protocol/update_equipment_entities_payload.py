import array
import json


def create_update_equipment_entities_payload(response):
    result = list(response["result"])
    if len(result) is 1:
        if 'equipment' in result[0]:
            payload = {
                "disableIds": [],
                "enableIds": [],
                "eqDetails": {result[0]["equipment"]["id"]: {"cpId":str(result[0]["equipment"]["id"]) }}
            }
        elif 'equipmentGroup' in result[0]:
            payload = {
                "disableIds": [],
                "enableIds": [],
                "eqDetails": {result[0]["equipmentGroup"]["equipments"][0]["id"]: {"cpId": str(result[0]["equipmentGroup"]["equipments"][0]["id"])}}
            }
    else:
        if 'equipment' in result[0] and 'equipment' in result[1]:
            payload = {
                "disableIds": [result[0]["equipment"]["id"]],
                "enableIds": [],
                "eqDetails": {result[1]["equipment"]["id"]: {"cpId": str(result[1]["equipment"]["id"])}}
            }
        elif 'equipment' in result[0] and 'equipmentGroup' in result[1]:
            payload = {
                "disableIds": [result[0]["equipment"]["id"]],
                "enableIds": [],
                "eqDetails": {result[0]["equipmentGroup"]["equipments"][0]["id"]: {"cpId": str(result[0]["equipmentGroup"]["equipments"][0]["id"])}}
            }
        elif 'equipmentGroup' in result[0] and 'equipmentGroup' in result[1]:
            payload = {
                "disableIds": [result[0]["equipmentGroup"]["equipments"][0]["id"]],
                "enableIds": [],
                "eqDetails": {result[0]["equipmentGroup"]["equipments"][0]["id"]: {"cpId": str(result[0]["equipmentGroup"]["equipments"][0]["id"])}}
            }
        elif 'equipmentGroup' in result[0] and 'equipment' in result[1]:
            payload = {
                "disableIds": [result[0]["equipment"]["id"]],
                "enableIds": [],
                "eqDetails": {result[0]["equipmentGroup"]["equipments"][0]["id"]: {"cpId": str(result[0]["equipmentGroup"]["equipments"][0]["id"])}}
            }
    return {"payload":payload}

def create_diselect_all_protocol_equipment_entites_payload(response):
    result = list(response["result"])
    disable_equipment=[]
    length = (len(result))
    for i in range(length):
        if 'equipment' in result[i]:
            disable_equipment.append(result[i]["equipment"]["id"])

        elif 'equipmentGroup' in result[i]:
            for j in range(len(result[i]["equipmentGroup"]["equipments"])):
                disable_equipment.append(result[i]["equipmentGroup"]["equipments"][j]["id"])
    payload = {
        "disableIds": disable_equipment,
        "enableIds": [],
        "eqDetails": {}
    }
    return {"payload":payload}