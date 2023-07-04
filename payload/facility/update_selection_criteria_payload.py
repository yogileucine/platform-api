import string
import random

def create_update_selection_criteria_payload():
    name_length=7
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=name_length))
    payload = {
                "name": name,

                "rules": [
                    {
                        "type": "ProductProperty",
                        "step": 1,
                        "property": "pde"
                    }
                ],
                "reason": "test11",
            }
    return {"payload": payload}