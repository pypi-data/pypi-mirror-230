import pathlib
from raga import *
import pandas as pd
import datetime

label_to_classname = {
    1: "no_data",
    2: "water",
    3: "trees",
    4: "grass",
    5: "flooded vegetation",
    6: "crops",
    7: "scrub",
    8: "built_area",
    9: "bare_ground",
    10: "snow_or_ice",
    11: "clouds",
}

def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def image_url(x):
    return f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/1/satsure_rgb/data_points/{pathlib.Path(x).stem}/images/{x}"

def mask_url(x):
    return f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/1/satsure_lulc/data_points/{pathlib.Path(x).stem}/images/{x}"

def attached_label(id, loss):
    return {id:loss}

def merge_loss_dicts(loss_dicts):
    mistake_score = MistakeScore()
    for d in loss_dicts:
        for key, value in d.items():
            mistake_score.add(key=key, value=value)
    return mistake_score

def csv_parser(file_path):
    df = pd.read_csv(file_path)
    df['loss'] = df.apply(lambda row: attached_label(row['label'], row['loss']), axis=1)
    merged_df = df.groupby('filepath', as_index=False)['loss'].agg(merge_loss_dicts)
    data_frame = pd.DataFrame()
    data_frame["ImageId"] = merged_df["filepath"].apply(lambda x: StringElement(x))
    data_frame["ImageUri"] = merged_df["filepath"].apply(lambda x: StringElement(image_url(x)))
    data_frame["TimeOfCapture"] = merged_df.apply(lambda row: TimeStampElement(get_timestamp_x_hours_ago(row.name)), axis=1)
    data_frame["SourceLink"] = merged_df['filepath'].apply(lambda x:StringElement(x))
    data_frame["Annotations"] = merged_df['filepath'].apply(lambda x:StringElement(mask_url(x)))
    data_frame["MistakeScores"] = merged_df['loss']
    data_frame["Reflection"] = data_frame.apply(lambda row: StringElement("Yes"), axis=1)
    data_frame["Overlap"] = data_frame.apply(lambda row: StringElement("No"), axis=1)
    data_frame["CameraAngle"] = data_frame.apply(lambda row: StringElement("Yes"), axis=1)
    return data_frame


data_frame = csv_parser("./assets/final_image_loss.csv")

#### Want to see in csv file uncomment line below ####
# data_frame_extractor(data_frame).to_csv("./assets/final_image_loss_full_s_df_new.csv", index=False)

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("Annotations", TIFFSchemaElement(label_mapping=label_to_classname, schema="tiff"))
schema.add("MistakeScores", MistakeScoreSchemaElement(ref_col_name="Annotations"))
schema.add('Reflection', AttributeSchemaElement())
schema.add('Overlap', AttributeSchemaElement())
schema.add('CameraAngle', AttributeSchemaElement())



run_name = f"loader_labeling_quality_semantic_segmentation-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")
# # #create test_ds object of Dataset instance
test_ds = Dataset(test_session=test_session, name="satsure-full-dataset-v4", data=data_frame, schema=schema)

# #load schema and pandas data frame
test_ds.load()
