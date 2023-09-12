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

def image_classification(x):
    classification = ImageClassificationElement()
    x = ast.literal_eval(x)
    for key, value in x.items():
        classification.add(key=key, value=value)
    return classification

def mistake_score(x):
    mistake_score = MistakeScore()
    x = ast.literal_eval(x)
    for key, value in x.items():
        mistake_score.add(key=key, value=value)
    return mistake_score

def image_id(row):
    file = row["SourceLink"].split("/")[-1]
    return StringElement(f"{row['ImageId']}_{file}".replace(" ", "_"))

def csv_parser(csv_file):
    df = pd.read_csv(csv_file)
    data_frame = pd.DataFrame()
    data_frame["ImageId"] = df.apply(image_id , axis=1)
    data_frame["ImageUri"] = df["SourceLink"].apply(lambda x: StringElement(f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/1/{x}"))
    data_frame["SourceLink"] = df["SourceLink"].apply(lambda x: StringElement(x))
    data_frame["TimeOfCapture"] = df.apply(lambda row: TimeStampElement(get_timestamp_x_hours_ago(row.name)), axis=1)
    data_frame["GroundTruth"] = df["Ground Truth"].apply(image_classification)
    data_frame["MistakeScore"] = df["mistake_score"].apply(mistake_score)
    return data_frame

pd_data_frame = csv_parser("./assets/labelling_qc_score_df.csv")

#### Want to see in csv file uncomment line below ####
# data_frame_extractor(pd_data_frame).to_csv("./assets/labelling_qc_score_df_test.csv", index=False)

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("GroundTruth", ImageClassificationSchemaElement(model="GT"))
schema.add("MistakeScore", MistakeScoreSchemaElement(ref_col_name="GroundTruth"))

run_name = f"loader_labeling_quality_image_classification-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

#create test_ds object of Dataset instance
test_ds = Dataset(test_session=test_session, name="100-sport-dataset-v12", data=pd_data_frame, schema=schema)

#load to server
test_ds.load()