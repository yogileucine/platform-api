def create_cleaning_limit_policy_active_pyload(response_data, update_data):
    data = dict(response_data)
    keys = list(update_data.keys())
    data["useGlobalRecoveryPercentage"] = False
    data["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"] = "mg"
    data["useResidueLimit"] = False
    for i in range(len(keys)):
        if keys[i] == "arl_value":
            data["arl"]["value"] = update_data["arl_value"]
        if keys[i] == "residueLimit":
            data["residueLimit"]["value"] = update_data["residueLimit"]
            data["residueLimit"]["unit"] = "mg/sqcm"
        if keys[i] == "salMassUnit":
            data["limitRepresentation"]["productAndEquipmentLimits"]["salMassUnit"] = update_data[keys[i]]
        if keys[i] in data and keys[i] != "residueLimit":
            data[keys[i]] = update_data[keys[i]]
    payload = {"data": data, "reason": "Test Automation"}
    return payload
