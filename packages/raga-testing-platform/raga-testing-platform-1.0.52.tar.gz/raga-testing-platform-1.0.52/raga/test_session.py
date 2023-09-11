import json
import sys
import time
import requests
from raga.validators.test_session_validation import TestSessionValidator
from raga.utils import HTTPClient
from raga.utils import read_raga_config, get_config_value

class TestSession():
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    ACCESS_KEY = "raga_access_key_id"
    SECRET_KEY = "raga_secret_access_key"


    def __init__(self, project_name: str, run_name: str, u_test=False, host=None, config_data=None, access_key=None, secret_key=None):
        if config_data is None and (access_key is None or secret_key is None or host is None):
            config_data = read_raga_config()
        
        self.api_host = host if host else get_config_value(config_data, 'default', 'api_host')
        self.raga_access_key_id = access_key if access_key else get_config_value(config_data, 'default', self.ACCESS_KEY)
        self.raga_secret_access_key = secret_key if secret_key else get_config_value(config_data, 'default', self.SECRET_KEY)
    
        self.project_name = TestSessionValidator.validate_project_name(project_name)
        self.run_name = TestSessionValidator.validate_run_name(run_name)
        self.http_client = HTTPClient(self.api_host)
        self.test_list = []
        self.added = False

        self.token = None
        self.project_id = None
        self.experiment_id = None
        if not u_test:
            self.initialize()


    def initialize(self):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                self.token = self.create_token()
                self.project_id = self.get_project_id()
                self.experiment_id = self.create_experiment()
                break  # Exit the loop if initialization succeeds
            except requests.exceptions.RequestException as exception:
                print(f"Network error occurred: {str(exception)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
            except KeyError as exception:
                print(f"Key error occurred: {str(exception)}")
                sys.exit() # No need to retry if a KeyError occurs
            except ValueError as exception:
                print(f"Value error occurred: {str(exception)}")
                sys.exit() # No need to retry if a ValueError occurs
            except Exception as exception:
                print(f"An unexpected error occurred: {str(exception)}")
                sys.exit()  # No need to retry if an unexpected error occurs

    def add(self, payload):
        if not isinstance(payload, dict) or not payload:
            raise ValueError("payload must be a non-empty dictionary.")
        if payload.get("test_type") == "ab_test":
            if payload.get("type") == "unlabelled":
                payload["api_end_point"] =  "api/experiment/test/unlabelled"
            if payload.get("type") == "labelled":
                payload["api_end_point"] = "api/experiment/test/labelled"

        if payload.get("test_type") == "drift_test":
            payload["api_end_point"] =  "api/experiment/test/drift"
        if payload.get("test_type") == "cluster":
            payload["api_end_point"] =  "api/experiment/test/fma"
        if payload.get("test_type") == "labelling_quality":
            payload["api_end_point"] =  "api/experiment/test/labelling-quality"
        self.test_list.append(payload)
        self.added = True

    def run(self):
        # Check if already added
        if not self.added:
            raise ValueError("add() is not called. Call add() before run().")
        if not len(self.test_list):
            raise ValueError("Test not found.")
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                for test_payload in self.test_list:
                    api_end_point = test_payload.get("api_end_point")
                    test_payload.pop("api_end_point")
                    test_payload.pop("test_type")
                    res_data = self.http_client.post(api_end_point, data=test_payload, headers={"Authorization": f'Bearer {self.token}'})
                    if not isinstance(res_data, dict):
                        raise ValueError("Invalid response data. Expected a dictionary.")
                    # print(res_data.get('data', ''))
                    self.test_list = []
                break  # Exit the loop if initialization succeeds
            except requests.exceptions.RequestException as exception:
                print(f"Network error occurred: {str(exception)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
                self.test_list = []
            except KeyError as exception:
                print(f"Key error occurred: {str(exception)}")
                self.test_list = []
                sys.exit() # No need to retry if a KeyError occurs
            except ValueError as exception:
                print(f"Value error occurred: {str(exception)}")
                self.test_list = []
                sys.exit() # No need to retry if a ValueError occurs
            except Exception as exception:
                print(f"An unexpected error occurred: {str(exception)}")
                self.test_list = []
                sys.exit()  # No need to retry if an unexpected error occurs

    def create_token(self):
        """
        Creates an authentication token by sending a request to the Raga API.

        Returns:
            str: The authentication token.

        Raises:
            KeyError: If the response data does not contain a valid token.
        """
        res_data = self.http_client.post(
            "api/token",
            {"accessKey": self.raga_access_key_id, "secretKey": self.raga_secret_access_key},
        )
        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")
        token = res_data.get("data", {}).get("token")
        if not token:
            raise KeyError("Invalid response data. Token not found.")
        return token


    def get_project_id(self):
        """
        Get project id by sending a request to the Raga API.

        Returns:
            str: The ID of the project.

        Raises:
            KeyError: If the response data does not contain a valid project ID.
            ValueError: If the response data is not in the expected format.
        """
        res_data = self.http_client.get(
            "api/project",
            params={"name": self.project_name},
            headers={"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")

        project_id = res_data.get("data", {}).get("id")

        if not project_id:
            raise KeyError("Invalid response data. project ID not found.")
        return project_id



    def create_experiment(self):
        """
        Creates an experiment by sending a request to the Raga API.

        Returns:
            str: The ID of the created experiment.

        Raises:
            KeyError: If the response data does not contain a valid experiment ID.
            ValueError: If the response data is not in the expected format.
        """
        res_data = self.http_client.post(
            "api/experiment",
            {"name": self.run_name, "projectId": self.project_id},
            {"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")

        experiment_id = res_data.get("data", {}).get("id")

        if experiment_id is None:
            raise KeyError("Invalid response data. Experiment ID not found.")
        return experiment_id
