from raga import *
import datetime


run_name = f"run-failure-mode-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

rules = FMARules()
rules.add(metric="Precision", conf_threshold=0.8, metric_threshold=0.5, iou_threshold=0.5, label="ALL")

cls_default = clustering(method="k-means", embedding_col="ImageVectorsM1", level="image", args= {"numOfClusters": 5})

edge_case_detection = failure_mode_analysis(test_session=test_session,
                                            dataset_name = "fma_image_object_detection_ds-v3",
                                            test_name = "Test",
                                            model = "ModelA",
                                            gt = "ModelB",
                                            rules = rules,
                                            output_type="object_detection",
                                            type="metadata",
                                            aggregation_level=['weather'])

test_session.add(edge_case_detection)

test_session.run()