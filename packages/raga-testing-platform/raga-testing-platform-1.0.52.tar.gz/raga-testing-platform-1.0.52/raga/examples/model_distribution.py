import ast
import csv
import pathlib
import re
from raga import *
import pandas as pd
import json
import datetime
import random

def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def csv_parser(csv_file):
    pd_df = pd.read_csv(csv_file)
    dr = []
    for index, row in pd_df.iterrows():
        df = {}
        try:
            for index_r, column_name in enumerate(pd_df.columns):
                if column_name == "ModelA Inference":
                    pass
                elif column_name == "ModelB Inference":
                    classification = ImageClassificationElement()
                    element = row[column_name]
                    conf = ast.literal_eval(element)
                    classification.add("live", conf['live'])
                    df[column_name] = classification

                elif column_name == "Ground Truth":
                    classification = ImageClassificationElement()
                    element = row[column_name]
                    conf = ast.literal_eval(element)
                    classification.add("live", conf['live'])
                    df[column_name] = classification
                    
                elif column_name == "ImageVectorsM1":
                    ImageVectorsM1 = ImageEmbedding()
                    element = row[column_name]
                    element = json.loads(element)
                    for embedding in element:
                        ImageVectorsM1.add(Embedding(embedding))
                    df[column_name] = ImageVectorsM1

                elif column_name == "TimeOfCapture":
                    element = row[column_name]
                    df[column_name] = TimeStampElement(get_timestamp_x_hours_ago(index_r))
                elif column_name == "ImageId":
                    element = row[column_name]
                    df[column_name] = element
                    df["ImageUri"] = StringElement(f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/spoof/{element}")
                    df[column_name] = StringElement(element)
                elif column_name == "SourceLink":
                    element = row[column_name]
                    file_path = f"/Users/manabroy/Downloads/retail dataset/spoof/{element.split('/')[-1]}"
                    df[column_name] = StringElement(file_path)

        except Exception as e:
                print(e)
                continue
        if index == 10:
            break
        dr.append(df)
    return pd.DataFrame(dr)


# print(csv_parser("./assets/signzy_df.csv"))
pd_data_frame = pd.DataFrame(csv_parser("./assets/signzy_df.csv"))


# data_frame_extractor(pd_data_frame).to_csv("./assets/signzy_df_test_10.csv", index=False)



schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("ModelB Inference", ImageClassificationSchemaElement(model="modelB"))
schema.add("Ground Truth", ImageClassificationSchemaElement(model="GT"))

run_name = f"run-30-aug-failure-mode-analysis-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


test_session = TestSession(project_name="testingProject", run_name=run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

raga_dataset = Dataset(test_session=test_session, name="model-distribution-v8", data=pd_data_frame, schema=schema)
raga_dataset.load()




model_exe_fac = ModelExecutorFactory().getModelExecutor(test_session=test_session, model_name="Signzy Embedding Model", version=3)

df = model_exe_fac.execute(init_args={"device": "cpu"},execution_args={"input_columns":{"img_paths":"SourceLink"}, "output_columns":{"embedding":"ImageEmbedding"}}, data_frame=raga_dataset)

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageEmbedding", ImageEmbeddingSchemaElement(model="signzyModel"))

raga_dataset.load(schema=schema)





# model_exe_fac = ModelExecutorFactory().getModelExecutor(test_session=test_session, model_name="model 1", version="1")

# model_exe_fac.execute(init_args={},execution_args={"input_columns":{"img_path":"SourceLink"}, "output_columns":{"detections":"ModelCInference"}}, data_frame=raga_dataset)

# schema = RagaSchema()
# schema.add("ImageId", PredictionSchemaElement())
# schema.add("ModelCInference", InferenceSchemaElement(model="modelC"))

# raga_dataset.load(schema=schema)





# model_exe_fac = ModelExecutorFactory().getModelExecutor(test_session=test_session, model_name="model 1", version="1")

# model_exe_fac.execute(init_args={},execution_args={"input_columns":{"img_path":"SourceLink"}, "output_columns":{"detections":"ModelDInference"}}, data_frame=raga_dataset)

# schema = RagaSchema()
# schema.add("ImageId", PredictionSchemaElement())
# schema.add("ModelDInference", InferenceSchemaElement(model="modelD"))

# raga_dataset.load(schema=schema)