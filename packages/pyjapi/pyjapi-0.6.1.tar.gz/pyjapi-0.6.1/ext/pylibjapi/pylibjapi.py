#!/usr/bin/env python3
import json
import logging as log
import os
import signal
import socket
import sys
from copy import deepcopy
from shutil import copyfile
from types import SimpleNamespace
from typing import Dict, List, Union

HOST = os.getenv("LIBJAPI_HOST", "localhost")
PORT = int(os.getenv("LIBJAPI_PORT", 1234))

SEPARATOR = 40 * "-"
"""Width of seperator printed between client messages."""

STYLE = SimpleNamespace(
    reset="\x1b[0m",
    bold="\x1b[1m",
    dim="\x1b[2m",
    danger="\x1b[91;1m",
)
"""https://en.wikipedia.org/wiki/ANSI_escape_code"""

# global socket and connection object for easy access
sock = None
conn = None
sockfile = None

# global JSON File object
jsonfileobj = None

jsonfilepath = ""

# shutdown / reboot flag to evaluate after sending a response
shutdown_flag = None


def japi_main():
    global sock, conn, loglevel, sockfile

    # SIGINT signal handler to shut down the server
    signal.signal(signal.SIGTERM, clean_exit)

    # startup code
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow socket to be used right away after it has been used by another program
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind((HOST, PORT))
    except OSError:
        # port binding failed
        print(
            STYLE.danger + f"⚠️  Error: {HOST}:{PORT} is already in use!" + STYLE.reset
        )
        clean_exit()
    sock.listen()

    # working path setup - change into japi directory
    # this makes the program work independently from the path from which it is started
    japi_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(japi_dir)

    # overwrite *_data.tmp.json file according to *_data.json
    copyfile("state_data.json", "state_data.tmp.json")
    copyfile("register_data.json", "register_data.tmp.json")

    print(f"\n" + "🚀 " + STYLE.bold + "Starting - Let's go!" + STYLE.reset)
    print(SEPARATOR)

    try:
        while True:
            log.info("Listening on %s:%d... ", HOST, PORT)
            conn, addr = sock.accept()  # waits here until client connects
            sockfile = conn.makefile(mode="rw")
            log.info("Client connected at %s:%d... ", addr[0], addr[1])

            with conn:
                # connection was found - for now, only one connection is accepted
                while True:
                    # receive until error -> None is returned in this case
                    try:
                        msgs = receive()
                    except TimeoutError:
                        # try again
                        break
                    if msgs is not None:
                        try:
                            respond(msgs)
                        except BrokenPipeError:
                            print("Error: Broken pipe!")
                            break
                    else:
                        # try again
                        break
    except KeyboardInterrupt:
        clean_exit(hide_escape=True)


def receive() -> Union[List[Dict], None]:
    """Receive data using global connection object.

    Split if multiple commands arrive at once

    Returns:
        japi requests or `None` on error (e.g. if loading as JSON fails)

    """
    global conn, sockfile

    received_data = sockfile.readline()

    requests = []
    log.debug("Raw received data: %s", str(received_data))

    # empty string received - connection was terminated
    # Note: This empty string results when websocketd terminates the WebSocket connection
    if received_data == "":
        log.info("Connection has been terminated")
        return None

    # in some cases multiple commands arrive as one string, delimited by '\n' (newline)
    # split them into a list, filter out emptystring (most likely because of '\n at the end')
    # for each, create a json object and put it into the "requests" list
    msgs = list(filter(None, received_data.split("\n")))
    for msg in msgs:
        try:
            request = json.loads(msg)
            requests.append(request)
        except ValueError as err:
            log.warning("JSON Error! Received data: %s", str(received_data))
            log.warning("Error: %s", str(err))
            return None
        if loglevel < log.WARN:
            print(SEPARATOR)
        print("▶️ ", json.dumps(request))

    return requests


def respond(requests: list):
    """Individually handle (just set) and respond (all) to the given list of requests."""

    global jsonfileobj
    global jsonfilepath
    global shutdown_flag

    # load data from tmp JSON file

    for request in requests:
        # keep track of success
        # Responding succeeds if we reach the end without errors
        # default values
        error_state = {
            "success": True,
            "error_type": "UNKNOWN_ERROR",
            "error_msg": "Fatal: An unknown error occurred",
        }

        # response template with default values
        response = {
            "japi_response": "invalid request",
            "args": {},
            "data": {},
        }  # yapf: disable

        request_cmd = request.get("japi_request")
        if request_cmd is None:
            error_msg = f"Error: {request} is not a JAPI request!"
            set_japi_error(error_state, "COMMAND_ERROR", error_msg)
        else:
            # mirror request to response
            response["japi_response"] = request_cmd

        if "japi_request_no" in request:
            # copy request japi_request_no to response, if it exists
            response["japi_request_no"] = request["japi_request_no"]

        args = request.get("args")
        if args:
            # mirror args if not empty
            _args = deepcopy(args)
            # update with original args - work with copied args
            response.update({"args": args})
        else:
            # empty args - remove from response
            _args = response.pop("args", {})

        data_entry = handle_request(request_cmd, _args, error_state)

        if data_entry is None:
            if error_state["success"] == False:
                response["data"]["JAPI_RESPONSE"] = "failure"
                # put error type and msg into response
                response["data"][error_state["error_type"]] = error_state["error_msg"]
        else:
            response["data"].update(data_entry)

        # determine if the file was opened with the last request
        if jsonfilepath != "":
            with open(jsonfilepath, "w") as jsonfile:
                # update JSON with new data
                json.dump(jsonfileobj, jsonfile, indent=2)

        response = json.dumps(response)
        print(f"◀️  {response}")
        print(SEPARATOR)

        if conn is not None:
            # not called from test_pylibjapi
            # format to NDJSON syntax (\n is needed!)
            conn.send((response + "\n").encode("utf-8"))

        if shutdown_flag:
            clean_exit(reboot=shutdown_flag == "reboot")


def handle_request(
    request_cmd: dict, args: dict, error_state: dict
) -> Union[Dict, None]:
    """Handle incoming requests.

    Determine name of JSON file to open, then open it.
    Handle given request dict, for example by updating the jsonfileobj according to set requests.
    Update error_state dict with occuring errors.

    Returns:
        Updated data entry (if request was successful, None otherwise)

    """

    global jsonfileobj
    global jsonfilepath
    global shutdown_flag

    if not error_state["success"]:
        # unsuccessful already - no reason to proceed
        return None

    # => data keys exist for get and set requests
    if request_cmd.startswith("get_") or request_cmd.startswith("set_"):
        # remove prefix ("get_" / "set_")
        # Example: "get_temperature" -> "temperature" as "temperature"
        # is the data key in the JSON file
        data_key = request_cmd[request_cmd.find("_") + 1 :]

        # decide which file to open
        if data_key == "converter_register":
            jsonfilepath = "register_data.tmp.json"
        else:
            jsonfilepath = "state_data.tmp.json"

        with open(jsonfilepath, "r") as jsonfile:
            jsonfileobj = json.load(jsonfile)

        # get value to data key - a dict is returned
        data_value = jsonfileobj.get(data_key)

        if data_value is None:
            # error - data_key not found
            error_msg = f"Error: Data Key not found: {data_key}"
            set_japi_error(error_state, "COMMAND_ERROR", error_msg)
            return None

        # get entry corresponding to given args
        data_entry = find_data_entry(data_value, args, error_state)
        if data_entry is not None:
            if request_cmd.startswith("set_"):
                # !! currently there is no check for value validity !!
                set_args = args.get("set")
                if set_args is None:
                    # Error - all set requests are required to have a set attribute
                    error_msg = (
                        f"Error: Set request with no set attribute: set_{data_key}"
                    )
                    set_japi_error(error_state, "COMMAND_ERROR", error_msg)
                    return None

                for set_arg in set_args:
                    # set request - set data according to args
                    if data_entry.get(set_arg) is None:
                        # set_arg not found in data entry
                        error_msg = f"Error: Set request key not found: {set_arg}"
                        set_japi_error(error_state, "COMMAND_ERROR", error_msg)
                        return None
                    # update entry
                    data_entry[set_arg] = set_args[set_arg]

            return data_entry
        else:
            # error in find_data_entry - handling was unsuccessful
            # error_state has been updated
            return None

    else:
        # not a get/set request - individual case by case handeling

        # for these requests we don't open a file
        jsonfilepath = ""

        if request_cmd == "test_connection":
            # test_connection - no data, just success
            return {}
        elif request_cmd == "trigger_pattern":
            return {"JAPI_MESSAGE": "Pattern triggered successfully "}
        elif request_cmd == "stop_pattern":
            return {"JAPI_MESSAGE": "Pattern stopped successfully "}
        elif request_cmd == "trigger_syncflag_reset":
            return {"JAPI_MESSAGE": "Sync Flag reset successful"}
        elif request_cmd == "trigger_sync_dac":
            return {"JAPI_MESSAGE": "ESI Sync successful"}
        elif request_cmd == "trigger_reset_dac":
            return {"JAPI_MESSAGE": "DAC reset successful"}
        elif request_cmd == "update_board":
            # emulate board update - no error handeling for the moment
            return {
                "JAPI_MESSAGE": "Update was installed successfully. "
                "To apply changes, system needs to be rebooted."
            }

        elif request_cmd == "shutdown_board":
            # emulate shutdown - shutdown after sending response
            log.info("Received command shutdown_board - shutting down")
            shutdown_flag = "shutdown"
            return {}

        elif request_cmd == "reboot_board":
            # emulate reboot - restart after sending response
            log.info("Received command reboot_board - restarting")
            shutdown_flag = "reboot"
            return {}

        elif request_cmd == "japi_pushsrv_list":
            return {"services": ["push_temperature"]}

        elif request_cmd == "japi_pushsrv_subscribe":
            return {"japi_response": "success"}

        elif request_cmd == "japi_pushsrv_unsubscribe":
            return {"japi_response": "success"}

        else:
            # unknown command -> error
            error_msg = f"Error: Command not found: {request_cmd}"
            set_japi_error(error_state, "COMMAND_ERROR", error_msg)
            return None


def find_data_entry(data_value: dict, args: dict, error_state: dict):
    """Find data entry for *data_value* corresponding to *args* recursively.

    Args:
        data_value: the dict in which the entry is to be found
        args: the args to match
        error_state: error state dict to keep track of error messages

    Returns:
        data_value corresponding to args (if available), None otherwise

    """

    # iterate over args - find one of the args in the key list
    for arg in args.keys():
        # set is not in here and will not be matched
        if arg in data_value.keys():
            # arg found in keys - go further
            # get value from arg key - str cast because they may exist as other types
            # Example: str(args["DEVICE"]) == "1"
            arg_value = str(args[arg])

            # with the new japi spec, this should not occur
            if type(data_value[arg]) is not dict:
                # exit condition #1 - arg was matched but value is not a dict
                # -> no need to go deeper, data_value is what we are looking for
                # the last arg is not really matched, but the corresponding data point
                # is returned for use in set request handling
                return data_value

            # get new values for matched arg - this line is important ;)
            # Example: data_value["DEVICE"].get("1") returns new dict
            # for device "1"
            new_values = data_value[arg].get(arg_value)

            if new_values is None:
                error_msg = (
                    f"error: key *{str(args[arg])}* not found in data_value[{arg}]"
                )
                set_japi_error(error_state, "VALUE_ERROR", error_msg)
                return None

            # arg handled successfully - pop it
            args.pop(arg)
            # recursive call - match remaining args in deeper layers
            return find_data_entry(new_values, args, error_state)
    else:
        # arg not found in for iteration
        if len(args) == 0:
            # exit conditon #2 - no (more) args - get request
            return data_value
        elif len(args) == 1 and "set" in args.keys():
            return data_value
        else:
            # something went wrong :( - this shouldn't happen
            log.error("fatal error: data_value is %s", data_value)
            assert False


def clean_exit(*args, **kwargs):
    """Close socket and exit program.

    Matches arbitrary args and kwargs, so it can be used as signal handler function.

    Args:
        reboot (bool): start new pylibjapi instance before closing this one (default: False)

    """
    if kwargs.get("hide_escape"):
        # erase escape character (^C) from terminal output
        print("\b\b  \b\b", flush=True, end="")
    global sock

    sock.close()

    if loglevel < log.WARN:
        print(SEPARATOR)
    if kwargs.get("reboot"):
        print("🔄 " + STYLE.bold + "Rebooting - Will be right back!" + STYLE.reset)
        # replace current process with new pylibjapi process
        os.execvp("./pylibjapi.py", ["./pylibjapi.py"])
    else:
        print("👋 " + STYLE.bold + "Terminating - Good bye!" + STYLE.reset)
        sys.exit()


def set_japi_error(error_state: dict, error_type: str, error_msg: str):
    """
    Update the error_state dict with success = False and the given error type and message.
    Said error message is also logged.
    """

    error_state["success"] = False
    error_state["error_type"] = error_type
    error_state["error_msg"] = error_msg
    print(STYLE.danger + "⚠️  " + error_msg + STYLE.reset)


def help():
    print(f"Usage: {sys.argv[0]} [-h HOST] [-p PORT] [-v]")


if __name__ == "__main__":
    try:
        if "--help" in sys.argv:
            help()
            sys.exit(0)
        if "-h" in sys.argv:
            HOST = sys.argv[sys.argv.index("-h") + 1]
        if "-p" in sys.argv:
            PORT = int(sys.argv[sys.argv.index("-p") + 1])

        loglevel = (
            log.DEBUG
            if "-vv" in sys.argv
            else log.INFO
            if "-v" in sys.argv
            else log.WARN
        )
        log.basicConfig(
            stream=sys.stdout,
            level=loglevel,
            format=f"📝 {STYLE.dim}%(message)s{STYLE.reset}",
        )

        japi_main()
    except (IndexError, ValueError):
        help()
        sys.exit(1)
