# libjapi-demo

This project demonstrates the usage of libjapi. Please take a look at demo.c
for the application and test.py for the client part.

## Concepts

libjapi provides two communication concepts. The first one is a synchronous request/response concept. The second one is a push service that delivers messages to the client asynchronously after it was subscribed. Both concepts are demonstrated in this demo project in the example of *get_temperature* and *push_temperature()*.
For more in-depth details consult the <a href="http://ks-ip-lib.git01.iis.fhg.de/software/libjapi/doc/html/index.html">documentation</a>.

## Prerequisites
* [CMake version 3.6](https://cmake.org/)
* [Python version 3.6](https://www.python.org/)
* [json-c](https://github.com/json-c/json-c)

## Setup

Perform the following steps to setup and run the demonstration:

First, clone the project including libjapi as a submodule.

    git clone --recurse-submodules git@git01.iis.fhg.de:ks-ip-lib/software/libjapi-demo.git

Next, build libjapi-demo.

    cd libjapi-demo/
    mkdir build
    cd build
    cmake ../
    make

Finally, call

    make run-static

to build and start the server on localhost port 1234.

Note: For the next step python3 needs to be installed.

Back in the libjapi-demo directory start the python client script in a separate tab with

    ./test.py

The server can manage multiple clients. Try and run multiple clients simultaneously.

To end the client(s) send a `CTRL-C`. Same for the server.

Troubleshooting: If cmake retrieves version 2.8, try `cmake3 ../`

## Examples

### Synchronous request/response

In this simple example a application (demo.c) delivers the temperature in
degree celsius or kelvin via JSON.

Example output:

```json
{
  "japi_response": "get_temperature",
  "data": {
    "temperature": 300.0,
    "unit": "kelvin"
  }
}
```

or

```json
{
  "japi_response": "get_temperature",
  "data": {
    "temperature": 27.0,
    "unit": "celsius"
  }
}
```

To retrieve the temperature a JSON request has to be send to the application:

```json
{
  "japi_request": "get_temperature",
  "args": {
    "unit": "kelvin",
  }
}
```

or

```json
{
  "japi_request": "get_temperature",
  "args": {
    "unit": "celsius",
  }
}
```

### Asynchronous push services

In addition to synchronous request/response messages the sample application (demo.c) pushes the temperature periodically via JSON messages.

Example output:

```json
{
  "japi_pushsrv": "push_temperature",
  "data": {
    "temperature": 33.894183
  }
}
{
  "japi_pushsrv": "push_temperature",
  "data": {
    "temperature": 37.794255
  }
}
{
  "japi_pushsrv": "push_temperature",
  "data": {
    "temperature": 35.646425
  }
}
```

#### Subscribe to push service

To retrieve the temperature it's needed to subscribe to the push service *push_temperature*. The request for that should look like this:

```json
{
  "japi_request": "japi_pushsrv_subscribe",
  "args": {
    "service": "push_temperature"
  }
}
```

If the request is successful there should be a response with the key *success* and value *true*:

```json
{
  "japi_response": "japi_pushsrv_subscribe",
  "data": {
    "service": "push_temperature",
    "success": true
 }
}
```

From this point on, until the push service is unsubscribed, the client will receive push messages, without further synchronous requests.

#### Unsubscribe from push service

To stop the push messages, the push service *push_temperature* needs to be unsubscribed:

```json
{
  "japi_request": "japi_pushsrv_unsubscribe",
  "args": {
    "service": "push_temperature"
  }
}
```

If the response contains an *success* *true*, the server will stop to push messages to the client:

```json
{
  "japi_response": "japi_pushsrv_unsubscribe",
  "data": {
    "service": "push_temperature",
    "success": true
  }
}
```
