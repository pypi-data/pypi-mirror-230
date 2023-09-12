from raga import *
import datetime


run_name = f"failure_mode_analysis_semantic_segmentation-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

rules = FMARules()

rules.add(metric = "F1Score",  metric_threshold = 0.5, label = "ALL", type="label", background_label="unlabelled", include_background=False)

rules.add(metric = "wIoU", metric_threshold = 0.5, weights={"car": 2, "unlabelled": 1}, type="label")



cls_default = clustering(method="k-means", embedding_col="ImageVectorsM1", level="image", args= {"numOfClusters": 5})

edge_case_detection = failure_mode_analysis(test_session=test_session,
                                            dataset_name = "satellite_image_dataset_v1",
                                            test_name = "Test",
                                            model = "ModelA",
                                            gt = "ModelB",
                                            rules = rules,
                                            output_type="semantic-metadata",
                                            type="metadata",
                                            aggregation_level=['weather'])

test_session.add(edge_case_detection)

test_session.run()