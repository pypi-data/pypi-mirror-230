from typing import Optional
from raga import TestSession, DriftDetectionRules

def data_drift_detection(test_session:TestSession, train_dataset_name: str, field_dataset_name: str, test_name: str, train_embed_col_name: str, field_embed_col_name: str, level: str, rules=DriftDetectionRules, aggregation_level:  Optional[list] = [],
filter: Optional[str] = ""):
    
    train_dataset_id, field_dataset_id = data_drift_detection_validation(test_session=test_session, train_dataset_name=train_dataset_name, field_dataset_name=field_dataset_name, test_name=test_name, train_embed_col_name=train_embed_col_name, field_embed_col_name=field_embed_col_name, level=level, rules=rules, aggregation_level=aggregation_level)    
    response = {
            "datasetId": field_dataset_id,
            "experimentId": test_session.experiment_id,
            "name": test_name,
            "aggregationLevels": aggregation_level,
            "filter":filter,
            "trainDatasetId":train_dataset_id,
            "trainEmbedColName": train_embed_col_name,
            "fieldEmbedColName": field_embed_col_name,
            "level": level,
            "rules": rules.get(),
            'test_type':'drift_test'
        }
    return response


def data_drift_detection_validation(test_session:TestSession, 
                                    train_dataset_name: str, 
                                    field_dataset_name: str,
                                    test_name: str,
                                    train_embed_col_name: str,
                                    field_embed_col_name: str,
                                    level: str, 
                                    rules=DriftDetectionRules,
                                    aggregation_level:Optional[list] = []):
    
    assert isinstance(test_session, TestSession), "test_session must be an instance of the TestSession class."
    assert isinstance(train_dataset_name, str) and train_dataset_name, "train_dataset_name is required and must be an instance of the str."
    assert isinstance(field_dataset_name, str) and field_dataset_name, "field_dataset_name is required and must be an instance of the str."
    
    train_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={train_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    if not isinstance(train_res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")
    train_dataset_id = train_res_data.get("data", {}).get("id")
    if not train_dataset_id:
        raise KeyError("Invalid response data. Token not found.")
    
    field_res_data = test_session.http_client.get(f"api/dataset?projectId={test_session.project_id}&name={field_dataset_name}", headers={"Authorization": f'Bearer {test_session.token}'})
    if not isinstance(field_res_data, dict):
            raise ValueError("Invalid response data. Expected a dictionary.")
    field_dataset_id = field_res_data.get("data", {}).get("id")
    if not field_dataset_id:
        raise KeyError("Invalid response data. Token not found.")
    
    assert isinstance(test_name, str) and test_name, "test_name is required and must be an instance of the str."
    assert isinstance(train_embed_col_name, str) and train_embed_col_name, "train_embed_col_name is required and must be an instance of the str."
    assert isinstance(field_embed_col_name, str) and field_embed_col_name, "field_embed_col_name is required and must be an instance of the str."
    assert isinstance(level, str) and level, "level is required and must be an instance of the str."
    assert isinstance(rules, DriftDetectionRules) and rules.get(), "rules is required and must be an instance of the DriftDetectionRules."

    if aggregation_level:
        assert isinstance(aggregation_level, list), "aggregation_level must be list"

    return train_dataset_id, field_dataset_id
