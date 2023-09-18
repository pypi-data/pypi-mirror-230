import json
import logging as log
import typing as t


class JAPIMessage(dict):
    def __init__(self, init_data=None):
        dict.__init__(self, init_data)

    @property
    def name(self) -> str:
        raise NotImplementedError()

    @property
    def args(self) -> t.Dict[str, t.Any]:
        return self.get("args")

    def dumps(self, *args, **kwargs) -> str:
        return json.dumps(self, *args, **kwargs)


class JAPIResponse(JAPIMessage):
    """A Japi response message."""

    def __init__(self, init_data=None):
        super().__init__(init_data)
        assert "japi_response" in self

    @property
    def name(self) -> str:
        return self["japi_response"]

    @property
    def data(self) -> t.Dict[str, t.Any]:
        return self.get("data")

    @property
    def success(self) -> bool:
        return self.get("data", {}).get("JAPI_RESPONSE") == "success"


class JAPIRequest(JAPIMessage):
    """A JAPI request message."""

    def __init__(self, init_data):
        JAPIMessage.__init__(self, init_data=init_data)
        log.debug(f"JAPIRequest({init_data})")
        assert "japi_request" in self
