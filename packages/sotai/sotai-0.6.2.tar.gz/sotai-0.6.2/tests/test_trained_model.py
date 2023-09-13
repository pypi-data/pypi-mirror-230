"""Tests for Trained Model."""

from unittest.mock import patch

import numpy as np
from sotai import (
    DatasetSplit,
    FeatureType,
    LinearConfig,
    LossType,
    Metric,
    NumericalFeatureConfig,
    PipelineConfig,
    TargetType,
    TrainedModel,
    TrainedModelMetadata,
    TrainingConfig,
    TrainingResults,
)
from sotai.models import CalibratedLinear

from .utils import construct_trained_model


def test_trained_classification_model_predict(fixture_data, fixture_feature_configs):
    """Tests the predict function on a trained model."""
    trained_model = construct_trained_model(
        TargetType.CLASSIFICATION, fixture_data, fixture_feature_configs
    )
    predictions, probabilities = trained_model.predict(fixture_data)
    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == len(fixture_data)
    assert isinstance(probabilities, np.ndarray)
    assert len(probabilities) == len(fixture_data)


def test_trained_regression_model_predict(fixture_data, fixture_feature_configs):
    """Tests the predict function on a trained model."""
    trained_model = construct_trained_model(
        TargetType.REGRESSION, fixture_data, fixture_feature_configs
    )
    predictions, _ = trained_model.predict(fixture_data)
    assert isinstance(predictions, np.ndarray)
    assert len(predictions) == len(fixture_data)


def test_trained_model_save_load(
    fixture_data,
    fixture_feature_configs,
    tmp_path,
):
    """Tests that a `TrainedModel` can be successfully saved and then loaded."""
    trained_model = construct_trained_model(
        TargetType.CLASSIFICATION, fixture_data, fixture_feature_configs
    )
    trained_model.save(tmp_path)
    loaded_trained_model = TrainedModel.load(tmp_path)
    assert isinstance(loaded_trained_model, TrainedModel)
    assert loaded_trained_model.dict(
        exclude={"model", "saved_filepath"}
    ) == trained_model.dict(exclude={"model", "saved_filepath"})
    assert isinstance(loaded_trained_model.model, CalibratedLinear)


@patch("sotai.trained_model.download_trained_model")
@patch(
    "sotai.trained_model.get_trained_model_metadata",
    return_value=TrainedModelMetadata(
        **{
            "id": 0,
            "dataset_id": 0,
            "model_config": LinearConfig(),
            "training_config": TrainingConfig(
                loss_type=LossType.MSE,
                epochs=1,
                batch_size=1,
                learning_rate=1,
            ),
            "training_results": TrainingResults(
                training_time=1,
                train_loss_by_epoch=[1],
                train_primary_metric_by_epoch=[1],
                val_loss_by_epoch=[1],
                val_primary_metric_by_epoch=[1],
                evaluation_time=1,
                test_loss=1,
                test_primary_metric=1,
                feature_analyses={},
                linear_coefficients={},
            ),
            "uuid": "test_uuid",
            "pipeline_config": PipelineConfig(
                id=0,
                target="target",
                target_type=TargetType.CLASSIFICATION,
                primary_metric=Metric.MSE,
                feature_configs={
                    "age": NumericalFeatureConfig(
                        name="age",
                        type=FeatureType.NUMERICAL,
                    ),
                },
                shuffle_data=False,
                drop_empty_percentage=70,
                dataset_split=DatasetSplit(train=80, val=10, test=10),
            ),
        }
    ),
)
def test_load_from_hosted(
    mock_get_trained_model,
    mock_download_trained_model,
    tmp_path,
    fixture_data,
    fixture_feature_configs,
):
    """Test loading a trained model from hosted."""
    trained_model = construct_trained_model(
        TargetType.CLASSIFICATION, fixture_data, fixture_feature_configs
    )
    trained_model.save(tmp_path)
    mock_download_trained_model.return_value = f"{tmp_path}/trained_ptcm_model.pt"
    trained_model = TrainedModel.from_hosted("test_uuid")
    mock_get_trained_model.assert_called_once()
    mock_download_trained_model.assert_called_once()
    assert isinstance(trained_model, TrainedModel)
    assert trained_model.training_config.epochs == 1
    assert trained_model.training_config.batch_size == 1
    assert trained_model.training_config.learning_rate == 1
    assert trained_model.training_config.loss_type == LossType.MSE
    assert trained_model.training_results.training_time == 1
    assert trained_model.training_results.train_loss_by_epoch == [1]
    assert trained_model.training_results.train_primary_metric_by_epoch == [1]
    assert trained_model.training_results.val_loss_by_epoch == [1]
    assert trained_model.model_config.output_calibration is False
