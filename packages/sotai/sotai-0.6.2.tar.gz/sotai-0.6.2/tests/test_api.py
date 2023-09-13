"""Tests for api."""
from unittest.mock import MagicMock, patch, call
import pandas as pd

from sotai.api import (
    download_prepared_dataset,
    get_dataset_uuids,
    get_inference_results,
    get_inference_status,
    post_inference,
    post_pipeline,
    get_pipeline,
    get_trained_model_metadata,
    post_pipeline_config,
    post_pipeline_feature_configs,
    post_trained_model,
    post_dataset,
    post_external_inference,
    post_hypertune_job,
    post_trained_model_analysis,
)
from sotai.types import HypertuneConfig, LinearConfig
from sotai.enums import LossType
from sotai.constants import SOTAI_API_ENDPOINT, SOTAI_BASE_URL
from .utils import MockResponse


@patch("requests.post", return_value=MockResponse({"uuid": "test_uuid"}))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_pipeline(mock_version, mock_get_api_key, mock_post, fixture_pipeline):
    """Tests that a pipeline is posted correctly.""" ""
    pipeline_response = post_pipeline(fixture_pipeline)

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines",
        json={
            "name": "target_classification",
            "target": "target",
            "target_column_type": "classification",
            "primary_metric": "auc",
        },
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )

    mock_get_api_key.assert_called_once()
    mock_version.assert_called()
    mock_version.assert_called_once()
    assert pipeline_response[1] == "test_uuid"
    assert mock_post.call_count == 1


@patch("requests.post", return_value=MockResponse({"uuid": "test_uuid"}))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_pipeline_config(
    mock_version, mock_get_api_key, mock_post, fixture_pipeline_config
):
    """Tests that a pipeline config is posted correctly."""
    pipeline_config_response = post_pipeline_config(
        "test_uuid", fixture_pipeline_config
    )

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines/test_uuid/pipeline-configs",
        json={
            "shuffle_data": False,
            "drop_empty_percentage": 80,
            "train_percentage": 60,
            "validation_percentage": 20,
            "test_percentage": 20,
            "pipeline_config_sdk_id": 1,
        },
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()
    assert pipeline_config_response[1] == "test_uuid"


@patch("requests.post", return_value=MockResponse({"uuid": "test_uuid"}))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_feature_configs(
    mock_version,
    mock_get_api_key,
    mock_post,
    fixture_pipeline_config,
    fixture_categories_strs,
    fixture_categories_ints,
):
    """Tests that feature configs are posted correctly."""
    pipeline_config_response = post_pipeline_feature_configs(
        "test_uuid", fixture_pipeline_config.feature_configs
    )

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipeline-configs/test_uuid/feature-configs",
        json=[
            {
                "feature_name": "numerical",
                "feature_type": "numerical",
                "num_keypoints": 10,
                "monotonicity": "increasing",
                "input_keypoints_init": "quantiles",
                "input_keypoints_type": "fixed",
            },
            {
                "feature_name": "categorical_strs",
                "feature_type": "categorical",
                "categories_str": fixture_categories_strs,
            },
            {
                "feature_name": "categorical_ints",
                "feature_type": "categorical",
                "categories_int": fixture_categories_ints,
            },
        ],
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()

    assert pipeline_config_response == "success"


@patch("requests.post", return_value=MockResponse({"uuid": "test_uuid"}))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_trained_model_analysis(
    mock_version, mock_get_api_key, mock_post, fixture_trained_model
):
    """Tests that a trained model is posted correctly."""
    fixture_trained_model.id = 1
    post_trained_model_analysis("test_uuid", fixture_trained_model)

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipeline-configs/test_uuid/analysis",
        json={
            "feature_analyses": [
                {
                    "feature_name": "test",
                    "feature_type": "numerical",
                    "keypoints_inputs_categorical": None,
                    "keypoints_inputs_numerical": [1.0, 2.0, 3.0],
                    "keypoints_outputs": [1.0, 2.0, 3.0],
                    "statistic_max": 2.0,
                    "statistic_mean": 3.0,
                    "statistic_median": 4.0,
                    "statistic_min": 1.0,
                    "statistic_std": 5.0,
                }
            ],
            "model_config": {
                "loss_type": "mse",
                "model_config_name": "Model 1",
                "model_framework": "pytorch",
                "model_type": "linear",
                "primary_metric": "auc",
                "target_column": "target",
                "target_column_type": "classification",
            },
            "overall_model_results": {
                "batch_size": 32,
                "epochs": 100,
                "feature_names": ["test"],
                "learning_rate": 0.001,
                "linear_coefficients": [1.0],
                "runtime_in_seconds": 1.0,
                "test_loss": 1.0,
                "test_primary_metric": 1.0,
                "train_loss_per_epoch": [1.0, 2.0, 3.0],
                "train_primary_metric_per_epoch": [1.0, 2.0, 3.0],
                "validation_loss_per_epoch": [1.0, 2.0, 3.0],
                "validation_primary_metric_per_epoch": [1.0, 2.0, 3.0],
            },
            "trained_model_metadata": {
                "batch_size": 32,
                "epochs": 100,
                "learning_rate": 0.001,
                "test_primary_metric": 1,
                "validation_primary_metric": [3],
                "train_primary_metric": [3],
                "trained_model_sdk_id": 1,
            },
        },
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()


@patch("tarfile.open")
@patch("builtins.open")
@patch("requests.post", return_value=MockResponse({"uuid": "test_uuid"}))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_trained_model(
    mock_version, mock_get_api_key, mock_post, mock_open_data, mock_tarfile_open
):
    """Tests that feature configs are posted correctly."""
    mock_add = MagicMock()
    mock_open_data.return_value.__enter__.return_value = "data"
    mock_tarfile_open.return_value.__enter__.return_value.add = mock_add
    pipeline_response = post_trained_model("/tmp/model", "test_uuid")

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/models",
        files={"file": "data"},
        data={"trained_model_metadata_uuid": "test_uuid"},
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()

    assert pipeline_response == "success"


@patch("builtins.open")
@patch(
    "requests.post",
    return_value=MockResponse({"inference_config_uuid": "test_inference_uuid"}),
)
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_inference(
    mock_version,
    mock_get_api_key,
    mock_post,
    mock_open_data,
):
    """Tests that feature configs are posted correctly."""
    mock_open_data.return_value.__enter__.return_value = "data"
    pipeline_response = post_inference("/tmp/model", "test_uuid")

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/inferences",
        files={"file": "data"},
        data={"trained_model_metadata_uuid": "test_uuid"},
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()

    assert pipeline_response[1] == "test_inference_uuid"
    assert pipeline_response[0] == "success"


@patch("requests.get", return_value=MockResponse("initializing", 200))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_get_inference_status(mock_version, mock_get_api_key, mock_get):
    """Tests that inference config retrieval is handled correctly."""
    inference_status = get_inference_status("test_uuid")

    mock_get.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/inferences/test_uuid/status",
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )

    assert inference_status[1] == "initializing"
    assert inference_status[0] == "success"
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()


@patch("urllib.request.urlretrieve", return_value=None)
@patch("requests.get", return_value=MockResponse("test.com", 200))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_get_inference_result(
    mock_version, mock_get_api_key, mock_get, mock_urlretrieve
):
    """Tests that inference file retrieval is handled correctly."""
    inference_status = get_inference_results("test_uuid", "/tmp")

    mock_get.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/inferences/test_uuid/download",
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )

    assert inference_status == "success"
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()
    mock_urlretrieve.assert_called_with("test.com", "/tmp/inference_results.csv")


@patch("builtins.open")
@patch(
    "requests.post",
    return_value=MockResponse({"uuid": "test_dataset_uuid"}),
)
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_dataset(
    mock_version,
    mock_get_api_key,
    mock_post,
    mock_open_data,
):
    """Tests that feature configs are posted correctly."""
    mock_open_data.return_value = "data"
    pipeline_response = post_dataset(
        "/tmp/dataset/train.csv",
        "/tmp/dataset/test.csv",
        "/tmp/dataset/validation.csv",
        ["age", "chol"],
        [],
        "test_pipeline_uuid",
        1,
    )

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/datasets",
        files=[("files", "data"), ("files", "data"), ("files", "data")],
        data={
            "pipeline_config_uuid": "test_pipeline_uuid",
            "columns": ["age", "chol"],
            "categorical_columns": [],
            "dataset_sdk_id": 1,
        },
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()

    assert pipeline_response[1] == "test_dataset_uuid"
    assert pipeline_response[0] == "success"


@patch(
    "requests.post",
    return_value=MockResponse(
        {"trained_model_metadata_uuids": ["test_uuid_1", "test_uuid_2"]}
    ),
)
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_hypertune(
    mock_version, mock_get_api_key, mock_post, fixture_pipeline_config
):
    """Tests that a trained model is posted correctly."""

    hypertune_config = HypertuneConfig(
        epochs=[100],
        batch_sizes=[32],
        learning_rates=[0.001, 0.01],
        loss_type=LossType.BINARY_CROSSENTROPY,
    )
    fixture_pipeline_config.uuid = "test_uuid"
    model_config = LinearConfig()
    post_hypertune_job(
        hypertune_config, fixture_pipeline_config, model_config, "test_dataset_uuid", 1
    )

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipeline-config/test_uuid/hypertune",
        json={
            "dataset_uuid": "test_dataset_uuid",
            "model_config": {
                "model_framework": "pytorch",
                "model_config_name": "Model 1",
                "model_type": "linear",
                "target_column_type": "classification",
                "target_column": "target",
                "primary_metric": "auc",
                "selected_features": [
                    "numerical",
                    "categorical_strs",
                    "categorical_ints",
                ],
                "loss_type": "binary",
                "advanced_options": {
                    "output_min": None,
                    "output_max": None,
                    "output_calibration": False,
                    "output_calibration_num_keypoints": 10,
                    "output_initialization": "quantiles",
                    "output_calibration_input_keypoints_type": "fixed",
                    "use_bias": True,
                },
            },
            "training_config": {
                "epochs_options": [100],
                "batch_size_options": [32],
                "learning_rate_options": [0.001, 0.01],
                "num_parallel_jobs": 4,
                "num_cpus_per_job": 2,
            },
            "next_model_id": 1,
        },
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()


@patch(
    "requests.get",
    return_value=MockResponse(
        {
            "name": "target_classification",
            "target": "target",
            "target_type": "classification",
            "primary_metric": "auc",
            "shuffle_data": True,
            "drop_empty_percentage": 70,
            "dataset_split": {
                "train_percentage": 80,
                "test_percentage": 10,
                "validation_percentage": 10,
            },
            "trained_model_metadata_uuids": ["test_model_uuid"],
            "pipeline_configs": [
                {
                    "uuid": "test_pipeline_config_uuid",
                    "pipeline_config_sdk_id": 1,
                    "shuffle_data": True,
                    "drop_empty_percentage": 70,
                    "train_percentage": 80,
                    "validation_percentage": 10,
                    "test_percentage": 10,
                    "feature_config_list": [
                        {
                            "feature_name": "age",
                            "feature_type": "numerical",
                            "monotonicity": "none",
                            "num_buckets": 0,
                            "num_keypoints": 10,
                            "input_keypoints": "quantiles",
                            "input_keypoints_type": "fixed",
                            "unimodality": "none",
                            "feature_index": 1,
                            "status": "success",
                        },
                        {
                            "feature_name": "sex",
                            "feature_type": "numerical",
                            "monotonicity": "none",
                            "num_buckets": 0,
                            "num_keypoints": 10,
                            "input_keypoints": "quantiles",
                            "input_keypoints_type": "fixed",
                            "unimodality": "none",
                            "feature_index": 2,
                            "status": "success",
                        },
                    ],
                }
            ],
        }
    ),
)
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_get_pipeline(mock_version, mock_get_api_key, mock_get):
    """Tests that a trained model is posted correctly."""

    (
        pipeline_metadata,
        last_pipeline_config,
        pipeline_configs,
        trained_model_uuids,
    ) = get_pipeline("test_uuid")
    mock_get.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines/test_uuid",
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()
    assert trained_model_uuids[0] == "test_model_uuid"
    assert pipeline_configs[1].uuid == "test_pipeline_config_uuid"
    assert pipeline_metadata["name"] == "target_classification"
    assert last_pipeline_config == 1


@patch(
    "requests.get",
    return_value=MockResponse(
        {
            "trained_model_metadata": {
                "uuid": "e5433d21-7b48-41e4-93e2-d87c9f33bef8",
                "model_config_id": 1,
                "epochs": 100,
                "learning_rate": 0.01,
                "batch_size": 32,
                "use_sample_weighting": False,
                "train_primary_metric": [0.6956136226654053],
                "validation_primary_metric": [0.7204969525337219],
                "train_loss": [0.5408805320764899],
                "validation_loss": [0.536510161892792],
                "test_primary_metric": 0.7826087474822998,
                "test_loss": 0.4712568339697588,
                "trained_model_sdk_id": None,
            },
            "overall_model_results": {
                "model_config_id": 317,
                "epochs": 100,
                "learning_rate": 0.01,
                "batch_size": 32,
                "test_primary_metric": 0.7826087474822998,
                "test_loss": 0.4712568339697588,
                "train_primary_metric_per_epoch": [
                    0.6437626481056213,
                    0.6544962525367737,
                    0.6522144079208374,
                ],
                "validation_primary_metric_per_epoch": [
                    0.714285671710968,
                    0.7267080545425415,
                    0.7329192757606506,
                ],
                "train_loss_per_epoch": [
                    0.6172197544043537,
                    0.600101311881279,
                    0.5933227655110775,
                ],
                "validation_loss_per_epoch": [
                    0.4814422345862075,
                    0.48776790247917684,
                    0.48770808078051964,
                ],
                "feature_names": [
                    "age",
                    "sex",
                ],
                "feature_importances": [
                    0.21172318895300993,
                    0.3109056738089249,
                    0.11562846497569708,
                    0.0,
                ],
                "linear_coefficients": [
                    0.21172318895300993,
                    0.3109056738089249,
                ],
                "runtime_in_seconds": 1,
            },
            "model_config": {
                "output_min": None,
                "output_max": None,
                "output_calibration": False,
                "output_calibration_num_keypoints": 10,
                "output_initialization": "uniform",
                "output_calibration_input_keypoints_type": "fixed",
                "lattice_size": 2,
                "interpolation": "hypercube",
                "parameterization": "kronecker_factored",
                "num_terms": 2,
                "random_seed": 0,
                "use_bias": True,
                "lattices": "random",
                "model_config_name": "Model 1",
                "model_framework": "pytorch",
                "model_type": "linear",
                "loss_type": "binary",
                "primary_metric": "auc",
                "best_primary_metric": 0.7204969525337219,
                "target_column": "target",
                "target_column_type": "classification",
            },
            "feature_analyses": [
                {
                    "feature_name": "age",
                    "feature_type": "numerical",
                    "statistic_min": 29.0,
                    "statistic_max": 77.0,
                    "statistic_mean": 54.50367647058823,
                    "statistic_median": 55.5,
                    "statistic_std": 8.785850155457481,
                    "keypoints_inputs_numerical": [
                        29.0,
                        39.0,
                        43.0,
                        48.0,
                        52.0,
                        56.0,
                        60.0,
                        65.0,
                        69.0,
                        77.0,
                    ],
                    "keypoints_inputs_categorical": [],
                    "keypoints_outputs": [
                        -2.023148125135339,
                        -1.2120778523877926,
                        -0.6988228320910564,
                        -0.3834010392634607,
                        -0.7148440594259099,
                        -0.2876861882027164,
                        0.06256910105143593,
                        0.6036461743404464,
                        0.2773983506080544,
                        1.5282870069736034,
                    ],
                    "updated_at": "2023-07-24T14:38:21.104913-07:00",
                    "created_at": "2023-07-24T14:38:21.104882-07:00",
                },
                {
                    "feature_name": "sex",
                    "feature_type": "numerical",
                    "statistic_min": 0.0,
                    "statistic_max": 1.0,
                    "statistic_mean": 0.6838235294117647,
                    "statistic_median": 1.0,
                    "statistic_std": 0.4649826986400699,
                    "keypoints_inputs_numerical": [0.0, 1.0],
                    "keypoints_inputs_categorical": [],
                    "keypoints_outputs": [-2.039680783236546, 1.9639668866171704],
                    "updated_at": "2023-07-24T14:38:21.112405-07:00",
                    "created_at": "2023-07-24T14:38:21.112378-07:00",
                },
            ],
            "name": "target_classification",
            "target": "target",
            "target_type": "classification",
            "primary_metric": "auc",
            "shuffle_data": True,
            "drop_empty_percentage": 70,
            "dataset_split": {
                "train_percentage": 80,
                "test_percentage": 10,
                "validation_percentage": 10,
            },
            "trained_model_metadata_uuids": ["test_model_uuid"],
            "pipeline_config": {
                "uuid": "test_pipeline_config_uuid",
                "pipeline_config_sdk_id": 1,
                "shuffle_data": True,
                "drop_empty_percentage": 70,
                "train_percentage": 80,
                "validation_percentage": 10,
                "test_percentage": 10,
                "feature_config_list": [
                    {
                        "feature_name": "age",
                        "feature_type": "numerical",
                        "monotonicity": "none",
                        "num_buckets": 0,
                        "num_keypoints": 10,
                        "input_keypoints": "quantiles",
                        "input_keypoints_type": "fixed",
                        "unimodality": "none",
                        "feature_index": 1,
                        "status": "success",
                    },
                    {
                        "feature_name": "sex",
                        "feature_type": "numerical",
                        "monotonicity": "none",
                        "num_buckets": 0,
                        "num_keypoints": 10,
                        "input_keypoints": "quantiles",
                        "input_keypoints_type": "fixed",
                        "unimodality": "none",
                        "feature_index": 2,
                        "status": "success",
                    },
                ],
            },
        }
    ),
)
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_get_trained_model_metadata(mock_version, mock_get_api_key, mock_get):
    """Tests that a trained model is posted correctly."""

    trained_model_metadata = get_trained_model_metadata("test_uuid")
    mock_get.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/trained-model/test_uuid",
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()
    assert (
        trained_model_metadata.training_config.loss_type == LossType.BINARY_CROSSENTROPY
    )
    assert trained_model_metadata.uuid == "test_uuid"


@patch("requests.get", return_value=MockResponse(["test_dataset_uuid"], 200))
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_get_dataset_uuids(mock_version, mock_get_api_key, mock_get):
    """Tests that inference config retrieval is handled correctly."""
    _, dataset_uuids = get_dataset_uuids("test_uuid")

    mock_get.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines/test_uuid/datasets",
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )

    assert dataset_uuids[0] == "test_dataset_uuid"
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()


@patch("pandas.read_csv", return_value=pd.DataFrame())
@patch("urllib.request.urlretrieve", return_value=None)
@patch(
    "requests.get",
    return_value=MockResponse(
        {
            "train_download_url": "test.com",
            "validation_download_url": "test.com",
            "test_download_url": "test.com",
            "dataset_sdk_id": 1,
            "pipeline_config_sdk_id": 2,
        },
        200,
    ),
)
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_download_prepared_dataset(
    mock_version, mock_get_api_key, mock_get, mock_urlretrieve, mock_pd
):
    """Tests that inference config retrieval is handled correctly."""
    _, dataset = download_prepared_dataset("test_uuid")

    mock_get.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/datasets/test_uuid/download",
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )

    assert dataset.id == 1
    assert dataset.pipeline_config_id == 2

    mock_get_api_key.assert_called_once()
    mock_version.assert_called()
    mock_urlretrieve.assert_has_calls(
        [
            call("test.com", "/tmp/sotai/pipeline/datasets/test_uuid/train.csv"),
            call("test.com", "/tmp/sotai/pipeline/datasets/test_uuid/test.csv"),
            call("test.com", "/tmp/sotai/pipeline/datasets/test_uuid/validation.csv"),
        ]
    )
    mock_pd.assert_has_calls(
        [
            call("/tmp/sotai/pipeline/datasets/test_uuid/train.csv"),
            call("/tmp/sotai/pipeline/datasets/test_uuid/validation.csv"),
            call("/tmp/sotai/pipeline/datasets/test_uuid/test.csv"),
        ]
    )


@patch("builtins.open")
@patch(
    "requests.post",
    return_value=MockResponse({"uuid": "test_shap_uuid"}),
)
@patch("sotai.api.get_api_key", return_value="test_api_key")
@patch("importlib.metadata.version", return_value="0.0.0")
def test_post_external_inference(
    mock_version,
    mock_get_api_key,
    mock_post,
    mock_open_data,
):
    """Tests that feature configs are posted correctly."""
    mock_open_data.return_value = "data"
    pipeline_response = post_external_inference(
        "/tmp/sotai/external/shapley_values.csv",
        "/tmp/sotai/external/base_values.csv",
        "/tmp/sotai/external/inference_predictions.csv",
        "test",
        "target",
        "dataset_name",
    )

    mock_post.assert_called_with(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/shapley-values",
        files=[("files", "data"), ("files", "data"), ("files", "data")],
        data={
            "external_shapley_value_name": "test",
            "target": "target",
            "dataset_name": "dataset_name",
        },
        headers={"sotai-api-key": "test_api_key", "sotai-sdk-version": "0.0.0"},
        timeout=10,
    )
    mock_get_api_key.assert_called_once()
    mock_version.assert_called()

    assert pipeline_response[1] == "test_shap_uuid"
    assert pipeline_response[0] == "success"
