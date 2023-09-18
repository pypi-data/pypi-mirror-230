#!/usr/bin/env python3
"""Generate initial data for get/set_adcregister requests.

If a certain pattern of data is required, the generateRegisterValue Function
can be modified accordingly. Then simply run the script to generate a new
register_data.json file

"""

import json

# according to ADC/DAC JAPI Interface Specification
MAX_REGISTER_ADC = 0x0b2c
MAX_REGISTER_DAC = 0x061c

# template to start from
register_data = {"converter_register": {"DEVICE": {"1": {"REGISTER": {}}, "2": {"REGISTER": {}}}}}


def generateRegisterValue(register):
    # maybe think of a good way to generate values
    # for now just return the address again
    return register


for elem in register_data["converter_register"]["DEVICE"].values():
    # fill attribute "REGISTER"
    for addr in range(MAX_REGISTER_ADC + 1):
        value = {str(addr): {"VALUE": generateRegisterValue(addr)}}
        elem["REGISTER"].update(value)

with open("register_data.json", 'w') as f:
    json.dump(register_data, f, indent=2)
