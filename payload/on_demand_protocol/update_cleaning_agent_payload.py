

def create_update_cleaning_agent_payload(response_direct,response_indirect):
    equipments_direct = response_direct["result"]["equipments"]
    equipments_indirect = response_indirect["result"]["equipments"]
    payload ={
        "showWorstCaseEvaluation": False,
        "direct": {
            "equipments":equipments_direct,
            "policy": "cleaningAgentSal"
        },
        "indirect": {
            "equipments": equipments_indirect,
            "policy": "policyBased"
        }
    }
    return {"payload":payload}

def create_update_cleaning_agent__direct_only_payload(response_direct,response_indirect):
    equipments_direct = response_direct["result"]["equipments"]
    equipments_indirect = response_indirect["result"]["equipments"]
    payload ={
        "showWorstCaseEvaluation": False,
        "direct": {
            "equipments":equipments_direct,
            "policy": "cleaningAgentSal"
        },
        "indirect": {
            "equipments": equipments_indirect,
        }
    }
    return {"payload":payload}

def create_cleaning_agent_direct_update_empty_limit_payload(response_direct,response_indirect):
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

def create_cleaning_agent_indirect_update_empty_limit_payload(response_direct,response_indirect):
    equipments_direct = response_direct["result"]["equipments"]
    equipments_indirect = response_indirect["result"]["equipments"]
    payload ={
        "showWorstCaseEvaluation": False,
        "direct": {
            "equipments":equipments_direct,
            "policy": "policyBased"
        },
        "indirect": {
            "equipments": equipments_indirect,
            "policy": "custom"
        }
    }
    return {"payload":payload}