import ast
import pandas as pd
import json
import datetime
from raga.dataset import Dataset
from raga.model_executor_factory import ModelExecutorFactory

from raga.raga_schema import (Embedding, 
                              FeatureSchemaElement, 
                              ImageClassificationElement, 
                              ImageClassificationSchemaElement, 
                              ImageEmbedding, 
                              ImageEmbeddingSchemaElement, 
                              ImageUriSchemaElement, 
                              PredictionSchemaElement, 
                              RagaSchema, 
                              StringElement, 
                              TimeOfCaptureSchemaElement, 
                              TimeStampElement)
from raga.test_session import TestSession


def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def img_url(x):
    return StringElement(f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/spoof/{x}")

def model_a_inference(row):
    classification = ImageClassificationElement()
    try:
        confidence = ast.literal_eval(row['ModelA Inference'])
        classification.add("live", confidence.get('live'))
    except Exception:
        classification.add("live", 0)
    return classification


def model_b_inference(row):
    classification = ImageClassificationElement()
    try:
        confidence = ast.literal_eval(row['ModelB Inference'])
        classification.add("live", confidence.get('live'))
    except Exception:
        classification.add("live", 0)
    return classification


def model_gt_inference(row):
    classification = ImageClassificationElement()
    try:
        confidence = ast.literal_eval(row['Ground Truth'])
        classification.add("live", confidence.get('live'))
    except Exception:
        classification.add("live", 0)
    return classification

def image_vectors_m1(row):
    image_vectors = ImageEmbedding()
    for embedding in json.loads(row['ImageVectorsM1']):
        image_vectors.add(Embedding(embedding))
    return image_vectors


def csv_parser(csv_file):
    df = pd.read_csv(csv_file).head(15)
    data_frame = pd.DataFrame()
    data_frame["ImageId"] = df["ImageId"].apply(lambda x: StringElement(x))
    data_frame["ImageUri"] = df["ImageId"].apply(lambda x: img_url(x))
    data_frame["TimeOfCapture"] = df.apply(lambda row: TimeStampElement(get_timestamp_x_hours_ago(row.name)), axis=1)
    data_frame["Reflection"] = df.apply(lambda row: StringElement("Yes"), axis=1)
    data_frame["Overlap"] = df.apply(lambda row: StringElement("No"), axis=1)
    data_frame["CameraAngle"] = df.apply(lambda row: StringElement("Yes"), axis=1)
    data_frame["SourceLink"] = df["SourceLink"].apply(lambda x: StringElement(f"/Users/manabroy/Downloads/retail dataset/spoof/{x.split('/')[-1]}"))
    data_frame["ModelA Inference"] = df.apply(model_a_inference, axis=1)
    data_frame["ModelB Inference"] = df.apply(model_b_inference, axis=1)
    data_frame["Ground Truth"] = df.apply(model_gt_inference, axis=1)
    data_frame["ImageVectorsM1"] =  df.apply(image_vectors_m1, axis=1)
    return data_frame


pd_data_frame = csv_parser("./assets/signzy_df.csv")


# data_frame_extractor(pd_data_frame).to_csv("./assets/signzy_df_test_10.csv", index=False)



schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("ModelA Inference", ImageClassificationSchemaElement(model="modelA"))
schema.add("ModelB Inference", ImageClassificationSchemaElement(model="modelB"))
schema.add("Ground Truth", ImageClassificationSchemaElement(model="GT"))
schema.add("ImageVectorsM1", ImageEmbeddingSchemaElement(model="imageModel"))

run_name = f"model_distribution-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


test_session = TestSession(project_name="testingProject", run_name=run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

raga_dataset = Dataset(test_session=test_session, name="model-distribution-v12", data=pd_data_frame, schema=schema)
raga_dataset.load()


model_exe_fac = ModelExecutorFactory().get_model_executor(test_session=test_session, model_name="Signzy Embedding Model", version=3)

df = model_exe_fac.execute(init_args={"device": "cpu"},execution_args={"input_columns":{"img_paths":"SourceLink"}, "output_columns":{"embedding":"ImageEmbedding"}}, data_frame=raga_dataset)

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageEmbedding", ImageEmbeddingSchemaElement(model="signzyModel"))

raga_dataset.load(schema=schema)