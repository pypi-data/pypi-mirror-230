"""
Module for AGClient class.

AGClient class contians all the methods to interact with the AG server like creating a session, uploading results, etc.
It also contains methods to get the budget, privacy odometer, etc.

"""

import requests
import json
from typing import Union
import warnings
import pandas as pd
from .magics.magics import AGMagic
from .enclave_client.oblv_client import get_oblv_client, oblv_client
from .config import config
from .models.models import AGServerInfo
from .utils.print_request_id import print_request_id
import onnx
from io import BytesIO
import time
import base64

def login(
    user_id: str,
    user_secret: str,
    competition: str = None,
    dataset: str = None,
):
    """
    Login to the AG server and get the client objects.

    Parameters:
        ag_client_id (str): The AG client ID.
        ag_client_secret (str): The AG client secret.
        competition (str, optional): The competition dataset ID.
        dataset (str, optional): The dataset ID.

    Returns:
        AGClient: The AGClient object.

    Raises:
        ConnectionError: If there is an error while creating the client.
    """
    try:
        return AGClient(user_id, user_secret, competition, dataset)
    except Exception as err:
        print(
            f"Login failed. Please verify the competition name and your credentials. If issue persists, contact support. Error: {str(err)}"
        )


class AGClient:
    """
    AGClient class to interact with the AG server for competitions as well as accessing datasets for functionalities like creating a session, uploading competition submissions, downloading metadata, etc.
    """

    oblv_enclave: oblv_client.Enclave
    session_id: str

    def __init__(self, ag_client_id, ag_client_secret, competition=None, dataset=None):
        """
        Initialize AGClient class and check for mock headers if MockClient.

        Parameters:
            ag_client_id (str): The AG client ID.
            ag_client_secret (str): The AG client secret.
            competition (str, optional): The competition dataset ID. Defaults to None.
            dataset (str, optional): The dataset ID. Defaults to None.

        Raises:
            ConnectionError: If there is an error while connecting to the server.
        """

        # Fetch latest PCRs from AG Server, and verify client version
        try:
            self._validate_server_info()
        except Exception as err:
            warnings.warn(f"Error while validating server info: {str(err)}")

        self.oblv_enclave = get_oblv_client(ag_client_id, ag_client_secret)
        self.headers = {}

        # Create an AG session
        self.connect(competition=competition, dataset=dataset)
        print(f"Connected to Antigranular server session id: {str(self.session_id)}, the session will time out if idle for 60 minutes")

        try:
            res = AGMagic.load_ag_magic()
        except Exception as ex:
            print(
                "Error loading %%ag magic functions, you might not be able to use cell magics as intended: ",
                str(ex),
            )

        AGMagic.load_oblv_client(self.oblv_enclave, self.session_id)

    def _validate_server_info(self) -> None:
        """
        Get the PCR values to use from antigranular.com.
        PCRs are fed to the enclave client for PCR validation along with client version check.
        """
        try:
            res = requests.get(config.AG_SRV_INFO_URL)
        except Exception as err:
            warnings.warn(f"Error fetching server AG information: {str(err)}")
        else:
            if res.status_code != 200:
                warnings.warn(
                    f"Error while getting PCR values from antigranular.com status code: {res.status_code} message: {res.text}"
                )
            ag_server_info = AGServerInfo.parse_raw(res.text)

            # Update the PCR values from the response
            config.AG_PCRS = ag_server_info.AG_PCRs.dict()
            from . import __version__

            if __version__ not in ag_server_info.supported_clients:
                warnings.warn(
                    f"Antigranular client version {__version__} not in supported clients list shared by the server, please update antigranular client to the latest version."
                )

    def connect(self, dataset: str = "", competition: str = "") -> None:
        """
        Connect to the AG server and create a session.

        Parameters:
            dataset (str, optional): The dataset ID. Defaults to "".
            competition (str, optional): The competition dataset ID. Defaults to "".

        Raises:
            ConnectionError: If there is an error while connecting to the server.
        """
    
        if not (dataset or competition):
            raise ValueError("dataset name or competition name must be provided.")
        if competition and dataset:
            raise ValueError(
                "Both competition and dataset cannot be passed. Please pass only one of them."
            )
        try:
            if competition:
                res = self._exec(
                    "POST",
                    "/start-session",
                    headers=self.headers,
                    json={
                        "session_type": "competition",
                        "type_identifier": competition,
                    },
                )
            if dataset:
                res = self._exec(
                    "POST",
                    "/start-session",
                    headers=self.headers,
                    json={"session_type": "dataset", "type_identifier": dataset},
                )
        except Exception as err:
            raise ConnectionError(f"Error calling /start-session: {str(err)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    print_request_id(f"Error while starting a new session in enclave status code: {res.status_code} message: {res.text}", res)
                )
            self.session_id = json.loads(res.text)["session_id"]
            self.__load_utils()

    def __load_utils(self) -> None:
        code = "from ag_utils import load_dataset, ag_print, export, submit_predictions"
        try:
            self.__session_execute(code)
        except Exception as e:
            raise ConnectionError(f"Error loading utils: {str(e)}")

    def interrupt_kernel(self) -> dict:
        """
        Interrupt the current session.

        Returns:
            dict: The interrupt kernel response.

        Raises:
            ConnectionError: If there is an error while calling /interrupt-kernel.
            requests.exceptions.HTTPError: If there is an error while fetching the interrupt kernel.
        """
        try:
            res = self._exec(
                "POST",
                "/sessions/interrupt-kernel",
                headers=self.headers,
                json={"session_id": self.session_id},
            )
        except Exception as e:
            raise ConnectionError(f"Error calling /terminate-session: {str(e)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    print_request_id(f"Error while fetching the terminate-session, HTTP status code: {res.status_code}, message: {res.text}", res)
                )
            return json.loads(res.text)

    def terminate_session(self) -> dict:
        """
        Terminate the current session.

        Returns:
            dict: The terminate session response.

        Raises:
            ConnectionError: If there is an error while calling /terminate-session.
            requests.exceptions.HTTPError: If there is an error while fetching the terminate session.
        """
        try:
            res = self._exec(
                "POST",
                "/sessions/terminate-session",
                headers=self.headers,
                json={"session_id": self.session_id},
            )
        except Exception as e:
            raise ConnectionError(f"Error calling /terminate-session: {str(e)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    print_request_id(f"Error while fetching the terminate-session, HTTP status code: {res.status_code}, message: {res.text}", res)
                )
            return json.loads(res.text)

    def privacy_odometer(self) -> dict:
        """
        Get the privacy odometer.

        Returns:
            dict: The privacy odometer.

        Raises:
            ConnectionError: If there is an error while calling /privacy_odometer.
            requests.exceptions.HTTPError: If there is an error while fetching the privacy odometer.
        """
        try:
            res = self._exec(
                "GET",
                "/sessions/privacy_odometer",
                params={"session_id": self.session_id},
                headers=self.headers,
            )
        except Exception as e:
            raise ConnectionError(f"Error calling /privacy_odometer: {str(e)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    print_request_id(f"Error while fetching the privacy odometer, HTTP status code: {res.status_code}, message: {res.text}", res)
                )
            return json.loads(res.text)

    def submit_predictions(self, data) -> dict:
        """
        Submit predictions to the AG server.

        Parameters:
            data (pd.DataFrame): The predictions dataframe.

        Returns:
            dict: The submit predictions response.
        """
        try:
            res = self._exec(
                "POST",
                "/sessions/submit_predictions",
                json={"session_id": self.session_id, "data": data.to_json()},
                headers=self.headers,
            )
        except Exception as e:
            raise ConnectionError(f"Error calling /submit_predictions: {str(e)}")
        else:
            if res.status_code != 200:
                if res.status_code == 500:
                    return print_request_id(res.text, res)
                raise requests.exceptions.HTTPError(
                    print_request_id(f"Error: {res.text}", res)
                )
            return json.loads(res.text)

    def __get_output(self) -> None:
        """
        Retrieves the code execution output from the Antigranular server.
        """
        count = 1

        while True:
            if count > config.AG_EXEC_TIMEOUT:
                print("Error : AG execution timeout.")
                break
            try:
                res = self._exec(
                    "GET",
                    "/sessions/output",
                    params={"session_id": self.session_id}
                )
            except Exception as err:
                raise ConnectionError(
                    f"Error during code execution on AG Server: {str(err)}"
                )
            if res.status_code != 200:
                raise HTTPError(
                    f"Error while requesting AG server for output, HTTP status code: {res.status_code}, message: {res.text}"
                )
            kernel_messages = json.loads(res.text)["output_list"]
            for message in kernel_messages:
                if message["msg_type"] == "status":
                    if message["content"]["execution_state"] == "idle":
                        return
                elif message["msg_type"] == "stream":
                    if message["content"]["name"] == "stdout":
                        print("Output:", message["content"]["text"])
                    elif message["content"]["name"] == "stderr":
                        print(message["content"]["text"])

                elif message["msg_type"] == "error":
                    tb_str = ""
                    for tb in message["content"]["traceback"]:
                        tb_str += tb

                    print(tb_str)
                    return
            time.sleep(1)
            count += 1
    
    def __session_execute(self, code) -> None:
        if not code:
            raise ValueError("Code must be provided.")
        try:
            res = self._exec(
                "POST",
                "/sessions/execute",
                headers=self.headers,
                json={"session_id": self.session_id, "code": code},
            )
        except Exception as err:
            raise ConnectionError(f"Error calling /sessions/execute: {str(err)}")
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"Error while executing the provided compute operation in the enclave status code: {res.status_code} message: {res.text}"
                )
            self.__get_output()

    def __load(self, name, data_type: str) -> None:
        if data_type == "model":
            code = f"from ag_utils import load_model\n{name} = load_model('{name}')"
        if data_type == "dataframe":
            code = f"from ag_utils import load_dataframe\n{name} = load_dataframe('{name}')"

        try:
            self.__session_execute(code)
        except Exception as e:
            raise ConnectionError(f"Error calling /sessions/execute: {str(e)}")


    def private_import(self, name: str, data=None, path=None) -> None:
        """
        Load a user provided model or dataset into the AG server.

        Parameters:
            name (str): The name to use for the model or dataset.
            data (onnx.ModelProto, pd.DataFrame): The data to load. Defaults to None.
            path (str, optional): The path to the model, the external data should be under the same directory of the model. Defaults to None.
        Returns:
            None
        """
        if not name.isidentifier():
            raise ValueError("Invalid variable name, please provide a valid variable name")
        if not (data is None or path is None):
            raise ValueError("Both data and path cannot be provided, please provide only one of them")
        try:
            if isinstance(data, onnx.ModelProto):
                try:
                    onnx.checker.check_model(data)
                    onnx_bytes_io = BytesIO()
                    onnx_bytes_io.seek(0)
                    onnx.save_model(data, onnx_bytes_io)
                except Exception as e:
                    raise ValueError(f"Invalid ONNX model: {str(e)}")
                res = self._exec(
                    "POST",
                    "/sessions/cache_model",
                    headers=self.headers,
                    json={"session_id": self.session_id, "name": name, "model": base64.b64encode(onnx_bytes_io.getvalue()).decode()},
                )
                data_type = "model"
            elif path:
                if not path.endswith(".onnx"):
                    raise ValueError("Invalid model file format, only .onnx files are supported")
                try:
                    onnx_model = onnx.load(path)
                    onnx.checker.check_model(onnx_model)
                except Exception as e:
                    raise ValueError(f"Invalid ONNX model: {str(e)}")
                res = self._exec(
                    "POST",
                    "/sessions/cache_model",
                    headers=self.headers,
                    json={"session_id": self.session_id, "name": name, "model": base64.b64encode(open(path, "rb").read()).decode()},
                )
                data_type = "model"
            elif isinstance(data, pd.DataFrame):
                res = self._exec(
                    "POST",
                    "/sessions/cache_data",
                    headers=self.headers,
                    json={"session_id": self.session_id, "data": data.to_json(), "name": name},
                )
                data_type = "dataframe"
            else:
                raise ValueError("Either a DataFrame, ONNX model, or path must be provided")
        except Exception as e:
            raise ConnectionError(f"Error: {str(e)}")
        
        else:
            if res.status_code != 200:
                raise requests.exceptions.HTTPError(
                    print_request_id(f"Error: {res.text}", res)
                )
            else:
                print(f"{data_type} cached to server, loading to kernel...")
                self.__load(name, data_type)

    # Use Oblv Client enclave to make HTTP requests
    def _exec(self, method, endpoint, data="", json={}, params={}, headers={}, files=None):
        """
        Execute an HTTP request using the Oblv Client enclave.

        Parameters:
            method (str): The HTTP method.
            endpoint (str): The endpoint URL.
            data (Any, optional): The request data. Defaults to "".
            json (Any, optional): The request JSON. Defaults to None.
            params (dict, optional): The request parameters. Defaults to None.
            headers (dict, optional): The request headers. Defaults to None.

        Returns:
            Response: The HTTP response.

        Raises:
            ValueError: If the method is not supported by the client.
        """
        url_endpoint = f"{self.oblv_enclave.url}:{self.oblv_enclave.port}{endpoint}"
        if method == "GET":
            r = self.oblv_enclave.get(
                url_endpoint,
                json=json,
                params=params,
                headers=headers,
            )
        elif method == "POST":
            r = self.oblv_enclave.post(
                url_endpoint, json=json, params=params, headers=headers, files=files
            )
        elif method == "PUT":
            r = self.oblv_enclave.put(
                url_endpoint, json=json, params=params, headers=headers
            )
        elif method == "DELETE":
            r = self.oblv_enclave.delete(
                url_endpoint, json=json, params=params, headers=headers
            )
        else:
            raise ValueError(f"{method} not supported by client")
        return r
