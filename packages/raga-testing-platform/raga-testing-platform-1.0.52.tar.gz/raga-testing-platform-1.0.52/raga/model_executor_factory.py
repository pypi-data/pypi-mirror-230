import logging
import os
import subprocess
import sys
import requests
from urllib.parse import urlparse, unquote


from raga.dataset import Dataset
from raga.exception import RagaException
from raga.test_session import TestSession
from raga.utils.raga_config_reader import format_python_versions, get_machine_platform, get_python_version, get_config_file_path

logger = logging.getLogger(__name__)

RAGA_REPO_PATH = ".raga/raga_repo"
MODEL_PATH = "models"

class ModelExecutorFactoryException(RagaException):
    pass

class PlatformError(RagaException):
    pass

class PythonVersionError(RagaException):
    pass

class WheelFileInstallationError(RagaException):
    pass

class ModelExecutorError(RagaException):
    pass

class ModelExecutor:
    def __init__(self, executor, wheel_path):
        self.executor = executor
        self.wheel_file_path = wheel_path

    def execute(self, init_args, execution_args, data_frame:Dataset):
        try:
            self.executor.initialise(init_args)
            columns = list(execution_args.get('input_columns').values())
            df, image_id_column = data_frame.get_data_frame(columns)
            df = self.executor.run(data_frame=df, input_args=execution_args['input_columns'], output_args=execution_args['output_columns'])
            data_frame.set_data_frame(df)
            uninstall_wheel(self.wheel_file_path)
            return df
        except Exception as exc:
            logger.exception(exc)
            uninstall_wheel(self.wheel_file_path)
        
        

class ModelExecutorFactory:
    def __init__(self):
        pass

    @staticmethod
    def getModelExecutor(test_session:TestSession, model_name:str, version:int):
        if not isinstance(model_name, str) or not model_name:
            raise ModelExecutorFactoryException("model_name is required and must be a non-empty string.")
        if not isinstance(version, int) or not version:
            raise ModelExecutorFactoryException("version is required and must be a non-empty int.")
        
        model_api_client = ModelAPIClient(test_session)
        
        model_id = model_api_client.get_model_id(model_name=model_name)
        model_version = model_api_client.get_version_by_version(model_id=model_id, version=version)

        model_wheel =  model_validation(model_version, model_name, RAGA_REPO_PATH, MODEL_PATH)
        wheel_path = download_model(model_wheel)
        install_wheel(wheel_path)
        try:
            from raga_models.executor import Executor
            executor = Executor()
            return ModelExecutor(executor, wheel_path)
        except ImportError as ie:
            raise ModelExecutorError("Model executor lib not found")
    

    
class ModelAPIClient:
    def __init__(self, test_session=TestSession):
        self.http_client = test_session.http_client

        self.token = test_session.token
        self.project_id = test_session.project_id
        self.experiment_id = test_session.experiment_id

    def get_model_id(self, model_name):
        """
        Get project id by sending a request to the Raga API.

        Returns:
            str: The ID of the project.

        Raises:
            KeyError: If the response data does not contain a valid project ID.
            ValueError: If the response data is not in the expected format.
        """
        res_data = self.http_client.get(
            "api/model",
            data={"modelName": model_name, "projectId":self.project_id},
            headers={"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")

        model_id = res_data.get("data", {}).get('id')

        if not model_id:
            raise KeyError("Invalid response data. model ID not found.")
        return model_id
    

    def get_version_by_version(self, model_id, version):
        """
        Get project id by sending a request to the Raga API.

        Returns:
            str: The ID of the project.

        Raises:
            KeyError: If the response data does not contain a valid project ID.
            ValueError: If the response data is not in the expected format.
        """
        res_data = self.http_client.get(
            "api/models-version",
            data={
                "modelId": model_id,
                "version":version
                },
            headers={"Authorization": f'Bearer {self.token}'},
        )

        if not isinstance(res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")

        data = res_data.get("data", {})

        if not data:
            raise KeyError("Invalid response data.")
        return data
    

def execution_validation(init_args: dict, execution_args: dict, dataset: Dataset):
    if not isinstance(dataset, Dataset):
        raise ModelExecutorFactoryException("Invalid dataset.")
    
    if not isinstance(init_args, dict):
        raise ModelExecutorFactoryException("Invalid init_args.")
    
    if not isinstance(execution_args, dict):
        raise ModelExecutorFactoryException("Invalid execution_args.")
    
    if 'input_cols' not in execution_args:
        raise ModelExecutorFactoryException("execution_args is missing the 'input_cols' key.")
    
    if 'output_cols' not in execution_args:
        raise ModelExecutorFactoryException("execution_args is missing the 'output_cols' key.")
    
    if not all(isinstance(col, str) for col in execution_args.get("input_cols", [])):
        raise ModelExecutorFactoryException("input_cols should be a list of strings.")
    
    if not all(isinstance(col, str) for col in execution_args.get("output_cols", [])):
        raise ModelExecutorFactoryException("output_cols should be a list of strings.")
    
    return 1


def model_validation(model, model_name, RAGA_REPO_PATH, MODEL_PATH):
    supportedPythonVersions = model.get("supportedPythonVersions")
    supportedPlatforms = model.get("supportedPlatforms")
    local_platform = get_machine_platform()
    local_python_version = get_python_version()
    if supportedPythonVersions and supportedPlatforms:
        supportedPlatforms = [platform.strip() for platform in supportedPlatforms.split(',')]
        supportedPythonVersions = format_python_versions(supportedPythonVersions)
        if local_platform not in supportedPlatforms:
            raise PlatformError(f"The model version does does not support your platform. Please try other model version. Your platform {local_platform}. Model platform version {supportedPlatforms}.")
        if local_python_version not in supportedPythonVersions:
            raise PythonVersionError(f"The python version does does not support your python. Please try other model version. Your version {local_python_version}. Model Python version{supportedPythonVersions}.")
    else:
        raise ModelExecutorFactoryException("Model platform or python version not found.")
    if not model.get("wheelFile"):
        raise ModelExecutorFactoryException("Wheel file not found.")

    raga_models_path = os.path.join(get_config_file_path(RAGA_REPO_PATH), f"{MODEL_PATH}/{model_name}/{model.get('version')}")
    if not os.path.exists(raga_models_path):
        os.makedirs(raga_models_path)
    model["raga_models_path"] = raga_models_path
    whl_files = os.listdir(raga_models_path)
    if any(file.endswith('.whl') for file in whl_files): 
        model["whl_path"] = raga_models_path
    return model

def get_wheel_file_name(model):
    wheelFileUrl = model.get("wheelFile")
    parts = wheelFileUrl.split()
    file_path = parts[-1]
    parsed_file_path = urlparse(file_path)
    return unquote(parsed_file_path.path.split("/")[-1])

def download_model(model):
    wheel_file = model.get("wheelFile")
    if model.get("whl_path"):
        model_wheel = os.path.join(model.get("whl_path"), get_wheel_file_name(model))
    else:
        model_wheel = os.path.join(model.get('raga_models_path'),get_wheel_file_name(model))
        with requests.get(wheel_file, stream=True) as response:
            response.raise_for_status()
            with open(model_wheel, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    return model_wheel


def install_wheel(package_name):
    try:
        logger.debug(f"PIP INSTALLING {package_name}")
        subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True, capture_output
        =True)
        logger.debug(f"PIP INSTALLED {package_name}")
    except subprocess.CalledProcessError as e:
        raise WheelFileInstallationError(f"Failed to install {package_name}. Error: {e}")

def uninstall_wheel(package_name):
    try:
        logger.debug(f"PIP UNINSTALLING {package_name}")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", package_name, "-y"], check=True, capture_output=True)
        logger.debug(f"PIP UNINSTALLED {package_name}")
    except subprocess.CalledProcessError as e:
        raise WheelFileInstallationError(f"Failed to uninstall {package_name}. Error: {e}")