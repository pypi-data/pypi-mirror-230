import ast
from raga import *
import pandas as pd
import datetime

def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def replace_url(old_value):
    url = f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/1/satellite_image_dataset/Satellite Image dataset/{old_value.replace('./', '')}"
    return StringElement(url)

def replace_embedding(old_value):
    embeddings = ImageEmbedding()
    embeddings_list = ast.literal_eval(old_value)
    for embedding in embeddings_list:
        embeddings.add(Embedding(embedding))
    return embeddings

label_to_classname = {
    1: "Building",
	2: "Land",
	3: "Road",
	4: "Vegetation",
	5: "Water",
	6: "Unlabelled"
}

def csv_parser(csv_path):
    data_frame = pd.read_csv(csv_path)
    data_frame["ImageId"] = data_frame["ImageId"].apply(lambda x: StringElement(x))
    data_frame["ImageUri"] = data_frame['SourceLink'].apply(lambda x: replace_url(x))
    data_frame["TimeOfCapture"] = data_frame.apply(lambda row: TimeStampElement(get_timestamp_x_hours_ago(row.name)), axis=1)
    data_frame["Reflection"] = data_frame.apply(lambda row: StringElement("Yes"), axis=1)
    data_frame["Overlap"] = data_frame.apply(lambda row: StringElement("No"), axis=1)
    data_frame["CameraAngle"] = data_frame.apply(lambda row: StringElement("Yes"), axis=1)
    data_frame["SourceLink"] = data_frame['SourceLink'].apply(lambda x:StringElement(x.replace('./', '')))
    data_frame["Annotations"] = data_frame['Annotations'].apply(lambda x: replace_url(x))
    data_frame["ModelAInfernences"] = data_frame['ModelAInfernences'].apply(lambda x:replace_url(x))
    data_frame["ImageVectorsM1"] = data_frame['ImageVectorsM1'].apply(lambda x:replace_embedding(x))
    return data_frame


pd_data_frame = csv_parser("./assets/ImageSegementation.csv")

#### Want to see in csv file uncomment line below ####
# data_frame_extractor(pd_data_frame).to_csv("./assets/ImageSegementation_test.csv")

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("Reflection", AttributeSchemaElement())
schema.add("Overlap", AttributeSchemaElement())
schema.add("CameraAngle", AttributeSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("Annotations", TIFFSchemaElement(label_mapping=label_to_classname, schema="tiff"))
schema.add("ModelAInfernences", TIFFSchemaElement(label_mapping=label_to_classname, schema="tiff"))
schema.add("ImageVectorsM1", ImageEmbeddingSchemaElement(model="imageModel"))




run_name = f"loader_failure_mode_analysis_semantic_segmentation-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

#create test_ds object of Dataset instance
test_ds = Dataset(test_session=test_session, name="satellite_image_dataset_v1", data=pd_data_frame, schema=schema)

#load to server
test_ds.load()
