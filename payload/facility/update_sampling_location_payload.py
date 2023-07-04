
# For now we are using properties value as hardcoded for unit test cases
# TODO But for scenario properties should not be hardcoded try to make it dynamic so that dont it need to hardcoded
def create_update_new_assessment_attribute(attribute_name):
    payload = {
        "name": attribute_name,
        "description": "Automation Test",
        "reason": "test",
        "type": "Yes/No",
        "properties": [
            {
                "label": "Yes",
                "rating": 1
            },
            {
                "label": "No",
                "rating": 0
            }]
    }

    return {"payload": payload}


def create_update_auto_selection_policies_payload_for_post(contact_type, atr_id, atr_property_id):
    payload = {
        "contactType": contact_type,
        "minLocations": 1,
        "operator": "or",
        "reason": "Test",
        "samplingSubPolicies": [{

            "operator": "or",
            "samplingSubPolicyAttributeMapping": [{
                "attributeId": atr_id,
                "attributePropertyId": atr_property_id,
                "comparator": "EqualTo"
            }]
        }]

    }

    return {"payload": payload}

