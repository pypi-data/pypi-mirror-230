"""Pydantic models for Pipelines."""
from typing import Dict, List, Literal, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, root_validator

from .enums import (
    FeatureType,
    HypertuneMethod,
    InputKeypointsInit,
    InputKeypointsType,
    LossType,
    Metric,
    Monotonicity,
    TargetType,
)


class DatasetSplit(BaseModel):
    """Defines the split percentage for train, val, and test datasets.

    Attributes:
        train: The percentage of the dataset to use for training.
        val: The percentage of the dataset to use for validation.
        test: The percentage of the dataset to use for testing.
    """

    train: int = 80
    val: int = 10
    test: int = 10

    @root_validator(pre=True, allow_reuse=True)
    @classmethod
    def validate_split_sum(cls, values):
        """Ensures that the split percentages add up to 100."""
        assert (
            values["train"] + values["val"] + values["test"] == 100
        ), "split percentages must add up to 100"
        return values


class PreparedData(BaseModel):
    """A train, val, and test set of data that's been cleaned.

    Attributes:
        train: The training dataset.
        val: The validation dataset.
        test: The testing dataset.
    """

    train: pd.DataFrame = Field(...)
    val: pd.DataFrame = Field(...)
    test: pd.DataFrame = Field(...)

    class Config:  # pylint: disable=missing-class-docstring,too-few-public-methods
        """Standard Pydantic BaseModel Config."""

        arbitrary_types_allowed = True


class Dataset(BaseModel):
    """A class for managing data.

    Attributes:
        id: The ID of the dataset used by the pipeline that prepared it.
        pipeline_config_id: The ID of the pipeline config used to create this dataset.
        prepared_data: The prepared data ready for training.
    """

    id: int = Field(...)
    pipeline_config_id: int = Field(...)
    prepared_data: PreparedData = Field(...)
    uuid: Optional[str] = None
    allow_hosting: bool = False

    class Config:  # pylint: disable=missing-class-docstring,too-few-public-methods
        """Standard Pydantic BaseModel Config."""

        arbitrary_types_allowed = True


class _BaseModelConfig(BaseModel):
    """Configuration for a calibrated model.

    Attributes:
        output_min: The minimum output value for the model. If None, then it will be
            assumed that there is no minimum output value.
        output_max: The maximum output value for the model. If None, then it will be
            assumed that there is no maximum output value.
        output_calibration: Whether to calibrate the output.
        output_calibration_num_keypoints: The number of keypoints to use for the output
            calibrator.
        output_initialization: The method for initializing the output calibrator input
            keypoints.
        output_calibration_input_keypoints_type: The type of output calibrator input
            keypoints.
    """

    output_min: Optional[float] = None
    output_max: Optional[float] = None
    output_calibration: bool = False
    output_calibration_num_keypoints: int = 10
    output_initialization: InputKeypointsInit = InputKeypointsInit.QUANTILES
    output_calibration_input_keypoints_type: InputKeypointsType = (
        InputKeypointsType.FIXED
    )


class LinearConfig(_BaseModelConfig):
    """Configuration for a calibrated linear model.

    Attributes:
        use_bias: Whether to use a bias term for the linear combination.
    """

    use_bias: bool = True


class TrainingConfig(BaseModel):
    """Configuration for training a single model.

    Attributes:
        loss_type: The type of loss function to use for training.
        epochs: The number of iterations through the dataset during training.
        batch_size: The number of examples to use for each training step.
        learning_rate: The learning rate to use for the optimizer.
    """

    loss_type: LossType = Field(...)
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 1e-3


class FeatureAnalysis(BaseModel):
    """Feature analysis results for a single feature of a trained model.

    Attributes:
        feature_name: The name of the feature.
        feature_type: The type of the feature.
        min: The minimum value of the feature.
        max: The maximum value of the feature.
        mean: The mean value of the feature.
        median: The median value of the feature.
        std: The standard deviation of the feature.
        keypoints_inputs_numerical: The input keypoints for the feature if the feature
            is numerical. Otherwise this should be `None`.
        keypoints_inputs_categorical: The input keypoints for the feature if the feature
            is categorical. Otherwise this should be `None`.
        keypoints_outputs: The output keypoints for each input keypoint.
    """

    feature_name: str = Field(...)
    feature_type: FeatureType = Field(...)
    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    # One of the keypoint inputs must exist, which one depends on feature_type.
    keypoints_inputs_numerical: Optional[List[float]] = Field(...)
    keypoints_inputs_categorical: Optional[List[str]] = Field(...)
    keypoints_outputs: List[float] = Field(...)


class TrainingResults(BaseModel):
    """Training results for a single calibrated model.

    Attributes:
        training_time: The total time spent training the model.
        train_loss_by_epoch: The training loss for each epoch.
        train_primary_metric_by_epoch: The training primary metric for each epoch.
        val_loss_by_epoch: The validation loss for each epoch.
        val_primary_metric_by_epoch: The validation primary metric for each
            epoch.
        evaluation_time: The total time spent evaluating the model.
        test_loss: The test loss.
        test_primary_metric: The test primary metric.
        feature_analyses: The feature analysis results for each feature.
        linear_coefficients: A mapping from feature name to linear coefficient. These
            coefficients are the coefficients of the linear combination of features
            after they have been calibrated, so any analysis of the coefficients should
            be done with the feature's calibrator in mind. If using a bias term, the
            bias value will be stored under the key "bias". Note that there will be no
            bias term if you set output bounds or use an output calibrator.
    """

    training_time: float = Field(...)
    train_loss_by_epoch: List[float] = Field(...)
    train_primary_metric_by_epoch: List[float] = Field(...)
    val_loss_by_epoch: List[float] = Field(...)
    val_primary_metric_by_epoch: List[float] = Field(...)
    evaluation_time: float = Field(...)
    test_loss: float = Field(...)
    test_primary_metric: float = Field(...)
    feature_analyses: Dict[str, FeatureAnalysis] = Field(...)
    linear_coefficients: Dict[str, float] = Field(...)


class NumericalFeatureConfig(BaseModel):
    """Configuration for a numerical feature.

    Attributes:
        name: The name of the feature.
        type: The type of the feature. Always `FeatureType.NUMERICAL`.
        num_keypoints: The number of keypoints to use for the calibrator.
        input_keypoints_init: The method for initializing the input keypoints.
        input_keypoints_type: The type of input keypoints.
        monotonicity: The monotonicity constraint, if any.
        projection_iterations: Number of times to run Dykstra's projection algorithm
            when applying constraints.
    """

    name: str = Field(...)
    type: Literal[FeatureType.NUMERICAL] = Field(FeatureType.NUMERICAL, frozen=True)
    num_keypoints: int = 10
    input_keypoints_init: InputKeypointsInit = InputKeypointsInit.QUANTILES
    input_keypoints_type: InputKeypointsType = InputKeypointsType.FIXED
    monotonicity: Monotonicity = Monotonicity.NONE
    projection_iterations: int = 8


class CategoricalFeatureConfig(BaseModel):
    """Configuration for a categorical feature.

    Attributes:
        name: The name of the feature.
        type: The type of the feature. Always `FeatureType.CATEGORICAL`.
        categories: The categories for the feature.
    """

    name: str = Field(...)
    type: Literal[FeatureType.CATEGORICAL] = Field(FeatureType.CATEGORICAL, frozen=True)
    categories: Union[List[int], List[str]] = Field(...)
    # TODO (will): add support for categorical monotonicity.


class PipelineConfig(BaseModel):
    """A configuration object for a `Pipeline`.

    Attributes:
        id: The ID of the pipeline config. This will be set by the Pipeline when it
            versions this config during preparation.
        uuid: The UUID of the pipeline.
        target: The column name for the target.
        target_type: The type of the target.
        primary_metric: The primary metric to use for training and evaluation.
        feature_configs: A dictionary mapping the column name for a feature to its
            config.
        shuffle_data: Whether to shuffle the data before splitting it into train,
            validation, and test sets.
        drop_empty_percentage: Rows will be dropped if they are this percentage empty.
        dataset_split: The split of the dataset into train, validation, and test sets.
    """

    id: Optional[int] = None
    uuid: Optional[str] = None
    target: str = Field(...)
    target_type: TargetType = Field(...)
    primary_metric: Metric = Field(...)
    feature_configs: Dict[
        str, Union[CategoricalFeatureConfig, NumericalFeatureConfig]
    ] = Field(...)
    shuffle_data: bool = Field(...)
    drop_empty_percentage: int = Field(...)
    dataset_split: DatasetSplit = Field(...)
    allow_hosting: bool = False


class HypertuneConfig(BaseModel):
    """A configuration object for hypertuning.

    Attributes:
        loss_type: The type of loss function to use for training.
        epochs: A list of epochs to try.
        batch_sizes: A list of batch sizes to try.
        learning_rates: A list of learning rates to try.
        hypertune_method: The method to use for hypertuning.
    """

    loss_type: LossType
    epochs: List[int]
    batch_sizes: List[int]
    learning_rates: List[float]
    hypertune_method: HypertuneMethod = Field(default=HypertuneMethod.GRID)


class TrainedModelMetadata(BaseModel):
    """Metadata for a trained model.

    Attributes:
        id: The ID of the trained model.
        dataset_id: The ID of the dataset used to train the model.
        pipeline_uuid: The UUID of the pipeline used to train the model. This will be
        `None` if the trained model has not been analyzed under a pipeline.
        pipeline_config: The configuration of the pipeline used to train the model.
        model_config: The configuration of the model used to train the model.
        training_config: The training configuration used to train the model.
        training_results: The results of training the model.
        uuid: The UUID of the trained model. This will be `None` if the trained model
        has not been analyzed under a pipeline.
        analysis_url: The URL of the analysis of the trained model. This will be `None`
        if the trained model has not been analyzed under a pipeline.
    """

    id: Optional[int] = None
    dataset_id: Optional[int] = None
    pipeline_uuid: Optional[str] = None
    pipeline_config: PipelineConfig = Field(...)
    # Note: model_config is protected in Pydantic >=2.0.0, so we use <2.0.0
    model_config: LinearConfig = Field(...)
    training_config: TrainingConfig = Field(...)
    training_results: TrainingResults = Field(...)
    uuid: Optional[str] = None
    analysis_url: Optional[str] = None
    allow_hosting: bool = False
