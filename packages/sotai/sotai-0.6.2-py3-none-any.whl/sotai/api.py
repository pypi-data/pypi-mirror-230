"""This module contains the API functions for interacting with the SOTAI API.""" ""
import logging
import os
import tarfile
import urllib
from typing import Any, Dict, List, Optional, Tuple, Type, Union
import importlib.metadata
import pandas as pd
import requests

from .constants import SOTAI_API_ENDPOINT, SOTAI_API_TIMEOUT, SOTAI_BASE_URL
from .enums import APIStatus, InferenceConfigStatus
from .types import (
    Dataset,
    PreparedData,
    CategoricalFeatureConfig,
    DatasetSplit,
    FeatureType,
    HypertuneConfig,
    LinearConfig,
    NumericalFeatureConfig,
    PipelineConfig,
    TrainedModelMetadata,
    TrainingConfig,
    TrainingResults,
    _BaseModelConfig,
)


def set_api_key(api_key: str):
    """Set the SOTAI API key in the environment variables.

    Args:
        api_key: The API key to set.
    """
    os.environ["SOTAI_API_KEY"] = api_key


def get_api_key() -> str:
    """Returns the SOTAI API key from the environment variables."""
    return os.environ["SOTAI_API_KEY"]


def get_auth_headers() -> Dict[str, str]:
    """Returns the authentication headers for a pipeline."""
    return {
        "sotai-api-key": get_api_key(),
        "sotai-sdk-version": importlib.metadata.version("sotai"),
    }


def extract_response(
    api_call: str, response: requests.Response
) -> Tuple[APIStatus, Optional[Any]]:
    """Extract the response from a requests response.

    Args:
        api_call: The name of the API call.
        response: The requests response.

    Returns:
        A tuple containing the status of the API call and JSON response encoded content.
        If unsuccessful, the response will be `None`.
    """
    if response.status_code != 200:
        if response.headers.get("content-type") == "application/json":
            logging.error("API call %s failed. %s", api_call, response.json()["detail"])
        else:
            logging.error("API call %s failed.", api_call)
        return APIStatus.ERROR, None
    return APIStatus.SUCCESS, response.json()


def post_pipeline(pipeline) -> Tuple[APIStatus, Optional[str]]:
    """Create a new pipeline on the SOTAI API.

    Args:
        pipeline: The pipeline to create.

    Returns:
        A tuple containing the status of the API call and the UUID of the created
        pipeline. If unsuccessful, the UUID will be `None`.
    """
    response = requests.post(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines",
        json={
            "name": pipeline.name,
            "target": pipeline.target,
            "target_column_type": pipeline.target_type,
            "primary_metric": pipeline.primary_metric,
        },
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("post_pipeline", response)
    if api_status == APIStatus.ERROR:
        return api_status, None

    return api_status, response_json["uuid"]


def post_pipeline_config(
    pipeline_uuid: str, pipeline_config: PipelineConfig
) -> Tuple[APIStatus, Optional[str]]:
    """Create a new pipeline config on the SOTAI API.

    Args:
        pipeline_uuid: The pipeline uuid to create the pipeline config for.
        pipeline_config : The pipeline config to create.

    Returns:
        A tuple containing the status of the API call and the UUID of the created
        pipeline. If unsuccessful, the UUID will be `None`.
    """
    response = requests.post(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines/{pipeline_uuid}/pipeline-configs",
        json={
            "shuffle_data": pipeline_config.shuffle_data,
            "drop_empty_percentage": pipeline_config.drop_empty_percentage,
            "train_percentage": pipeline_config.dataset_split.train,
            "validation_percentage": pipeline_config.dataset_split.val,
            "test_percentage": pipeline_config.dataset_split.test,
            "pipeline_config_sdk_id": pipeline_config.id,
        },
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("post_pipeline_config", response)
    if api_status == APIStatus.ERROR:
        return api_status, None

    return APIStatus.SUCCESS, response_json["uuid"]


def post_pipeline_feature_configs(
    pipeline_config_uuid: str,
    feature_configs: Dict[str, Union[CategoricalFeatureConfig, NumericalFeatureConfig]],
) -> APIStatus:
    """Create a new pipeline feature configs on the SOTAI API.

    Args:
        pipeline_config_uuid: The pipeline config uuid to create the pipeline
            feature configs for.
        feature_configs: The feature configs to create.

    Returns:
        The status of the API call.
    """
    sotai_feature_configs = []

    for feature_config in feature_configs.values():
        sotai_feature_config = {
            "feature_name": feature_config.name,
            "feature_type": feature_config.type,
        }
        if feature_config.type == FeatureType.CATEGORICAL:
            if isinstance(feature_config.categories[0], int):
                sotai_feature_config["categories_int"] = feature_config.categories
            else:
                sotai_feature_config["categories_str"] = feature_config.categories
        else:
            sotai_feature_config["num_keypoints"] = feature_config.num_keypoints
            sotai_feature_config[
                "input_keypoints_init"
            ] = feature_config.input_keypoints_init
            sotai_feature_config[
                "input_keypoints_type"
            ] = feature_config.input_keypoints_type
            sotai_feature_config["monotonicity"] = feature_config.monotonicity

        sotai_feature_configs.append(sotai_feature_config)

    response = requests.post(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipeline-configs/"
        f"{pipeline_config_uuid}/feature-configs",
        json=sotai_feature_configs,
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, _ = extract_response("post_pipeline_feature_configs", response)

    return api_status


def post_trained_model_analysis(
    pipeline_config_uuid: str, trained_model: TrainedModelMetadata
) -> Tuple[APIStatus, Optional[Dict[str, str]]]:
    """Create a new trained model analysis on the SOTAI API.

    Args:
        pipeline_config_uuid: The pipeline config uuid to create the trained model
            analysis for.
        trained_model: The trained model to create.

    Returns:
        A tuple containing the status of the API call and a dict containing the UUIDs
        of the resources created as well as a link that can be used to view the trained
        model analysis. If unsuccessful, the UUID will be `None`.

        Keys:
            - `trained_model_metadata_uuid`: The UUID of the trained model.
            - `model_config_uuid`: The UUID of the model configuration.
            - `pipeline_config_uuid`: The UUID of the pipeline configuration.
            - `analysis_url`: The URL of the trained model analysis.
    """
    training_results = trained_model.training_results
    train_primary_metrics = training_results.train_primary_metric_by_epoch
    val_primary_metrics = training_results.val_primary_metric_by_epoch
    overall_model_results_dict = {
        "epochs": trained_model.training_config.epochs,
        "batch_size": trained_model.training_config.batch_size,
        "learning_rate": trained_model.training_config.learning_rate,
        "runtime_in_seconds": round(training_results.training_time),
        "train_loss_per_epoch": training_results.train_loss_by_epoch,
        "train_primary_metric_per_epoch": train_primary_metrics,
        "validation_loss_per_epoch": training_results.val_loss_by_epoch,
        "validation_primary_metric_per_epoch": val_primary_metrics,
        "test_loss": training_results.test_loss,
        "test_primary_metric": training_results.test_primary_metric,
        "feature_names": [
            feature.feature_name for feature in trained_model.model.features
        ],
        "linear_coefficients": [
            training_results.linear_coefficients[feature.feature_name]
            for feature in trained_model.model.features
        ],
    }
    feature_analyses_list = [
        {
            "feature_name": feature.feature_name,
            "feature_type": feature.feature_type.value,
            "statistic_min": feature.min,
            "statistic_max": feature.max,
            "statistic_mean": feature.mean,
            "statistic_median": feature.median,
            "statistic_std": feature.std,
            "keypoints_outputs": feature.keypoints_outputs,
            "keypoints_inputs_categorical": feature.keypoints_inputs_categorical,
            "keypoints_inputs_numerical": feature.keypoints_inputs_numerical,
        }
        for feature in trained_model.training_results.feature_analyses.values()
    ]
    trained_model_metadata_dict = {
        "epochs": trained_model.training_config.epochs,
        "batch_size": trained_model.training_config.batch_size,
        "learning_rate": trained_model.training_config.learning_rate,
        "train_primary_metric": [training_results.train_primary_metric_by_epoch[-1]],
        "validation_primary_metric": [training_results.val_primary_metric_by_epoch[-1]],
        "test_primary_metric": training_results.test_primary_metric,
        "trained_model_sdk_id": trained_model.id,
    }

    model_config_dict = {
        "model_framework": "pytorch",
        "model_type": "linear",
        "loss_type": trained_model.training_config.loss_type.value,
        "primary_metric": trained_model.pipeline_config.primary_metric.value,
        "target_column_type": trained_model.pipeline_config.target_type.value,
        "target_column": trained_model.pipeline_config.target,
        "model_config_name": f"Model {trained_model.id}",
    }

    response = requests.post(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipeline-configs/{pipeline_config_uuid}/analysis",
        json={
            "trained_model_metadata": trained_model_metadata_dict,
            "overall_model_results": overall_model_results_dict,
            "model_config": model_config_dict,
            "feature_analyses": feature_analyses_list,
        },
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    return extract_response("post_trained_model_analysis", response)


def post_trained_model(trained_model_path: str, trained_model_uuid: str) -> APIStatus:
    """Create a new trained model on the SOTAI API.

    Args:
        trained_model_path: The path to the trained model file to post.
        trained_model_uuid: The UUID of the trained model.

    Returns:
        The status of the API call.
    """
    original_filepath = f"{trained_model_path}/trained_ptcm_model.pt"
    tar_filepath = f"{trained_model_path}/model.tar.gz"
    with tarfile.open(tar_filepath, "w:gz") as tar:
        tar.add(original_filepath, arcname="model.pt")

    with open(tar_filepath, "rb") as data_file:
        response = requests.post(
            f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/models",
            files={"file": data_file},
            data={"trained_model_metadata_uuid": trained_model_uuid},
            headers=get_auth_headers(),
            timeout=SOTAI_API_TIMEOUT,
        )

    api_status, _ = extract_response("post_trained_model", response)
    return api_status


def post_inference(
    data_filepath: str,
    trained_model_uuid: str,
) -> Tuple[APIStatus, Optional[str]]:
    """Create a new inference on the SOTAI API .

    Args:
        data_filepath: The path to the data file to create the inference for.
        trained_model_uuid: The trained model uuid to create the inference for.

    Returns:
        A tuple containing the status of the API call and the UUID of the created
        inference job. If unsuccessful, the UUID will be `None`.
    """
    with open(data_filepath, "rb") as data_file:
        response = requests.post(
            f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/inferences",
            files={"file": data_file},
            data={"trained_model_metadata_uuid": trained_model_uuid},
            headers=get_auth_headers(),
            timeout=SOTAI_API_TIMEOUT,
        )

    api_status, response_json = extract_response("post_trained_model", response)
    if api_status == APIStatus.ERROR:
        return api_status, None

    return api_status, response_json["inference_config_uuid"]


def get_inference_status(
    inference_uuid: str,
) -> Tuple[APIStatus, Optional[InferenceConfigStatus]]:
    """Get an inference from the SOTAI API.

    Args:
        inference_uuid: The UUID of the inference to get.

    Returns:
       A tuple containing the status of the API call and the status of the inference job
       if the API call is successful. If unsuccessful, the UUID will be `None`.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/inferences/{inference_uuid}/status",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    return extract_response("get_inference_status", response)


def get_inference_results(inference_uuid: str, download_folder: str) -> APIStatus:
    """Get an inference from the SOTAI API.

    Args:
        inference_uuid: The UUID of the inference results to get.

    Returns:
        The status of the API call.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/inferences/{inference_uuid}/download",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("get_inference_results", response)
    if api_status == APIStatus.ERROR:
        return api_status

    urllib.request.urlretrieve(
        response_json, f"{download_folder}/inference_results.csv"
    )
    return api_status


def post_dataset(
    train_filepath: str,
    test_filepath: str,
    validation_filepath: str,
    columns: List[str],
    categorical_columns: List[str],
    pipeline_config_uuid: str,
    dataset_id: int,
) -> Tuple[APIStatus, Optional[str]]:
    """Upload a dataset to th the SOTAI API.

    Args:
        data_filepath: The path to the data file to push to the API.
        columns: The columns of the dataset.
        categorical_columns: The categorical columns of the dataset.
        pipeline_uuid: The pipeline uuid for which to upload the dataset.

    Returns:
        A tuple containing the status of the API call and the UUID of the created
        dataset. If unsuccessful, the UUID will be `None`.
    """

    response = requests.post(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/datasets",
        files=[
            ("files", open(test_filepath, "rb")),  # pylint: disable=consider-using-with
            (
                "files",
                open(train_filepath, "rb"),  # pylint: disable=consider-using-with
            ),
            (
                "files",
                open(validation_filepath, "rb"),  # pylint: disable=consider-using-with
            ),
        ],
        data={
            "pipeline_config_uuid": pipeline_config_uuid,
            "columns": columns,
            "categorical_columns": categorical_columns,
            "dataset_sdk_id": dataset_id,
        },
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("post_dataset", response)
    if api_status == APIStatus.ERROR:
        return api_status, None
    return api_status, response_json["uuid"]


def post_hypertune_job(
    hypertune_config: HypertuneConfig,
    pipeline_config: PipelineConfig,
    model_config: Type[_BaseModelConfig],
    dataset_uuid: str,
    next_model_id: int,
):
    """Upload a dataset to th the SOTAI API.

    Args:
        hypertune_config: The hypertune config to create the hypertune job for.
        pipeline_config: The pipeline config to create the hypertune job for.
        dataset_uuid: The dataset uuid to create the hypertune job for.

    Returns:
        A tuple containing the status of the API call and an array of the UUIDs of the
        created trained models. If unsuccessful, the UUIDs will be `None`.
    """

    input_keypoints_type = model_config.output_calibration_input_keypoints_type
    advanced_options = {
        "output_min": model_config.output_min,
        "output_max": model_config.output_max,
        "output_calibration": model_config.output_calibration,
        "output_calibration_num_keypoints": model_config.output_calibration_num_keypoints,
        "output_initialization": model_config.output_initialization,
        "output_calibration_input_keypoints_type": input_keypoints_type,
    }
    if isinstance(model_config, LinearConfig):
        advanced_options["use_bias"] = model_config.use_bias

    response = requests.post(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipeline-config/{pipeline_config.uuid}/hypertune",
        json={
            "dataset_uuid": dataset_uuid,
            "training_config": {
                "epochs_options": hypertune_config.epochs,
                "batch_size_options": hypertune_config.batch_sizes,
                "learning_rate_options": hypertune_config.learning_rates,
                "num_cpus_per_job": 2,
                "num_parallel_jobs": 4,
            },
            "model_config": {
                "model_framework": "pytorch",
                "model_config_name": f"Model {pipeline_config.id}",
                "model_type": "linear",
                "target_column_type": pipeline_config.target_type.value,
                "target_column": pipeline_config.target,
                "primary_metric": pipeline_config.primary_metric.value,
                "selected_features": list(pipeline_config.feature_configs.keys()),
                "loss_type": hypertune_config.loss_type.value,
                "advanced_options": advanced_options,
            },
            "next_model_id": next_model_id,
        },
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("post_hypertune_job", response)
    if api_status == APIStatus.ERROR:
        return api_status, None
    return api_status, response_json["trained_model_metadata_uuids"]


def _parse_pipeline_config(
    pipeline_config_json: Dict[str, Any], update_dict: Dict[str, Any]
) -> PipelineConfig:
    """Parse a pipeline config from the SOTAI API.

    Args:
        pipeline_config_json: The pipeline config JSON to parse.
        update_dict: The dictionary with which to update the pipeline config.

    Returns:
        The parsed pipeline config.
    """
    pipeline_config = {}
    pipeline_config.update(pipeline_config_json)
    pipeline_config.update(update_dict)
    pipeline_config["dataset_split"] = DatasetSplit(
        train=pipeline_config_json["train_percentage"],
        val=pipeline_config_json["validation_percentage"],
        test=pipeline_config_json["test_percentage"],
    )
    feature_configs = {}
    for feature in pipeline_config_json["feature_config_list"]:
        feature["name"] = feature["feature_name"]
        feature["type"] = feature["feature_type"]
        if feature["feature_type"] == "categorical":
            if feature["categories_str"]:
                feature["categories"] = feature["categories_str"]
                del feature["categories_str"]
            else:
                feature["categories"] = feature["categories_int"]
                del feature["categories_int"]
            feature_configs[feature["name"]] = CategoricalFeatureConfig(**feature)
        else:
            feature_configs[feature["name"]] = NumericalFeatureConfig(**feature)

    pipeline_config["feature_configs"] = feature_configs
    pipeline_config["id"] = pipeline_config_json["pipeline_config_sdk_id"]
    pipeline_config["allow_hosting"] = True
    return PipelineConfig(**pipeline_config)


def get_pipeline(
    pipeline_uuid: str,
) -> Union[None, Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], List[str]]]:
    """Get a pipeline from the SOTAI API.

    Args:
        pipeline_uuid: The UUID of the pipeline to get.

    Returns:
        A tuple containing the metadata for the pipeline, the id for the most recent
        config of the pipeline, the pipeline configs for the pipeline, and the UUIDs
        of the trainedmodels for the pipeline. If unsuccessful, returns `None`.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines/{pipeline_uuid}",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("get_pipeline", response)
    if api_status == APIStatus.ERROR:
        return None

    pipeline_metadata = {
        "name": response_json["name"],
        "target": response_json["target"],
        "target_type": response_json["target_type"],
        "primary_metric": response_json["primary_metric"],
        "shuffle_data": response_json["shuffle_data"],
        "drop_empty_percentage": response_json["drop_empty_percentage"],
    }

    last_config_id = -1
    pipeline_configs = {}

    for pipeline_config_json in response_json["pipeline_configs"]:
        pipeline_config = _parse_pipeline_config(
            pipeline_config_json, pipeline_metadata
        )
        last_config_id = max(last_config_id, pipeline_config.id)
        pipeline_configs[pipeline_config.id] = pipeline_config
    last_config = pipeline_configs[last_config_id]
    pipeline_metadata["dataset_split"] = last_config.dataset_split
    trained_model_uuids = response_json["trained_model_metadata_uuids"]
    return pipeline_metadata, last_config_id, pipeline_configs, trained_model_uuids


def get_trained_model_uuids(pipeline_uuid: str) -> List[str]:
    """Get the UUIDs of the trained models for a pipeline from the SOTAI API.

    Args:
        pipeline_uuid: The UUID of the pipeline to get the trained models for.

    Returns:
        The UUIDs of the trained models for the pipeline.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines/{pipeline_uuid}/trained-models",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, _ = extract_response("get_trained_model_uuids", response)
    if api_status == APIStatus.ERROR:
        return []

    return [trained_model["uuid"] for trained_model in response.json()]


def get_trained_model_metadata(
    trained_model_uuid: str,
) -> Optional[TrainedModelMetadata]:
    """Get the metadata for a TrainedModelfrom the SOTAI API.

    Args:
        trained_model_uuid: The UUID of the trained model to get.

    Returns:
        The metadata for the trained model if training is complete, otherwise `None`.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/trained-model/{trained_model_uuid}",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    _, response_json = extract_response("get_trained_model_metadata", response)
    if response_json["overall_model_results"] is None:
        return APIStatus.ERROR, None

    trained_model_metadata_json = response_json["trained_model_metadata"]
    overall_model_results = response_json["overall_model_results"]
    model_config = response_json["model_config"]
    pipeline_config_json = response_json["pipeline_config"]
    feature_analyses = response_json["feature_analyses"]
    trained_model_metadata = {
        "id": trained_model_metadata_json["trained_model_sdk_id"],
        "model_config": LinearConfig(
            output_calibration=model_config["output_calibration"],
            output_calibration_num_keypoints=model_config[
                "output_calibration_num_keypoints"
            ],
            output_initialization=model_config["output_initialization"],
            output_min=model_config["output_min"],
            output_max=model_config["output_max"],
            output_calibration_input_keypoints_type=model_config[
                "output_calibration_input_keypoints_type"
            ],
            use_bias=model_config["use_bias"],
        ),
        "training_config": TrainingConfig(
            epochs=trained_model_metadata_json["epochs"],
            batch_size=overall_model_results["batch_size"],
            learning_rate=overall_model_results["learning_rate"],
            loss_type=model_config["loss_type"],
        ),
        "training_results": TrainingResults(
            training_time=overall_model_results["runtime_in_seconds"],
            train_loss_by_epoch=overall_model_results["train_loss_per_epoch"],
            train_primary_metric_by_epoch=overall_model_results[
                "train_primary_metric_per_epoch"
            ],
            val_loss_by_epoch=overall_model_results["validation_loss_per_epoch"],
            val_primary_metric_by_epoch=overall_model_results[
                "validation_primary_metric_per_epoch"
            ],
            evaluation_time=overall_model_results["runtime_in_seconds"],
            test_loss=overall_model_results["test_loss"],
            test_primary_metric=overall_model_results["test_primary_metric"],
            feature_analyses={
                feature["feature_name"]: {
                    "feature_name": feature["feature_name"],
                    "feature_type": feature["feature_type"],
                    "min": feature["statistic_min"],
                    "max": feature["statistic_max"],
                    "mean": feature["statistic_mean"],
                    "median": feature["statistic_median"],
                    "std": feature["statistic_std"],
                    "keypoints_outputs": feature["keypoints_outputs"],
                    "keypoints_inputs_categorical": feature[
                        "keypoints_inputs_categorical"
                    ],
                    "keypoints_inputs_numerical": feature["keypoints_inputs_numerical"],
                }
                for feature in feature_analyses
            },
            linear_coefficients=dict(
                zip(
                    overall_model_results["feature_names"],
                    overall_model_results["linear_coefficients"],
                )
            ),
        ),
        "pipeline_config": _parse_pipeline_config(
            pipeline_config_json,
            {
                "target": model_config["target_column"],
                "target_type": model_config["target_column_type"],
                "primary_metric": model_config["primary_metric"],
            },
        ),
        "uuid": trained_model_uuid,
        "allow_hosting": True,
    }
    return TrainedModelMetadata(**trained_model_metadata)


def download_trained_model(trained_model_uuid: str) -> str:
    """Download a trained model from the SOTAI API to a local tmp directory.

    Args:
        trained_model_uuid: The UUID of the trained model to download.

    Returns:
        The path to the downloaded model.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/trained-model/{trained_model_uuid}/download",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    download_folder = f"/tmp/sotai/pipeline/trained_models/{trained_model_uuid}"
    download_path = f"{download_folder}/model.tar.gz"
    model_file_path = f"{download_folder}/model.pt"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    urllib.request.urlretrieve(response.json(), download_path)

    with tarfile.open(download_path) as model_file:
        model_file.extractall(download_folder)
    return model_file_path


def get_dataset_uuids(pipeline_uuid: str) -> Tuple[APIStatus, List[str]]:
    """Returns the UUIDs of the datasets for a pipeline from the SOTAI API.

    Args:
        pipeline_uuid: The UUID of the pipeline to get the datasets for.

    Returns:
        A tuple containing the status of the API call and the UUIDs of the datasets for
        the pipeline. If unsuccessful, the UUIDs will be `None`.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/pipelines/{pipeline_uuid}/datasets",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    return extract_response("get_dataset_uuids", response)


def download_prepared_dataset(dataset_uuid: str) -> Tuple[APIStatus, Optional[Dataset]]:
    """Download a dataset from the SOTAI API.

    Args:
        trained_model_uuid: The UUID of the trained model to download.

    Returns:
        A tuple containing the status of the API call and the downloaded Dataset. If
        unsuccessful, the dataset will be `None`.
    """
    response = requests.get(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/datasets/{dataset_uuid}/download",
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("download_prepared_dataset", response)
    if api_status == APIStatus.ERROR:
        return api_status, None

    download_folder = f"/tmp/sotai/pipeline/datasets/{dataset_uuid}"
    train_download_path = f"{download_folder}/train.csv"
    test_download_path = f"{download_folder}/test.csv"
    validation_download_path = f"{download_folder}/validation.csv"
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    urllib.request.urlretrieve(response_json["train_download_url"], train_download_path)
    urllib.request.urlretrieve(response_json["test_download_url"], test_download_path)
    urllib.request.urlretrieve(
        response_json["validation_download_url"], validation_download_path
    )

    return APIStatus.SUCCESS, Dataset(
        prepared_data=PreparedData(
            train=pd.read_csv(train_download_path),
            val=pd.read_csv(validation_download_path),
            test=pd.read_csv(test_download_path),
        ),
        id=response_json["dataset_sdk_id"],
        pipeline_config_id=response_json["pipeline_config_sdk_id"],
        allow_hosting=True,
    )


def post_external_inference(
    shap_filepath: str,
    base_filepath: str,
    inference_filepath: str,
    external_shapley_value_name: str,
    target: str,
    dataset_name: str,
) -> Tuple[APIStatus, Optional[str]]:
    """Upload inference + shap values to the SOTAI API.

    Args:
        shap_filepath: The path to the shap values file to push to the API.
        base_filepath: The path to the base file to push to the API.
        inference_filepath: The path to the inference file to push to the API.
        external_shapley_value_name: The name of the external shapley value to create.
        target: The target column of the dataset.
        dataset_name: The name of the dataset.

    Returns:
        A tuple containing the status of the API call and the UUID of the created
        inference job. If unsuccessful, the UUID will be `None`.
    """

    response = requests.post(
        f"{SOTAI_BASE_URL}/{SOTAI_API_ENDPOINT}/shapley-values",
        files=[
            ("files", open(shap_filepath, "rb")),  # pylint: disable=consider-using-with
            (
                "files",
                open(base_filepath, "rb"),  # pylint: disable=consider-using-with
            ),
            (
                "files",
                open(inference_filepath, "rb"),  # pylint: disable=consider-using-with
            ),
        ],
        data={
            "external_shapley_value_name": external_shapley_value_name,
            "target": target,
            "dataset_name": dataset_name,
        },
        headers=get_auth_headers(),
        timeout=SOTAI_API_TIMEOUT,
    )

    api_status, response_json = extract_response("post_external_inference", response)
    if api_status == APIStatus.ERROR:
        return api_status, None
    return api_status, response_json["uuid"]
