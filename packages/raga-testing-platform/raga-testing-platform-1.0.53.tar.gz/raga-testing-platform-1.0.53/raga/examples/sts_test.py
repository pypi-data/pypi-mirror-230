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

def json_parser(file_path):
    data_frame = []
    hr = 1
    with open(file_path, 'r') as file:
        dataset = json.load(file)
    for index, data_point in enumerate(dataset):
        AnnotationsV1 = ImageDetectionObject()
        ModelInferences = ImageDetectionObject()
        ROIVectorsM1 = ROIEmbedding()
        for AnnotationsV1_item in data_point.get('AnnotationsV1'):
            AnnotationsV1.add(ObjectDetection(Id=AnnotationsV1_item['Id'], ClassId=AnnotationsV1_item['ClassId'], ClassName=AnnotationsV1_item['ClassName'], Confidence=AnnotationsV1_item['Confidence'], BBox= AnnotationsV1_item['BBox'], Format="xywh_normalized"))

        for ModelInferences_item in data_point.get('ModelInferences'):
            ModelInferences.add(ObjectDetection(Id=ModelInferences_item['Id'], ClassId=ModelInferences_item['ClassId'], ClassName=ModelInferences_item['ClassName'], Confidence=ModelInferences_item['Confidence'], BBox= ModelInferences_item['BBox'], Format="xywh_normalized"))
        
        for roi_emb in data_point.get('ROIVectorsM1'):
                ROIVectorsM1.add(id=roi_emb.get("Id"), embedding_values=roi_emb.get("embedding"))

        data_point.get("ImageId")
        image_file = data_point.get("SourceLink").split("/")[-1]
        data_point = {
            'ImageUri':StringElement(f"https://ragaaimedia.s3.ap-south-1.amazonaws.com/sts-test/001.jpg"),
            'ImageId': StringElement(data_point.get("ImageId")),
            'TimeOfCapture': TimeStampElement(get_timestamp_x_hours_ago(hr)),
            'SourceLink': StringElement(data_point.get("SourceLink")),
            'AnnotationsV1': AnnotationsV1,
            'ModelInferences': ModelInferences,
            # 'ROIVectorsM1': ROIVectorsM1
        }
        data_frame.append(data_point)
        hr+=1
        if index == 10:
             break
    return pd.DataFrame(data_frame)

# data_frame_extractor(json_parser("./assets/COCO_engg_final.json")).to_csv("./assets/COCO_engg_final_100.csv", index=False)

pd_data_frame = json_parser("./assets/COCO_engg_final.json")

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("AnnotationsV1", InferenceSchemaElement(model="ModelA"))
schema.add("ModelInferences", InferenceSchemaElement(model="ModelB"))
# schema.add("ROIVectorsM1", RoiEmbeddingSchemaElement(model="ROI Model"))

run_name = f"run-failure-mode-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

creds = DatasetCreds(arn="arn:aws:iam::596708924737:role/test-s3")

#create test_ds object of Dataset instance
test_ds = Dataset(test_session=test_session, name="arn-test-ds-4", data=pd_data_frame, schema=schema, creds=creds)

#load schema and pandas data frame
test_ds.load()