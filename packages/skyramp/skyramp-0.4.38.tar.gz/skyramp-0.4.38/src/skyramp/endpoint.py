"""
Contains helpers for interacting with Skyramp endpoints.
"""

from abc import ABC, abstractmethod

import os
import ctypes
import json
import yaml

from skyramp.utils import _library, _call_function

class _Endpoint(ABC):
    """
    Base class for endpoints. This should not be used for instantiation.
    """

    @abstractmethod
    def __init__(self, endpoint_data: str) -> None:
        try:
            endpoint = json.loads(endpoint_data)
            self.services = endpoint["services"]
            self.endpoint = endpoint["endpoints"][0]

            for method in self.endpoint["methods"]:
                method["proxy"] = True

            self.response_values = endpoint["responseValues"]

            self.mock_description = {
                "services": self.services,
                "endpoints": [self.endpoint],
                "responseValues": self.response_values
            }
        except:
            raise Exception("failed to parse endpoint data")

    def mock_method(self, method_name: str, mock_object: str, dynamic: bool = False) -> None:
        """
        Adds the given mock_data blob to the method name for this endpoint.
        """
        for method in self.endpoint["methods"]:
            if method_name not in [method.get("name"), method.get("type")]:
                continue

            response_name = method["responseValue"]
            method.pop("proxy", None)

            for response_value in self.response_values:
                if response_value["name"] != response_name:
                    continue

                if dynamic:
                    response_value["javascriptPath"] = mock_object
                    response_value.pop("blob", None)
                else:
                    response_value["blob"] = mock_object["responseValue"]["blob"]
                    response_value.pop("javascriptPath", None)
                return

        raise Exception(f"method {method_name} not found")

    def mock_method_from_file(self, method_name: str, file_name: str) -> None:
        """
        Uses the given mock data from a provided file, and associates it with the
        corresponding method_name for this endpoint.
        """
        _, file_ext = os.path.splitext(file_name)

        try:
            with open(file_name) as file:
                file_contents = file.read()
        except:
            raise Exception(f"failed to open file: {file_name}")

        dynamic = False

        if file_ext == ".json":
            data = json.loads(file_contents)
        elif file_ext in [".yaml", ".yml"]:
            data = yaml.safe_load(file_contents)
        elif file_ext == ".js":
            dynamic = True
            data = file_name
        else:
            raise Exception(
                f"unsupported file format: {file_ext}. Only JSON, YAML, and JS are supported"
            )

        return self.mock_method(method_name=method_name, mock_object=data, dynamic=dynamic)

    def write_mock_configuration_to_file(self, alias: str) -> None:
        """
        Persists (as a file to be used by Skyramp) all of the mock configurations
        for this endpoint.

        alias: The name of the networking alias that will be used to reach this endpoint. 
        For example, it can be the Kubernetes service name or the Docker alias name.
        """
        try:
            yaml_content = yaml.dump(self.mock_description)
        except:
            raise Exception("failed to convert mock description to YAML")

        func = _library.writeMockDescriptionWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        restype = ctypes.c_char_p

        _call_function(func, argtypes, restype, [yaml_content.encode(), alias.encode()])


class _GrpcEndpoint(_Endpoint):
    """
    Represents an endpoint of a gRPC based service.
    """

    def __init__(self, name: str, service: str, port: int, pb_file: str) -> None:
        """
        name: Name of the endpoint
        service: The service name to associate with this endpoint
        port: Port number where the endpoint will be reached
        pb_file: Protobuf file with definitions corresponding to this endpoint
        """
        func = _library.newGrpcEndpointWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        restype = ctypes.c_char_p

        output = _call_function(
            func,
            argtypes,
            restype,
            [name.encode(), service.encode(), port, pb_file.encode()],
            True,
        )

        super().__init__(output)


class _RestEndpoint(_Endpoint):
    """
    Represents an endpoint of a REST based service.
    """

    def __init__(
        self, name: str, openapi_tag: str, port: int, openapi_file: str
    ) -> None:
        """
        name: name of the endpoint
        openapi_tag: (optional) tag to filter an OpenAPI file
        port: Port number where the endpoint will be reached
        openapi_file: (optional) OpenAPI file with definitions corresponding to this endpoint
        """
        func = _library.newRestEndpointWrapper
        argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
        restype = ctypes.c_char_p

        output = _call_function(
            func,
            argtypes,
            restype,
            [name.encode(), openapi_tag.encode(), port, openapi_file.encode()],
            True,
        )

        super().__init__(output)
