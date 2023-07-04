
def create_update_intermediate_payload(direct_data, data):
    direct_data["result"].update({"policy": data})
    payload = {"direct": direct_data["result"]}
    return payload
