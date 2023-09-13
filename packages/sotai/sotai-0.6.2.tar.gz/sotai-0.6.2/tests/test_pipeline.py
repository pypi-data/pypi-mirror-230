"""Tests for Pipeline."""
from unittest.mock import patch
import pandas as pd
import pytest

from sotai import (
    APIStatus,
    DatasetSplit,
    FeatureType,
    HypertuneConfig,
    LossType,
    Metric,
    Pipeline,
    PipelineConfig,
    TargetType,
    NumericalFeatureConfig,
)
from sotai.enums import InferenceConfigStatus
from sotai.constants import SOTAI_BASE_URL


@pytest.mark.parametrize(
    "target_type,expected_primary_metric",
    [(TargetType.CLASSIFICATION, Metric.AUC), (TargetType.REGRESSION, Metric.MSE)],
)
def test_init(
    fixture_feature_names,
    fixture_target,
    target_type,
    expected_primary_metric,
):
    """Tests pipeline initialization for a classification target."""
    pipeline = Pipeline(fixture_feature_names, fixture_target, target_type)
    assert pipeline.name == f"{fixture_target}_{target_type}"
    assert pipeline.target == fixture_target
    assert pipeline.target_type == target_type
    assert pipeline.primary_metric == expected_primary_metric
    assert len(pipeline.feature_configs) == 3
    numerical_config = pipeline.feature_configs["numerical"]
    assert numerical_config.name == "numerical"
    assert numerical_config.type == FeatureType.NUMERICAL
    categorical_strs_config = pipeline.feature_configs["categorical_strs"]
    assert categorical_strs_config.name == "categorical_strs"
    # Note: we expect the default config to be numerical if not specified.
    assert categorical_strs_config.type == FeatureType.NUMERICAL
    categorical_ints_config = pipeline.feature_configs["categorical_ints"]
    assert categorical_ints_config.name == "categorical_ints"
    # Note: we expect the default config to be numerical if not specified.
    assert categorical_ints_config.type == FeatureType.NUMERICAL


def test_init_with_categories(
    fixture_feature_names,
    fixture_target,
    fixture_categories_strs,
    fixture_categories_ints,
):
    """Tests pipeline initialization with specified categories."""
    pipeline = Pipeline(
        fixture_feature_names,
        fixture_target,
        TargetType.CLASSIFICATION,
        categories={
            "categorical_strs": fixture_categories_strs,
            "categorical_ints": fixture_categories_ints,
        },
    )
    categorical_strs_config = pipeline.feature_configs["categorical_strs"]
    assert categorical_strs_config.name == "categorical_strs"
    assert categorical_strs_config.type == FeatureType.CATEGORICAL
    assert categorical_strs_config.categories == fixture_categories_strs
    categorical_ints_config = pipeline.feature_configs["categorical_ints"]
    assert categorical_ints_config.name == "categorical_ints"
    assert categorical_ints_config.type == FeatureType.CATEGORICAL
    assert categorical_ints_config.categories == fixture_categories_ints


@pytest.mark.parametrize(
    "target_type", [TargetType.CLASSIFICATION, TargetType.REGRESSION]
)
@pytest.mark.parametrize("metric", [Metric.AUC, Metric.MSE, Metric.MAE])
@pytest.mark.parametrize("shuffle_data", [True, False])
@pytest.mark.parametrize("drop_empty_percentage", [30, 60, 80])
@pytest.mark.parametrize(
    "dataset_split",
    [
        DatasetSplit(train=80, val=10, test=10),
        DatasetSplit(train=60, val=20, test=20),
        DatasetSplit(train=70, val=20, test=10),
    ],
)
def test_init_from_config(
    fixture_target,
    fixture_feature_configs,
    target_type,
    metric,
    shuffle_data,
    drop_empty_percentage,
    dataset_split,
):
    """Tests pipeline initialization from a `PipelineConfig` instance."""
    pipeline_config = PipelineConfig(
        id=0,
        target=fixture_target,
        target_type=target_type,
        primary_metric=metric,
        feature_configs=fixture_feature_configs,
        shuffle_data=shuffle_data,
        drop_empty_percentage=drop_empty_percentage,
        dataset_split=dataset_split,
    )
    name = "test_pipeline"
    pipeline = Pipeline.from_config(pipeline_config, name=name)
    assert pipeline.name == name
    assert pipeline.target == fixture_target
    assert pipeline.target_type == target_type
    assert pipeline.primary_metric == metric
    assert pipeline.feature_configs == fixture_feature_configs
    assert pipeline.shuffle_data == shuffle_data
    assert pipeline.drop_empty_percentage == drop_empty_percentage
    assert pipeline.dataset_split == dataset_split


def test_prepare(
    fixture_data,
    fixture_feature_names,
    fixture_target,
    fixture_categories_strs,
):
    """Tests the pipeline prepare function."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, target_type=TargetType.CLASSIFICATION
    )
    # We set shuffle to false to ensure the data is split in the same way.
    pipeline.shuffle_data = False
    pipeline.dataset_split.train = 80
    pipeline.dataset_split.val = 10
    pipeline.dataset_split.test = 10
    dataset, pipeline_config = pipeline.prepare(fixture_data)
    assert pipeline_config.id == 0
    categorical_strs_config = pipeline_config.feature_configs["categorical_strs"]
    assert categorical_strs_config.name == "categorical_strs"
    assert categorical_strs_config.type == FeatureType.CATEGORICAL
    assert categorical_strs_config.categories == fixture_categories_strs
    categorical_ints_config = pipeline_config.feature_configs["categorical_ints"]
    assert categorical_ints_config.name == "categorical_ints"
    # Note: integer categories will be detected as numerical if not specified.
    assert categorical_ints_config.type == FeatureType.NUMERICAL
    assert dataset.id == 0
    assert dataset.pipeline_config_id == pipeline_config.id
    num_examples = len(fixture_data)
    num_training_examples = int(num_examples * pipeline.dataset_split.train / 100)
    num_val_examples = int(num_examples * pipeline.dataset_split.val / 100)
    assert dataset.prepared_data.train.equals(fixture_data.iloc[:num_training_examples])
    assert dataset.prepared_data.val.equals(
        fixture_data.iloc[
            num_training_examples : num_training_examples + num_val_examples
        ]
    )
    assert dataset.prepared_data.test.equals(
        fixture_data.iloc[num_training_examples + num_val_examples :]
    )


@pytest.mark.parametrize(
    "target_type",
    [
        (TargetType.CLASSIFICATION),
        (TargetType.REGRESSION),
    ],
)
def test_train_calibrated_linear_model(
    fixture_data,
    fixture_feature_names,
    fixture_target,
    target_type,
):
    """Tests pipeline training for calibrated linear regression model."""
    pipeline = Pipeline(fixture_feature_names, fixture_target, target_type)
    pipeline.shuffle_data = False
    pipeline.dataset_split.train = 60
    pipeline.dataset_split.val = 20
    pipeline.dataset_split.test = 20
    trained_model = pipeline.train(fixture_data)
    assert len(pipeline.configs) == 1
    assert len(pipeline.datasets) == 1
    assert trained_model
    assert trained_model.dataset_id == 0
    assert pipeline.datasets[trained_model.dataset_id]
    assert trained_model.pipeline_config.id == 0
    assert pipeline.configs[trained_model.pipeline_config.id]


def test_pipeline_save_load(
    fixture_data,
    fixture_feature_names,
    fixture_target,
    tmp_path,
):
    """Tests that an instance of `Pipeline` can be successfully saved and loaded."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, TargetType.CLASSIFICATION
    )
    trained_model = pipeline.train(fixture_data)
    pipeline.save(tmp_path)
    loaded_pipeline = Pipeline.load(tmp_path)
    assert isinstance(loaded_pipeline, Pipeline)
    assert loaded_pipeline.name == pipeline.name
    assert loaded_pipeline.target == pipeline.target
    assert loaded_pipeline.target_type == pipeline.target_type
    assert loaded_pipeline.primary_metric == pipeline.primary_metric
    assert loaded_pipeline.feature_configs == pipeline.feature_configs
    assert loaded_pipeline.configs == pipeline.configs
    for dataset_id, loaded_dataset in loaded_pipeline.datasets.items():
        dataset = pipeline.datasets[dataset_id]
        assert loaded_dataset.id == dataset.id
        assert loaded_dataset.pipeline_config_id == dataset.pipeline_config_id
        assert loaded_dataset.prepared_data.train.equals(dataset.prepared_data.train)
        assert loaded_dataset.prepared_data.val.equals(dataset.prepared_data.val)
        assert loaded_dataset.prepared_data.test.equals(dataset.prepared_data.test)
    assert len(loaded_pipeline.trained_models) == 1
    assert loaded_pipeline.trained_models[0].dataset_id == trained_model.dataset_id
    assert (
        loaded_pipeline.trained_models[0].pipeline_uuid == trained_model.pipeline_uuid
    )
    assert (
        loaded_pipeline.trained_models[0].pipeline_config
        == trained_model.pipeline_config
    )
    assert (
        loaded_pipeline.trained_models[0].training_results
        == trained_model.training_results
    )
    assert (
        loaded_pipeline.trained_models[0].training_config
        == trained_model.training_config
    )


@patch(
    "sotai.pipeline.post_pipeline", return_value=(APIStatus.SUCCESS, "test_pipeline_id")
)
def test_publish(
    post_pipeline,
    fixture_feature_names,
    fixture_target,
):
    """Tests that a pipeline can be published to the API."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, TargetType.CLASSIFICATION
    )
    pipeline_uuid = pipeline.publish()
    post_pipeline.assert_called_once()
    assert pipeline_uuid == "test_pipeline_id"


@patch("sotai.pipeline.Pipeline._upload_model", return_value=APIStatus.SUCCESS)
@patch(
    "sotai.pipeline.post_trained_model_analysis",
    return_value=(
        APIStatus.SUCCESS,
        {"trained_model_metadata_uuid": "test_uuid"},
    ),
)
@patch("sotai.pipeline.post_pipeline_feature_configs", return_value=APIStatus.SUCCESS)
@patch(
    "sotai.pipeline.post_pipeline_config",
    return_value=(APIStatus.SUCCESS, "test_pipeline_config_id"),
)
@patch(
    "sotai.pipeline.post_pipeline", return_value=(APIStatus.SUCCESS, "test_pipeline_id")
)
@patch("sotai.pipeline.get_api_key", return_value="test_api_key")
def test_analysis(
    get_api_key,
    post_pipeline,
    post_pipeline_config,
    post_pipeline_feature_configs,
    post_trained_model_analysis,
    upload_model,
    fixture_data,
    fixture_feature_names,
    fixture_target,
):
    """Tests that pipeline analysis works as expected."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, TargetType.CLASSIFICATION
    )
    trained_model = pipeline.train(fixture_data)
    analysis_response = pipeline.analysis(trained_model)

    get_api_key.assert_called()
    upload_model.assert_called_once()
    post_pipeline.assert_called_once()
    post_pipeline_config.assert_called_once_with(
        "test_pipeline_id", trained_model.pipeline_config
    )
    post_pipeline_feature_configs.assert_called_once_with(
        "test_pipeline_config_id", trained_model.pipeline_config.feature_configs
    )
    post_trained_model_analysis.assert_called_once_with(
        "test_pipeline_config_id", trained_model
    )
    expected_analysis_response = (
        f"{SOTAI_BASE_URL}/pipelines/test_pipeline_id/"
        f"trained-models/test_uuid/overall-model-results"
    )
    assert analysis_response == expected_analysis_response


@patch(
    "pandas.read_csv",
    return_value=pd.DataFrame(
        [[1, 2, 3]], columns=["categorical_ints", "numerical", "categorical_strs"]
    ),
)
@patch(
    "sotai.pipeline.post_inference",
    return_value=(APIStatus.SUCCESS, "test_inference_uuid"),
)
@patch("sotai.pipeline.get_api_key", return_value="test_api_key")
def test_run_inference(
    get_api_key,
    post_inference,
    read_csv,
    fixture_data,
    fixture_feature_names,
    fixture_target,
):
    """Tests that a pipeline can run inference on a dataset."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, TargetType.CLASSIFICATION
    )
    trained_model = pipeline.train(fixture_data)
    trained_model.uuid = "test_uuid"

    pipeline.inference("/tmp/data.csv", trained_model)

    read_csv.assert_called_once_with("/tmp/data.csv")
    get_api_key.assert_called_once()
    post_inference.assert_called_once_with("/tmp/data.csv", "test_uuid")


@patch("sotai.pipeline.INFERENCE_POLLING_INTERVAL", 1)
@patch("sotai.pipeline.get_inference_results", response_value=APIStatus.SUCCESS)
@patch(
    "sotai.pipeline.get_inference_status",
    side_effect=[
        (APIStatus.SUCCESS, InferenceConfigStatus.INITIALIZING),
        (APIStatus.SUCCESS, InferenceConfigStatus.SUCCESS),
    ],
)
def test_await_inference_results(
    get_inference_status,
    get_inference_results,
    fixture_data,
    fixture_feature_names,
    fixture_target,
):
    """Tests that a pipeline can await inference results."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, TargetType.CLASSIFICATION
    )
    pipeline.train(fixture_data)

    pipeline.await_inference("test_uuid", "/tmp/predictions")
    get_inference_status.assert_called_with("test_uuid")
    get_inference_results.assert_called_once()


@patch(
    "sotai.pipeline.post_hypertune_job",
    return_value=(
        APIStatus.SUCCESS,
        ["test_uuid"],
    ),
)
@patch(
    "sotai.pipeline.Pipeline._upload_dataset",
    return_value="test_dataset_id",
)
@patch(
    "sotai.pipeline.Pipeline._post_pipeline_config",
    return_value="test_pipeline_config_id",
)
@patch("sotai.pipeline.get_api_key", return_value="test_api_key")
def test_hypertune_hosted(
    get_api_key,
    post_pipeline_config,
    upload_dataset,
    post_hypertune_job,
    fixture_data,
    fixture_feature_names,
    fixture_target,
):
    """Tests that pipeline analysis works as expected."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, TargetType.CLASSIFICATION
    )
    hypertune_config = HypertuneConfig(
        epochs=[100],
        batch_sizes=[32],
        learning_rates=[0.001, 0.01],
        loss_type=LossType.BINARY_CROSSENTROPY,
    )
    hypertune_response = pipeline.hypertune(fixture_data, hypertune_config, hosted=True)

    get_api_key.assert_called()
    upload_dataset.assert_called_once()
    post_hypertune_job.assert_called_once()
    post_pipeline_config.assert_called_once()

    assert hypertune_response[0] == "test_uuid"


def test_hypertune_local(fixture_feature_names, fixture_target, fixture_data):
    """Tests that pipeline hypertuning works as expected."""
    pipeline = Pipeline(
        fixture_feature_names, fixture_target, TargetType.CLASSIFICATION
    )
    hypertune_config = HypertuneConfig(
        epochs=[100],
        batch_sizes=[32, 64],
        learning_rates=[0.001, 0.01],
        loss_type=LossType.BINARY_CROSSENTROPY,
    )
    trained_models = pipeline.hypertune(fixture_data, hypertune_config, hosted=False)

    assert len(trained_models) == 4
    assert trained_models[0].training_config.epochs == 100


@patch(
    "sotai.pipeline.get_pipeline",
    return_value=(
        {
            "id": 1,
            "name": "test_pipeline",
            "target": "target",
            "target_type": "classification",
            "primary_metric": "auc",
        },
        0,
        {
            0: PipelineConfig(
                **{
                    "id": 0,
                    "target": "target",
                    "target_type": "classification",
                    "primary_metric": "auc",
                    "feature_configs": {
                        "age": NumericalFeatureConfig(
                            **{
                                "name": "age",
                                "num_keypoints": 10,
                                "input_keypoints_init": "quantiles",
                                "monotonicity": "none",
                            }
                        ),
                        "chol": NumericalFeatureConfig(
                            **{
                                "name": "chol",
                                "num_keypoints": 10,
                                "input_keypoints_init": "quantiles",
                                "monotonicity": "none",
                            }
                        ),
                    },
                    "shuffle_data": False,
                    "drop_empty_percentage": 70,
                    "dataset_split": {
                        "train": 80,
                        "val": 10,
                        "test": 10,
                    },
                }
            )
        },
        ["test_uuid"],
    ),
)
def test_load_from_hosted(mock_get_pipeline):
    """Tests that a pipeline can be loaded from the API."""
    pipeline = Pipeline.from_hosted("test_uuid", include_trained_models=False)

    mock_get_pipeline.assert_called_once_with("test_uuid")

    assert pipeline.name == "test_pipeline"
    assert pipeline.target == "target"
    assert pipeline.target_type == TargetType.CLASSIFICATION
    assert pipeline.primary_metric == Metric.AUC
    assert len(pipeline.feature_configs) == 2
    assert len(pipeline.configs) == 1
    assert len(pipeline.datasets) == 0


@patch("sotai.pipeline.TrainedModel.from_hosted", return_value=None)
@patch(
    "sotai.pipeline.get_trained_model_uuids",
    return_value=["test_model_uuid"],
)
@patch(
    "sotai.pipeline.Pipeline._upload_model",
    return_value=(APIStatus.SUCCESS),
)
@patch(
    "sotai.pipeline.Pipeline.analysis",
    return_value=(APIStatus.SUCCESS),
)
@patch(
    "sotai.pipeline.Pipeline._upload_dataset",
    return_value=(APIStatus.SUCCESS, "test_dataset_id"),
)
@patch(
    "sotai.pipeline.Pipeline._post_pipeline_config",
    return_value="test_pipeline_config_id",
)
@patch(
    "sotai.pipeline.Pipeline.publish",
    return_value=None,
)
def test_sync(
    publish,
    post_pipeline_config,
    upload_dataset,
    analysis,
    upload_model,
    get_trained_model_uuids,
    from_hosted,
    fixture_data,
    fixture_feature_names,
    fixture_target,
):
    """Tests that a pipeline can be synced."""
    pipeline = Pipeline(
        fixture_feature_names,
        fixture_target,
        TargetType.CLASSIFICATION,
        default_allow_hosting=True,
    )

    pipeline.hypertune(
        fixture_data,
        hypertune_config=HypertuneConfig(
            epochs=[100, 200],
            batch_sizes=[32],
            learning_rates=[0.01],
            loss_type=LossType.BINARY_CROSSENTROPY,
        ),
        hosted=False,
    )
    pipeline.sync()

    publish.assert_called_once()
    from_hosted.assert_called_once()
    upload_dataset.assert_called_once()
    post_pipeline_config.assert_called_once()
    analysis.assert_called()
    upload_model.assert_called()
    get_trained_model_uuids.assert_called_once()
