from raga import *
import datetime

run_name = f"run-labeling-quality-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="nnXvot82D3idpraRtCjJ", secret_key="P2doycL4WBZXLNARIs4bESxttzF3MHSC5K15Jrs9", host="http://65.0.13.122:8080")

rules = LQRules()
rules.add(metric="mistake_score", label=["ALL"], metric_threshold=0.005)


edge_case_detection = labelling_quality_test(test_session=test_session,
                                            dataset_name = "100-sport-dataset-v11",
                                            test_name = "Labeling Quality Test",
                                            type = "labelling_consistency",
                                            output_type="image_classification",
                                            mistake_score_col_name = "MistakeScore",
                                            rules = rules)
test_session.add(edge_case_detection)

test_session.run()