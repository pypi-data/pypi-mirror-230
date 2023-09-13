"""A Pipeline for calibrated modeling."""
from __future__ import annotations

import logging
import os
import pickle
from time import sleep
from typing import Dict, List, Optional, Tuple, Union
import itertools
import numpy as np
import pandas as pd

from .api import (
    download_prepared_dataset,
    get_api_key,
    get_dataset_uuids,
    get_inference_results,
    get_inference_status,
    get_trained_model_uuids,
    post_inference,
    post_pipeline,
    post_pipeline_config,
    post_pipeline_feature_configs,
    post_trained_model,
    post_trained_model_analysis,
    post_dataset,
    get_pipeline,
    post_hypertune_job,
)
from .constants import INFERENCE_POLLING_INTERVAL, SOTAI_BASE_URL
from .data import determine_feature_types, replace_missing_values
from .enums import (
    APIStatus,
    FeatureType,
    InferenceConfigStatus,
    LossType,
    Metric,
    TargetType,
)
from .trained_model import TrainedModel
from .training import train_and_evaluate_model
from .types import (
    CategoricalFeatureConfig,
    Dataset,
    DatasetSplit,
    LinearConfig,
    NumericalFeatureConfig,
    PipelineConfig,
    PreparedData,
    TrainingConfig,
    HypertuneConfig,
)


class Pipeline:  # pylint: disable=too-many-instance-attributes
    """A pipeline for calibrated modeling.

    The pipeline defines the configuration for training a calibrated model. The
    pipeline itself defines the features, target, and target type to be used. When
    training a model, the data and configuration used will be versioned and stored in
    the pipeline. The pipeline can be used to train multiple models with different
    configurations if desired; however, the target, target type, and primary metric
    should not be changed after initialization so that models trained by this pipeline
    can be compared.

    Example:
    ```python
    data = pd.read_csv(...)
    pipeline = Pipeline(features, target, TargetType.CLASSIFICATION)
    trained_model = pipeline.train(data)
    ```

    Attributes:
        name: The name of the pipeline.
        target: The name of the target column.
        target_type: The type of the target column.
        primary_metric: The primary metric to use for training and evaluation.
        feature_configs: A dictionary mapping feature names to feature configurations.
        shuffle_data: Whether or not to shuffle the data before training.
        drop_empty_percentage: The percentage of empty values in a single row that will
            result in dropping the row before training.
        dataset_split: The dataset split to use for training and evaluation.
        configs: A dictionary mapping versioned pipeline configuration IDs to pipeline
            configurations.
        datasets: A dictionary mapping versioned dataset IDs to datasets.
        uuid: The UUID of the pipeline. This will be `None` unless the pipeline has been
            published.
        trained_models: A dictionary mapping trained model UUIDs to trained models.
    """

    def __init__(
        self,
        features: List[str],
        target: str,
        target_type: TargetType,
        categories: Optional[Dict[str, Union[List[int], List[str]]]] = None,
        primary_metric: Optional[Metric] = None,
        name: Optional[str] = None,
        default_allow_hosting: bool = True,
    ):
        """Initializes an instance of `Pipeline`.

        The pipeline is initialized with a default config, which can be modified later.
        The target type can be optionally specfified. The default primary metric will be
        AUC for classification and Mean Squared Error for regression if not specified.

        Args:
            features: The column names in your data to use as features.
            target: The name of the target column.
            target_type: The type of the target column.
            categories: A dictionary mapping feature names to unique categories. Any
                values not in the categories list for a given feature will be treated
                as a missing value.
            primary_metric: The primary metric to use for training and evaluation.
            name: The name of the pipeline. If not provided, the name will be set to
                `{target}_{target_type}`.
            default_allow_hosting: Whether or not to allow hosting by default for
                datasets and models created by this pipeline.
        """
        self.name: str = name if name else f"{target}_{target_type}"
        self.target: str = target
        self.target_type: TargetType = target_type
        self.default_allow_hosting: bool = default_allow_hosting

        self.primary_metric: Metric = (
            primary_metric
            if primary_metric is not None
            else (
                Metric.AUC
                if self.target_type == TargetType.CLASSIFICATION
                else Metric.MSE
            )
        )
        self.feature_configs: Dict[
            str, Union[CategoricalFeatureConfig, NumericalFeatureConfig]
        ] = {
            feature_name: (
                CategoricalFeatureConfig(
                    name=feature_name,
                    categories=categories[feature_name],
                )
                if categories and feature_name in categories
                else NumericalFeatureConfig(name=feature_name)
            )
            for feature_name in features
        }
        self.shuffle_data: bool = True
        self.drop_empty_percentage: int = 70
        self.dataset_split: DatasetSplit = DatasetSplit(train=80, val=10, test=10)

        # Maps a pipeline config id to its corresponding `PipelineConfig`` instance.
        self.configs: Dict[int, PipelineConfig] = {}
        # Maps a dataset id to its corresponding `Dataset`` instance.
        self.datasets: Dict[int, Dataset] = {}

        # Maps a trained model id to its corresponding `TrainedModel`` instance.
        self.trained_models: Dict[int, TrainedModel] = {}

        # Tracking for the next versioned config, dataset, and model.
        self._next_config_id = 0
        self._next_dataset_id = 0
        self._next_model_id = 0

        # Tracks
        self.uuid = None

    def prepare(  # pylint: disable=too-many-locals
        self,
        data: pd.DataFrame,
        pipeline_config_id: Optional[int] = None,
    ) -> Tuple[Dataset, PipelineConfig]:
        """Prepares the data and versions it along with the current pipeline config.

        If any features in data are detected as non-numeric, the pipeline will attempt
        to handle them as categorical features. Any features that the pipeline cannot
        handle will be skipped.

        Args:
            data: The raw data to be prepared for training.
            pipeline_config_id: The id of the pipeline config to be used for training.
                If not provided, the current pipeline config will be used and versioned.

        Returns:
            A tuple of the versioned dataset and pipeline config.
        """
        data.replace("", np.nan, inplace=True)  # treat empty strings as NaN
        if pipeline_config_id is None:
            pipeline_config = self._version_pipeline_config(data)
        else:
            pipeline_config = self.configs[pipeline_config_id]

        if (
            pipeline_config.target_type == TargetType.CLASSIFICATION
            and data[pipeline_config.target].dtype != np.int64
            and data[pipeline_config.target].unique().sort() != [0, 1]
        ):
            raise ValueError(
                "Target column must be of type int64 with values [0,1] for classification."
            )

        # Select only the features defined in the pipeline config.
        data = data[list(pipeline_config.feature_configs.keys()) + [self.target]]
        # Drop rows with too many missing values according to the drop empty percent.
        max_num_empty_columns = int(
            (pipeline_config.drop_empty_percentage * data.shape[1]) / 100
        )
        data = data[data.isnull().sum(axis=1) <= max_num_empty_columns]
        # Replace any missing values (i.e. NaN) with missing value constants.
        data = replace_missing_values(data, pipeline_config.feature_configs)
        if pipeline_config.shuffle_data:
            data = data.sample(frac=1).reset_index(drop=True)
        train_percentage = pipeline_config.dataset_split.train / 100
        train_data = data.iloc[: int(len(data) * train_percentage)]
        val_percentage = pipeline_config.dataset_split.val / 100
        val_data = data.iloc[
            int(len(data) * train_percentage) : int(
                len(data) * (train_percentage + val_percentage)
            )
        ]
        test_data = data.iloc[int(len(data) * (train_percentage + val_percentage)) :]

        dataset_id = self._next_dataset_id
        self._next_dataset_id += 1
        dataset = Dataset(
            id=dataset_id,
            pipeline_config_id=pipeline_config.id,
            prepared_data=PreparedData(train=train_data, val=val_data, test=test_data),
            allow_hosting=self.default_allow_hosting,
        )
        self.datasets[dataset_id] = dataset

        return dataset, pipeline_config

    def train(
        self,
        data: Union[pd.DataFrame, int],
        pipeline_config_id: Optional[int] = None,
        model_config: Optional[LinearConfig] = None,
        training_config: Optional[TrainingConfig] = None,
    ) -> TrainedModel:
        """Returns a calibrated model trained according to the given configs.

        Args:
            data: The raw data to be prepared and trained on. If an int is provided,
                it is assumed to be a dataset id and the corresponding dataset will be
                used.
            pipeline_config_id: The id of the pipeline config to be used for training.
                If not provided, the current pipeline config will be versioned and used.
                If data is an int, this argument is ignored and the pipeline config used
                to prepare the data with the given id will be used.
            model_config: The config to be used for training the model. If not provided,
                a default config will be used.
            training_config: The config to be used for training the model. If not
                provided, a default config will be used.

        Returns:
            A `TrainedModel` instance.
        """
        if isinstance(data, int):
            dataset = self.datasets[data]
            pipeline_config = self.configs[dataset.pipeline_config_id]
        else:
            dataset, pipeline_config = self.prepare(data, pipeline_config_id)

        if model_config is None:
            model_config = LinearConfig()

        if training_config is None:
            training_config = TrainingConfig(
                loss_type=LossType.BINARY_CROSSENTROPY
                if self.target_type == TargetType.CLASSIFICATION
                else LossType.MSE
            )

        model, training_results = train_and_evaluate_model(
            dataset,
            self.target,
            self.primary_metric,
            pipeline_config,
            model_config,
            training_config,
        )
        trained_model = TrainedModel(
            id=self._next_model_id,
            dataset_id=dataset.id,
            pipeline_config=pipeline_config,
            model_config=model_config,
            training_config=training_config,
            training_results=training_results,
            model=model,
            allow_hosting=self.default_allow_hosting,
        )

        self.trained_models[self._next_model_id] = trained_model
        self._next_model_id += 1
        return trained_model

    def hypertune(
        self,
        data: Union[int, pd.DataFrame],
        hypertune_config: HypertuneConfig,
        pipeline_config_id: Optional[int] = None,
        model_config: Optional[LinearConfig] = None,
        hosted: bool = False,
    ) -> List[Union[TrainedModel, str]]:
        """Returns a list of trained models trained according to the given configs.

        Args:
            data: The raw data to be prepared and trained on. If an int is provided,
                it is assumed to be a dataset id and the corresponding dataset will be
                used.
            hypertune_config: The config to be used for hypertuning the model.
            pipeline_config_id: The id of the pipeline config to be used for training.
                If not provided, the current pipeline config will be versioned and used.
                If data is an int, this argument is ignored and the pipeline config used
                to prepare the data with the given id will be used.
            model_config: The config to be used for training the model. If not provided,
                a default config will be used.
            hosted: Whether to run the hypertune job on the SOTAI cloud. If False, the
                hypertune job will be run locally.

        Returns:
            A list of `TrainedModel` instances if run locally, or a list of trained
            model uuids if run in the SOTAI cloud.
        """

        if pipeline_config_id is None:
            pipeline_config = self._version_pipeline_config(data)
            pipeline_config_id = pipeline_config.id
        else:
            pipeline_config = self.configs[pipeline_config_id]

        if model_config is None:
            model_config = LinearConfig()

        if hosted:
            if not get_api_key():
                raise ValueError(
                    "You must have an API key to run hosted hypertuning."
                    " Please visit app.sotai.ai to get an API key."
                )

            _ = self._post_pipeline_config(pipeline_config=pipeline_config)

            dataset_uuid = self._upload_dataset(self.uuid, data, pipeline_config_id)
            if dataset_uuid is None:
                return []

            hypertune_response, trained_model_uuids = post_hypertune_job(
                hypertune_config,
                pipeline_config,
                model_config,
                dataset_uuid,
                self._next_model_id,
            )
            if hypertune_response == APIStatus.ERROR:
                return []

            self._next_model_id += len(trained_model_uuids)
            return trained_model_uuids

        return self._local_hypertuning(
            hypertune_config=hypertune_config,
            data=data,
            pipeline_config_id=pipeline_config.id,
            model_config=model_config,
        )

    def publish(self) -> Optional[str]:
        """Uploads the pipeline to the SOTAI web client.

        Returns:
            If the pipeline was successfully uploaded, the pipeline UUID.
            Otherwise, None.
        """
        pipeline_response_status, pipeline_uuid = post_pipeline(self)
        if pipeline_response_status == APIStatus.ERROR:
            return None

        self.uuid = pipeline_uuid
        return self.uuid

    def analysis(  # pylint: disable=too-many-return-statements
        self,
        trained_model: TrainedModel,
    ) -> Optional[str]:
        """Charts the results for the specified trained model in the SOTAI web client.

        This function requires an internet connection and a SOTAI account. The trained
        model will be uploaded to the SOTAI web client for analysis.

        If you would like to analyze the results for a trained model without uploading
        it to the SOTAI web client, the data is available in `training_results`.

        Args:
            trained_model: The trained model to be analyzed.

        Returns:
            If the analysis was successfully run, the analysis URL. Otherwise `None`.
        """
        if trained_model.analysis_url:  # early exit if analysis has already been run.
            return trained_model.analysis_url

        if not get_api_key():
            raise ValueError(
                "You must have an API key to run analysis."
                " Please visit app.sotai.ai to get an API key."
            )

        pipeline_config_uuid = self._post_pipeline_config(trained_model.pipeline_config)

        if not pipeline_config_uuid:
            return None

        analysis_response_status, analysis_results = post_trained_model_analysis(
            pipeline_config_uuid, trained_model
        )

        if analysis_response_status == APIStatus.ERROR:
            return None

        trained_model.uuid = analysis_results["trained_model_metadata_uuid"]

        upload_response = self._upload_model(trained_model)
        if upload_response == APIStatus.ERROR:
            return None

        # TODO: update to use response analysisUrl once no longer broken.
        analysis_url = (
            f"{SOTAI_BASE_URL}/pipelines/{self.uuid}"
            f"/trained-models/{trained_model.uuid}/overall-model-results"
        )
        trained_model.analysis_url = analysis_url

        return analysis_url

    def inference(
        self,
        filepath: str,
        trained_model: TrainedModel,
    ) -> Optional[str]:
        """Runs inference on a dataset with a trained model in the SOTAI cloud.

        Args:
            inference_dataset_path: The path to the dataset to run inference on.
            trained_model: The trained model to use for inference.

        Returns:
            If UUID of the inference run. If unsuccessful, `None`.
        """

        if not get_api_key():
            raise ValueError(
                "You must have an API key to run inference."
                " Please visit app.sotai.ai to get an API key."
            )

        if trained_model.uuid is None:
            self.analysis(trained_model)

        data = pd.read_csv(filepath)
        expected_columns = list(trained_model.pipeline_config.feature_configs.keys())
        if not set(expected_columns) <= set(data.columns):
            raise ValueError(
                "Inference data must have columns for all features to run inference."
            )

        inference_response_status, inference_uuid = post_inference(
            filepath, trained_model.uuid
        )
        if inference_response_status == APIStatus.ERROR:
            return None

        return inference_uuid

    def await_inference(
        self,
        inference_uuid: str,
        inference_results_folder_path: str,
    ):
        """Polls the SOTAI cloud for the results of the specified inference job.

        Args:
            inference_uuid: The uuid of the inference job to poll.
            inference_results_folder_path: The path to save the inference results to.

        Returns:
            If inference was successfully run, the path to the inference results.
        """
        while True:
            inference_response_status, inference_job_status = get_inference_status(
                inference_uuid
            )
            logging.info("Current inference job status: %s", inference_job_status)
            if (
                inference_response_status == APIStatus.SUCCESS
                and inference_job_status == InferenceConfigStatus.SUCCESS
            ):
                get_inference_response = get_inference_results(
                    inference_uuid, inference_results_folder_path
                )
                if get_inference_response == APIStatus.ERROR:
                    logging.info("Error getting inference results")
                else:
                    logging.info(
                        "Inference results saved to: %s ", inference_results_folder_path
                    )
                return inference_results_folder_path

            sleep(INFERENCE_POLLING_INTERVAL)

    def save(self, filepath: str, include_trained_models: bool = True):
        """Saves the pipeline to the specified filepath.

        Trained models will be saved with the pipeline by default.

        Args:
            filepath: The directory to which the pipeline wil be saved. If the directory
                does not exist, this function will attempt to create it. If the
                directory already exists, this function will overwrite any existing
                content with conflicting filenames.
            include_trained_models: If True (default), then all models trained under
                this pipeline present in the trained_models dictionary attribute will
                be stored along with the pipeline under a `trained_models/{id}`
                directory. If False, trained models will be excluded from saving.
        """
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(os.path.join(filepath, "pipeline.pkl"), "wb") as file:
            pickle.dump(self, file)

        if include_trained_models:
            for trained_model in self.trained_models.values():
                # trained_model.save(filepath) handles creating the directory.
                trained_model.save(
                    os.path.join(filepath, f"trained_models/{trained_model.id}")
                )

    def sync(self):
        """Syncs the pipeline with the SOTAI cloud."""
        if self.uuid is None:
            self.publish()

        for pipeline_config in self.configs.values():
            if pipeline_config.uuid is None and pipeline_config.allow_hosting:
                self._post_pipeline_config(pipeline_config)

        for trained_model in self.trained_models.values():
            if trained_model.uuid is None and trained_model.allow_hosting:
                self.analysis(trained_model)
                self._upload_model(trained_model)

        for dataset in self.datasets.values():
            if dataset.uuid is None and dataset.allow_hosting:
                self._upload_dataset(self.uuid, dataset.id, dataset.pipeline_config_id)

        trained_model_uuids = get_trained_model_uuids(self.uuid)
        local_trained_model_uuids = [
            trained_model.uuid for trained_model in self.trained_models.values()
        ]
        for trained_model_uuid in trained_model_uuids:
            if trained_model_uuid not in local_trained_model_uuids:
                trained_model = TrainedModel.from_hosted(trained_model_uuid)
                if trained_model is not None:
                    self.trained_models[trained_model.id] = trained_model

    @classmethod
    def from_hosted(
        cls,
        pipeline_uuid: str,
        include_trained_models: bool = False,
        include_datasets: bool = False,
    ) -> Pipeline:
        """Returns a new pipeline created from the specified hosted pipeline uuid.

        Args:
            pipeline_uuid: The uuid of the hosted pipeline to load.
            include_trained_models: If True, trained models will be loaded along with
                the pipeline. If False (default), trained models will not be loaded.

        Returns:
            A `Pipeline` instance.
        """
        (
            pipeline_metadata,
            last_config_id,
            pipeline_configs,
            trained_model_uuids,
        ) = get_pipeline(pipeline_uuid)

        if not pipeline_configs:
            raise ValueError(
                "Pipeline configs not found. Please run training before loading."
            )
        pipeline = Pipeline.from_config(
            name=pipeline_metadata["name"],
            config=pipeline_configs[last_config_id],
        )
        pipeline.configs = pipeline_configs
        pipeline.uuid = pipeline_uuid

        if include_trained_models:
            for trained_model_uuid in trained_model_uuids:
                trained_model = TrainedModel.from_hosted(trained_model_uuid)
                if trained_model:
                    pipeline.trained_models[trained_model.id] = trained_model

        if include_datasets:
            _, dataset_uuids = get_dataset_uuids(pipeline_uuid)
            for dataset_uuid in dataset_uuids:
                _, dataset = download_prepared_dataset(dataset_uuid)
                if dataset is not None:
                    pipeline.datasets[dataset.id] = dataset

        pipeline._next_config_id = len(pipeline.configs) + 1
        if len(pipeline.trained_models) != 0:
            pipeline._next_model_id = max(pipeline.trained_models.keys()) + 1

        return pipeline

    @classmethod
    def load(cls, filepath: str) -> Pipeline:
        """Loads the pipeline from the specified filepath.

        Args:
            filepath: The filepath from which to load the pipeline. The filepath should
                point to a file created by the `save` method of a `TrainedModel`
                instance.

        Returns:
            A `Pipeline` instance.
        """
        with open(os.path.join(filepath, "pipeline.pkl"), "rb") as file:
            pipeline = pickle.load(file)

        trained_model_dir = os.path.join(filepath, "trained_models")
        if os.path.isdir(trained_model_dir):
            for directory in os.listdir(trained_model_dir):
                if os.path.isdir(os.path.join(trained_model_dir, directory)):
                    trained_model = TrainedModel.load(
                        os.path.join(trained_model_dir, directory)
                    )
                    pipeline.trained_models[trained_model.id] = trained_model

        return pipeline

    @classmethod
    def from_config(
        cls, config: PipelineConfig, name: Optional[str] = None
    ) -> Pipeline:
        """Returns a new pipeline created from the specified config."""
        pipeline = cls(
            features=list(config.feature_configs.keys()),
            target=config.target,
            target_type=config.target_type,
            primary_metric=config.primary_metric,
            name=name,
        )
        pipeline.feature_configs = config.feature_configs
        pipeline.shuffle_data = config.shuffle_data
        pipeline.drop_empty_percentage = config.drop_empty_percentage
        pipeline.dataset_split = config.dataset_split

        return pipeline

    ############################################################################
    #                            Private Methods                               #
    ############################################################################

    def __getstate__(self):
        """Return state values to be pickled.

        We exclude the trained models from the pipeline.
        """
        state = self.__dict__.copy()
        del state["trained_models"]
        return state

    def __setstate__(self, state):
        """Restore state from the unpickled state values.

        We restore the trained model field
        """
        self.__dict__.update(state)
        self.trained_models = {}

    def _version_pipeline_config(self, data: pd.DataFrame):
        """Returns a new `PipelineConfig` instance verisoned from the current config."""
        pipeline_config_id = self._next_config_id
        self._next_config_id += 1
        pipeline_config = PipelineConfig(
            id=pipeline_config_id,
            target=self.target,
            target_type=self.target_type,
            primary_metric=self.primary_metric,
            feature_configs=self.feature_configs,
            shuffle_data=self.shuffle_data,
            drop_empty_percentage=self.drop_empty_percentage,
            dataset_split=self.dataset_split,
            allow_hosting=self.default_allow_hosting,
        )

        feature_types = determine_feature_types(
            data[list(pipeline_config.feature_configs.keys())]
        )
        for feature_name, feature_type in feature_types.items():
            feature_config = pipeline_config.feature_configs[feature_name]
            if (
                feature_type == FeatureType.NUMERICAL
                or feature_config.type == FeatureType.CATEGORICAL
            ):
                continue
            if feature_type == FeatureType.CATEGORICAL:
                logging.info(
                    "Detected %s as categorical. Replacing numerical config with "
                    "default categorical config using unique values as categories",
                    feature_name,
                )
                pipeline_config.feature_configs[
                    feature_name
                ] = CategoricalFeatureConfig(
                    name=feature_name,
                    categories=sorted(data[feature_name].dropna().unique().tolist()),
                )
            else:
                logging.info(
                    "Removing feature %s because its data type is not supported.",
                    feature_name,
                )
                pipeline_config.feature_configs.pop(feature_name)

        self.configs[pipeline_config_id] = pipeline_config
        return pipeline_config

    def _upload_model(
        self,
        trained_model: TrainedModel,
    ) -> APIStatus:
        """Uploads the trained model to the SOTAI web client.

        If a model has already been uploaded, this function will return without
        uploading the model again. This function requires an internet connection and a
        SOTAI account. The trained model will be uploaded to the SOTAI web client for
        inference.

        Args:
            trained_model: The trained model to upload.
        """

        if not get_api_key():
            raise ValueError(
                "You must have an API key to upload a model."
                " Please visit app.sotai.ai to get an API key."
            )
        model_save_folder_path = f"/tmp/sotai/model/{trained_model.uuid}"

        if trained_model.uuid is None:
            raise ValueError("Must run analysis to generate uuid before uploading.")

        trained_model.save(model_save_folder_path)
        trained_model_response = post_trained_model(
            model_save_folder_path, trained_model.uuid
        )
        return trained_model_response

    def _upload_dataset(
        self,
        pipeline_uuid: str,
        data: Union[int, pd.DataFrame],
        pipeline_config_id: int,
    ) -> Optional[str]:
        """Uploads the dataset to the SOTAI web client.

        If a dataset has already been uploaded, this function will return without
        uploading the dataset again. This function requires an internet connection and a
        SOTAI account. The dataset will be uploaded to the SOTAI web client for
        inference.

        Args:
            pipeline_uuid: The uuid of the pipeline to upload the dataset to.
            data: The raw data to be prepared and trained on. If an int is provided,
                it is assumed to be a dataset id and the corresponding dataset will be
                used.
            pipeline_config_id: The id of the pipeline config to be used for training.
                If not provided, the current pipeline config will be versioned and used.
                If data is an int, this argument is ignored and the pipeline config used
                to prepare the data with the given id will be used.

        Returns:
            If the dataset was successfully uploaded, the dataset UUID.
            Otherwise, `None`.
        """
        filepath = "/tmp/sotai"
        if not os.path.exists(filepath):
            os.makedirs("/tmp/sotai/")

        if isinstance(data, int):
            dataset = self.datasets[data]
            if dataset.uuid is not None:
                return dataset.uuid
        else:
            dataset, new_pipeline_config = self.prepare(data, pipeline_config_id)
            pipeline_config_id = new_pipeline_config.id

        if self.configs[pipeline_config_id].uuid is None:
            status, pipeline_config_uuid = post_pipeline_config(
                pipeline_uuid, self.configs[pipeline_config_id]
            )
            if status == APIStatus.ERROR:
                return None
        else:
            pipeline_config_uuid = self.configs[pipeline_config_id].uuid

        dataset.prepared_data.train.to_csv("/tmp/sotai/train.csv")
        dataset.prepared_data.test.to_csv("/tmp/sotai/test.csv")
        dataset.prepared_data.val.to_csv("/tmp/sotai/validation.csv")
        columns = dataset.prepared_data.train.columns.tolist()
        _, dataset_uuid = post_dataset(
            "/tmp/sotai/train.csv",
            "/tmp/sotai/test.csv",
            "/tmp/sotai/validation.csv",
            columns=columns,
            categorical_columns=[],
            pipeline_config_uuid=pipeline_config_uuid,
            dataset_id=dataset.id,
        )
        dataset.uuid = dataset_uuid

        return dataset_uuid

    def _post_pipeline_config(self, pipeline_config: PipelineConfig) -> str:
        """Posts a pipeline config to the SOTAI web client.

        If a pipeline config has already been posted, this function will return without
        posting the config again.

        Args:
            pipeline_config: The pipeline config to post.

        Returns:
            If the pipeline config was successfully posted, the pipeline config UUID.
            Otherwise, None.
        """

        if pipeline_config.uuid is not None:
            return pipeline_config.uuid

        if self.uuid is None:
            self.uuid = self.publish()

        if self.uuid is None:
            return None

        pipeline_config_response_status, pipeline_config_uuid = post_pipeline_config(
            self.uuid, pipeline_config
        )

        if pipeline_config_response_status == APIStatus.ERROR:
            return None

        pipeline_config.uuid = pipeline_config_uuid

        feature_config_response_status = post_pipeline_feature_configs(
            pipeline_config_uuid, pipeline_config.feature_configs
        )

        if feature_config_response_status == APIStatus.ERROR:
            return None

        return pipeline_config_uuid

    def _local_hypertuning(
        self,
        hypertune_config: HypertuneConfig,
        data: pd.DataFrame,
        pipeline_config_id: Optional[int] = None,
        model_config: Optional[LinearConfig] = None,
    ) -> List[TrainedModel]:
        """Runs hypertuning locally.

        Args:
            hypertune_config: The config to be used for hypertuning the model.
            data: The raw dataframe to be trained on.
            pipeline_config_id: The id of the pipeline config to be used for training.
            model_config: The config to be used for training the model.

        Returns:
            A list of `TrainedModel` instances.
        """

        prepared_data, _ = self.prepare(data, pipeline_config_id)
        hyperparameter_permutations = list(
            itertools.product(
                hypertune_config.batch_sizes,
                hypertune_config.epochs,
                hypertune_config.learning_rates,
            )
        )
        trained_models = []

        for i, hyperparameters in enumerate(hyperparameter_permutations):
            batch_size, epochs, learning_rate = hyperparameters
            logging.info(
                "Training model %s/%s", i + 1, len(hyperparameter_permutations)
            )

            trained_model = self.train(
                prepared_data.id,
                pipeline_config_id=pipeline_config_id,
                model_config=model_config,
                training_config=TrainingConfig(
                    batch_size=batch_size,
                    epochs=epochs,
                    learning_rate=learning_rate,
                    loss_type=hypertune_config.loss_type,
                ),
            )

            trained_models.append(trained_model)

        return trained_models
