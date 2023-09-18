#!/usr/bin/env python3
import shutil

import pylibjapi


def testing():
    """testing various pylibjapi features - used for developement"""

    shutil.copyfile("state_data.json", "state_data.tmp.json")

    requests = [
        {"japi_request": "get_controlbits", "args": {"DEVICE": 1, "CONTROLBIT": 1}},
        {"japi_request": "get_clock_config"},
        {"japi_request": "get_temperature", "args": {"DEVICE": "ADC1"}},
        {"japi_request": "get_chip_revision", "args": {"DEVICE": 2}},
        {"japi_request": "get_fubar", "args": {"DEVICE": 2, "UNIT": "KELVIN", "CONTROLBIT": 2}},
        {"japi_request": "get_fubar", "args": {"DEVICE": 2, "UNIT": "KELVIN", "CONTROLBIT": 2, "TEMPERATURE": "456"}},
        # set request testing

        # old syntax - should fail
        {"japi_request": "set_clock_config", "args": {"REFCLOCK": 30, "SAMPLECLOCK": 5.5, "CLOCKCHAIN": True}},
        {"japi_request": "set_fubar", "args": {"DEVICE": 2, "UNIT": "KELVIN", "CONTROLBIT": 2, "TEMPERATURE": 4567}},
        # new syntax - should succeed
        {"japi_request": "set_clock_config", "args": {"set": {"REFCLOCK": 30, "SAMPLECLOCK": 5.5, "CLOCKCHAIN": True}}},
        {"japi_request": "set_fubar", "args": {"DEVICE": 2, "UNIT": "KELVIN", "CONTROLBIT": 2, "set": {"TEMPERATURE": 4567}}},
        {"japi_request": "set_controlbits", "args": {"DEVICE": 1, "CONTROLBIT": 1, "set": {"FUNCTIONALITY": "timestamp"}}, "japi_request_no": "fubar"},
        # set request with invalid set key
        {"japi_request": "set_controlbits", "args": {"DEVICE": 1, "CONTROLBIT": 1, "set": {"INVALID_KEY": "timestamp"}}, "japi_request_no": "fubar"},

        {"japi_request": "set_fubar", "args": {"DEVICE": 2, "UNIT": "KELVIN", "CONTROLBIT": "invalid_key", "TEMPERATURE": 4567}},
        {"jaajasdfasdf": "get_chip_revision", "args": {"DEVICE": 2}},
        {"japi_request": "get_bullshitrequest", "args": {"DEVICE": 2}},
        # other
        {"japi_request": "foobullshitrequest", "args": {"DEVICE": 2}},
        {"japi_request": "test_connection"},
    ]  # yapf: disable

    for request in requests:
        print(f"<-- {request}")
        pylibjapi.respond([request])


if __name__ == "__main__":
    testing()
