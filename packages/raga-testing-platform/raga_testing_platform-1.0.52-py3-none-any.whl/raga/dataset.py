import json
import os
import sys
import time
import requests
from typing import Optional
import pandas as pd
from raga.exception import RagaException
from raga.raga_schema import RagaSchema
from raga.validators.dataset_validations import DatasetValidator
from raga.dataset_creds import DatasetCreds
from raga import TestSession
import logging
import zipfile
from raga.utils import get_file_name, delete_files, upload_file, create_csv_and_zip_from_data_frame, data_frame_extractor, make_arg, on_upload_success, on_upload_failed, check_key_value_existence

logger = logging.getLogger(__name__)

class DatasetException(RagaException):
    pass
class Dataset():
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __init__(
        self,
        test_session:TestSession,
        name: str,
        data: (pd.DataFrame, str),
        schema: Optional[RagaSchema] = None,
        creds: Optional[DatasetCreds] = None,
        u_test = False
    ):
        self.test_session = test_session
        self.name = DatasetValidator.validate_name(name)
        self.creds = DatasetValidator.validate_creds(creds)
        self.csv_file = f"experiment_{test_session.experiment_id}_{self.name}.csv"
        self.zip_file = f"experiment_{test_session.experiment_id}_{self.name}.zip"
        self.dataset_id = None
        if not u_test:
            self.dataset_id = self.create_dataset()
            if self.creds and self.dataset_id:
                self.create_dataset_creds()
        self.dataset_file_id = None
        self.data_set_top_five_rows = {}
        self.raga_dataset = data
        self.raga_extracted_dataset = None
        self.raga_schema = schema
        self.dataset_schema_columns = None
        if not data.empty and isinstance(data, pd.DataFrame) and schema and isinstance(schema, RagaSchema):
            self.initialize(data, schema)


    def initialize(
        self,
        data = None, 
        schema = None, 
        format= None,
        model_name = None,
        inference_col_name= None,
        embedding_col_name= None):
        # Validate and process the data argument
        if data is not None:
            if isinstance(data, str):
                # Assume it's a file path
                self.load_labels_from_file(
                data,
                format,
                model_name,
                inference_col_name,
                embedding_col_name
            )
            elif isinstance(data, pd.DataFrame):

                if not data.empty:
                    # Validate and process the schema argument
                    if schema is not None:
                        if isinstance(schema, RagaSchema):
                            # Use the provided schema object
                            self.dataset_schema_columns = schema.columns
                            # Use the provided DataFrame
                            self.raga_extracted_dataset = data_frame_extractor(data)
                            # print(json.dumps(dataset_column))

                        else:
                            raise ValueError("Invalid schema argument. Expected an instance of RagaSchema.")
                else:
                    raise ValueError("Empty DataFrame data argument.")
            else:
                raise ValueError("Invalid data argument. Expected a DataFrame or a file path.")
    
    def load(self, data:Optional[pd.DataFrame]=None, schema:Optional[RagaSchema]=None, ):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                if isinstance(data, pd.DataFrame) and not data.empty and schema and isinstance(schema, RagaSchema):
                    self.load_data_frame(data, schema.columns)
                elif (not isinstance(data, pd.DataFrame) or data.empty) and schema and isinstance(schema, RagaSchema):
                    self.load_data_frame(self.raga_extracted_dataset, schema.columns)
                else:
                    self.load_data_frame(self.raga_extracted_dataset, self.dataset_schema_columns)
                print("Data loaded successful!")
                break  # Exit the loop if initialization succeeds
            except requests.exceptions.RequestException as e:
                print(f"Network error occurred: {str(e)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
            except KeyError as e:
                if os.getenv("DEBUG"):
                    logger.exception(e)
                print(f"Key error occurred: {str(e)}")
                sys.exit(1)# No need to retry if a KeyError occurs 
            except ValueError as e:
                if os.getenv("DEBUG"):
                    logger.exception(e)
                print(f"Value error occurred: {str(e)}")
                sys.exit(1) # No need to retry if a ValueError occurs
            except Exception as e:
                if os.getenv("DEBUG"):
                    logger.exception(e)
                print(f"An unexpected error occurred: {str(e)}")
                sys.exit(1) # No need to retry if an unexpected error occurs
    
        

    def load_static(
        self,
        filePath = None,
        schema = None,
        format= None,
        model_name = None,
        inference_col_name= None,
        embedding_col_name= None
    ):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                from raga import RagaSchema

                if isinstance(schema, RagaSchema):
                    # Use the provided schema object
                    dataset_column = schema.columns
                    # Use the provided DataFrame
                    # self.load_data_frame(data_frame_extractor(data), dataset_column)
                    self.load_static_data_frame(filePath, dataset_column)
                    # print(json.dumps(dataset_column))

                else:
                    raise ValueError("Invalid schema argument. Expected an instance of RagaSchema.")
                print("Data loaded successful!")
                break  # Exit the loop if initialization succeeds
            except requests.exceptions.RequestException as e:
                print(f"Network error occurred: {str(e)}")
                retries += 1
                if retries < self.MAX_RETRIES:
                    print(f"Retrying in {self.RETRY_DELAY} second(s)...")
                    time.sleep(self.RETRY_DELAY)
            except KeyError as e:
                print(f"Key error occurred: {str(e)}")
                sys.exit(1)# No need to retry if a KeyError occurs 
            except ValueError as e:
                print(f"Value error occurred: {str(e)}")
                sys.exit(1) # No need to retry if a ValueError occurs
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
                sys.exit(1) # No need to retry if an unexpected error occurs


    def load_data_frame(self, data_frame:pd.DataFrame, dataset_column):
        """
        Loads the data frame, creates a CSV file, zips it, and uploads it to the server.
        """
        column_list = data_frame.columns.to_list()
        for col in dataset_column:
            if col.get("customerColumnName") not in column_list:
                raise ValueError(f"Raga Schema Error: Column name `{col.get('customerColumnName')}` not found in provided Data Frame. {column_list}")
        logger.debug("Loading Data Frames")
        if not check_key_value_existence(dataset_column, 'type', 'imageName'):
            raise ValueError("Missing required field 'ImageId' in the schema. Please provide 'ImageId' using a PredictionSchemaElement instance.")
        create_csv_and_zip_from_data_frame(data_frame, self.csv_file, self.zip_file)
        signedUploadPath, filePath = self.get_pre_signed_s3_url(self.zip_file)

        upload_file(
            signedUploadPath,
            self.zip_file,
            success_callback=on_upload_success,
            failure_callback=on_upload_failed,
        )
        delete_files(self.csv_file, self.zip_file)

        self.dataset_file_id = self.create_dataset_load_definition(filePath, "csv", dataset_column)
        self.notify_server()
    
    # def run_validation_on_one_row(data_frame:pd.DataFrame, dataset_column):


    def load_static_data_frame(self, filePath, dataset_column):
        """
        Loads the data frame, creates a CSV file, zips it, and uploads it to the server.
        """
        logger.debug("Loading Data Frames")

        if not check_key_value_existence(dataset_column, 'type', 'imageName'):
            raise ValueError("Missing required field 'ImageId' in the schema. Please provide 'ImageId' using a PredictionSchemaElement instance.")

        self.dataset_file_id = self.create_dataset_load_definition(filePath, "csv", dataset_column)
        self.notify_server()


    def load_labels_from_file(
        self,
        path_to_file,
        format,
        model_name,
        inference_col_name,
        embedding_col_name
    ):
        """
        Loads labels from a file, zips it, and uploads it to the server.

        Args:
            path_to_file (str): The path to the file containing labels.
            format (str): The format of the labels.
            model_name (str): The name of the model.
            inference_col_name (str): The name of the inference column.
            embedding_col_name (str): The name of the embedding column.

        Raises:
            ValueError: If any required parameter is missing.
        """
        required_params = [
            "format",
            "model_name",
            "inference_col_name"
        ]
        for param in required_params:
            if not locals().get(param):
                raise ValueError(
                    f"{param.capitalize().replace('_', ' ')} is required.")
        file_dir = os.path.dirname(path_to_file)
        file_name_without_ext, file_extension, file_name = get_file_name(
            path_to_file)
        zip_file_name = os.path.join(file_dir, file_name_without_ext + ".zip")
        with zipfile.ZipFile(zip_file_name, "w") as zip_file:
            zip_file.write(path_to_file, file_name)
        signedUploadPath, filePath  = self.get_pre_signed_s3_url(
            file_name_without_ext + ".zip")
        upload_file(
            signedUploadPath,
            zip_file_name,
            success_callback=on_upload_success,
            failure_callback=on_upload_failed,
        )
        if os.path.exists(zip_file_name):
            os.remove(zip_file_name)
            logger.debug("Zip file deleted")
        else:
            logger.debug("Zip file not found")

        arguments = make_arg(model_name, inference_col_name, embedding_col_name)

        self.dataset_file_id = self.create_dataset_load_definition(filePath, format, arguments)
        self.notify_server()
    
    def column_validate(self, file_dir, format, inference_col_name, embedding_col_name):
        if format == 'coco':
            with open(file_dir, 'r') as f:
                json_data = json.load(f)
            if json_data.get(inference_col_name) is None:
                raise ValueError(f"Raga Schema Error: Column name `{inference_col_name}` not found in provided coco file. {list(json_data.keys())}")
            if json_data.get(embedding_col_name) is None:
                raise ValueError(f"Raga Schema Error: Column name `{embedding_col_name}` not found in provided coco file. {list(json_data.keys())}")
        return True

    def head(self):
        res_data = self.test_session.http_client.get(
            f"api/dataset/{self.dataset_id}/data",
            headers={"Authorization": f'Bearer {self.test_session.token}'},
        )
        if not res_data or 'data' not in res_data or 'rows' not in res_data['data'] or 'columns' not in res_data['data']:
            raise ValueError("Record not found!")
        
        print(self.filter_head(res_data.get('data', {}).get('rows', {}), res_data.get('data', {}).get('columns', {})))

    def filter_head(self, rows, columns):
        pd_data = pd.DataFrame(rows)
        columns_temp = []
        for col in columns:
            columns_temp.append(col.get("columnName"))
        return pd_data.get(columns_temp)
    
    def get_pre_signed_s3_url(self, file_name: str):
        """
        Generates a pre-signed URL for uploading the file to an S3 bucket.

        Args:
            file_name (str): The name of the file.

        Returns:
            str: The pre-signed S3 URL.

        Raises:
            ValueError: If the file name is missing.
        """
        res_data = self.test_session.http_client.get(
            "api/dataset/uploadpath",
            None,{"experimentId": self.test_session.experiment_id, "fileName": file_name, "contentType":"application/zip"},
            {"Authorization": f'Bearer {self.test_session.token}'},
        )
        logger.debug("Pre-signed URL generated")
        print("Pre-signed URL generated")
        return res_data["data"]["signedUploadPath"], res_data["data"]["filePath"]


    def notify_server(self):
        """
        Notifies the server to load the dataset with the provided experiment ID and data definition.
        """
        res_data = self.test_session.http_client.post(
            "api/experiment/load-data",
            {"experimentId": self.test_session.experiment_id, "datasetFileId": self.dataset_file_id},
            {"Authorization": f'Bearer {self.test_session.token}'},
        )
        print(res_data.get('data', ''))
        return res_data

    def create_dataset(self):
        if not self.test_session.project_id:
            raise ValueError("Project ID is required.")
        if not self.test_session.token:
            raise ValueError("Token is required.")

        res_data = self.test_session.http_client.post(
            "api/dataset",
            {"name": self.name, "projectId": self.test_session.project_id, "experimentId":self.test_session.experiment_id},
            {"Authorization": f'Bearer {self.test_session.token}'},
        )

        if not res_data or 'data' not in res_data or 'id' not in res_data['data']:
            raise ValueError("Failed to create dataset.")

        return res_data['data']['id']

    def create_dataset_creds(self,):
        if not self.dataset_id:
            raise ValueError("Dataset ID is required.")
        if not self.test_session.token:
            raise ValueError("Token is required.")

        data = {
            "datasetId": self.dataset_id,
            "storageService": "s3",
            "json": {'arn': self.creds.arn}
        }
        res_data = self.test_session.http_client.post(
            "api/dataset/credential",
            data,
            {"Authorization": f'Bearer {self.test_session.token}'},
        )

        if not res_data or 'data' not in res_data or 'id' not in res_data['data']:
            raise ValueError("Failed to create dataset credentials.")

        return res_data['data']['id']
    
    def create_dataset_load_definition(self, filePath: str, type: str, arguments: dict):
        payload = {
            "datasetId": self.dataset_id,
            "filePath": filePath,
            "type": type,
            "arguments": arguments
        }

        res_data = self.test_session.http_client.post(
            "api/dataset/definition", payload,
            {"Authorization": f'Bearer {self.test_session.token}'},
        )
        return res_data.get('data',{}).get('id')

    def get_data_frame(self, columns:list):
        image_id_column = next((item['customerColumnName'] for item in self.raga_schema.columns if item['type'] == 'imageName'), None)
        if image_id_column not in columns:
            columns.append(image_id_column)
        
        missing_columns = [col for col in columns if col not in self.raga_extracted_dataset.columns]
        if not missing_columns:
            return self.raga_extracted_dataset[columns], image_id_column
        else:
            missing_columns_str = ', '.join(missing_columns)
            raise DatasetException(f"The following columns do not exist in the DataFrame: {missing_columns_str}")
    
    def set_data_frame(self, data_frame:pd.DataFrame):
        print(type(data_frame))
        self.raga_extracted_dataset = data_frame
        return 1