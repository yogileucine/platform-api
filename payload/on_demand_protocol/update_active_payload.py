

def create_update_active_payload(response_direct,response_indirect):
    equipments_direct = response_direct["result"]["equipments"]
    equipments_indirect = response_indirect["result"]["equipments"]
    payload ={
        "showWorstCaseEvaluation": False,
        "direct": {
            "equipments":equipments_direct,
            "policy": "productWise"
        },
        "indirect": {
            "equipments": equipments_indirect,
            "policy": "policyBased"
        }
    }
    return {"payload":payload}

def create_active_direct_update_empty_limit_payload(response_direct,response_indirect):
    equipments_direct = response_direct["result"]["equipments"]
    equipments_indirect = response_indirect["result"]["equipments"]
    payload ={
        "showWorstCaseEvaluation": False,
        "direct": {
            "equipments":equipments_direct,
            "policy": "custom"
        },
        "indirect": {
            "equipments": equipments_indirect,
            "policy": "policyBased"
        }
    }
    return {"payload":payload}

def create_active_indirect_update_empty_limit_payload(response_direct,response_indirect):
    equipments_direct = response_direct["result"]["equipments"]
    equipments_indirect = response_indirect["result"]["equipments"]
    payload ={
        "showWorstCaseEvaluation": False,
        "direct": {
            "equipments":equipments_direct,
            "policy": "productWise"
        },
        "indirect": {
            "equipments": equipments_indirect,
            "policy": "custom"
        }
    }
    return {"payload":payload}

def create_active_update_only_direct_limit_payload(response_direct,response_indirect):
    equipments_direct = response_direct["result"]["equipments"]
    equipments_indirect = response_indirect["result"]["equipments"]
    payload ={
        "showWorstCaseEvaluation": False,
        "direct": {
            "equipments":equipments_direct,
            "policy": "productWise"
        },
        "indirect": {
            "equipments": equipments_indirect,
        }
    }
    return {"payload":payload}