"""PyTorch Calibrated training utility functions."""
import time
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import torch
import torchmetrics
from pydantic import BaseModel
from tqdm import trange

from .constants import MISSING_CATEGORY_VALUE, MISSING_NUMERICAL_VALUE
from .data import CSVData
from .enums import FeatureType, LossType, Metric
from .features import CategoricalFeature, NumericalFeature
from .models import CalibratedLinear
from .types import (
    CategoricalFeatureConfig,
    Dataset,
    FeatureAnalysis,
    LinearConfig,
    NumericalFeatureConfig,
    PipelineConfig,
    TrainingConfig,
    TrainingResults,
)


class PerEpochResults(BaseModel):
    """Container for the per-epoch results of training a PyTorch Calibrated model."""

    train_loss_by_epoch: List[float]
    train_primary_metric_by_epoch: List[float]
    val_loss_by_epoch: List[float]
    val_primary_metric_by_epoch: List[float]


def create_features(
    feature_configs: Dict[str, Union[CategoricalFeatureConfig, NumericalFeatureConfig]],
    train_csv_data: CSVData,
) -> List[Union[CategoricalFeature, NumericalFeature]]:
    """Returns a list of PyTorch Calibrated feature configs."""
    features = []

    for feature_name, feature_config in feature_configs.items():
        if feature_config.type == FeatureType.CATEGORICAL:
            features.append(
                CategoricalFeature(
                    feature_name=feature_name,
                    categories=feature_config.categories,
                    missing_input_value=MISSING_NUMERICAL_VALUE,
                )
            )
        else:  # FeatureType.NUMERICAL
            features.append(
                NumericalFeature(
                    feature_name=feature_name,
                    data=train_csv_data(feature_name),
                    num_keypoints=feature_config.num_keypoints,
                    input_keypoints_init=feature_config.input_keypoints_init,
                    missing_input_value=MISSING_NUMERICAL_VALUE,
                    monotonicity=feature_config.monotonicity,
                    projection_iterations=feature_config.projection_iterations,
                )
            )

    return features


def create_loss(loss_type: LossType) -> torch.nn.Module:
    """Returns a Torch loss function from the given `LossType`."""
    if loss_type == LossType.BINARY_CROSSENTROPY:
        return torch.nn.BCEWithLogitsLoss()
    if loss_type == LossType.HINGE:
        return torch.nn.HingeEmbeddingLoss()
    if loss_type == LossType.HUBER:
        return torch.nn.HuberLoss()
    if loss_type == LossType.MAE:
        return torch.nn.L1Loss()
    if loss_type == LossType.MSE:
        return torch.nn.MSELoss()

    raise ValueError(f"Unknown loss type: {loss_type}")


def create_metric(metric: Metric) -> torchmetrics.Metric:
    """Returns a torchmetric Metric for the given `Metric`."""
    if metric == Metric.AUC:
        return torchmetrics.AUROC("binary")
    if metric == Metric.MAE:
        return torchmetrics.MeanAbsoluteError()
    if metric == Metric.MSE:
        return torchmetrics.MeanSquaredError()

    raise ValueError(f"Unknown metric: {metric}")


def create_model(
    features: List[Union[CategoricalFeature, NumericalFeature]],
    model_config: LinearConfig,
):
    """Returns a PTCM model config constructed from the given `ModelConfig`."""
    return CalibratedLinear(
        features,
        output_min=model_config.output_min,
        output_max=model_config.output_max,
        use_bias=model_config.use_bias,
        output_calibration_num_keypoints=None
        if not model_config.output_calibration
        else model_config.output_calibration_num_keypoints,
    )


def train_model(  # pylint: disable=too-many-locals
    target: str,
    primary_metric: Metric,
    train_csv_data: CSVData,
    val_csv_data: CSVData,
    pipeline_config: PipelineConfig,
    model_config: LinearConfig,
    training_config: TrainingConfig,
) -> Tuple[CalibratedLinear, PerEpochResults, torch.nn.Module, torchmetrics.Metric]:
    """Trains a PyTorch Calibrated model according to the given config."""
    features = create_features(pipeline_config.feature_configs, train_csv_data)
    model = create_model(features, model_config)

    optimizer = torch.optim.Adam(
        model.parameters(recurse=True), training_config.learning_rate
    )
    loss_fn = create_loss(training_config.loss_type)
    metric_fn = create_metric(primary_metric)

    train_loss_by_epoch = []
    train_primary_metric_by_epoch = []
    val_loss_by_epoch = []
    val_primary_metric_by_epoch = []
    train_csv_data.prepare(features, target)
    val_csv_data.prepare(features, target)
    val_examples, val_targets = list(val_csv_data.batch(val_csv_data.num_examples))[0]
    for _ in trange(training_config.epochs, desc="Training Progress"):
        train_prediction_tensors = []
        train_target_tensors = []
        for example_batch, target_batch in train_csv_data.batch(
            training_config.batch_size
        ):
            optimizer.zero_grad()
            outputs = model(example_batch)
            train_prediction_tensors.append(outputs)
            train_target_tensors.append(target_batch)
            loss = loss_fn(outputs, target_batch)
            loss.backward()
            optimizer.step()
            model.constrain()
        with torch.no_grad():
            predictions = torch.cat(train_prediction_tensors)
            targets = torch.cat(train_target_tensors)
            train_loss = loss_fn(predictions, targets)
            train_loss_by_epoch.append(train_loss.tolist())
            train_metric = metric_fn(predictions, targets)
            train_primary_metric_by_epoch.append(train_metric.tolist())
            val_predictions = model(val_examples)
            val_loss = loss_fn(val_predictions, val_targets)
            val_loss_by_epoch.append(val_loss.tolist())
            val_metric = metric_fn(val_predictions, val_targets)
            val_primary_metric_by_epoch.append(val_metric.tolist())

    per_epoch_results = PerEpochResults(
        train_loss_by_epoch=train_loss_by_epoch,
        train_primary_metric_by_epoch=train_primary_metric_by_epoch,
        val_loss_by_epoch=val_loss_by_epoch,
        val_primary_metric_by_epoch=val_primary_metric_by_epoch,
    )

    return model, per_epoch_results, loss_fn, metric_fn


def extract_feature_analyses(
    model: CalibratedLinear,
    feature_configs: Dict[str, Union[CategoricalFeatureConfig, NumericalFeatureConfig]],
    data: pd.DataFrame,
) -> Dict[str, FeatureAnalysis]:
    """Extracts feature statistics and calibration weights for each feature.

    Args:
        model: A (pytorch) calibrated model.
        feature_configs: A mapping from feature name to feature config.
        data: The training + validation data for this model.

    Returns:
        A dictionary mapping feature name to `FeatureAnalysis` instance.
    """
    feature_analyses = {}

    for feature_name, calibrator in model.calibrators.items():
        feature_config = feature_configs[feature_name]

        if feature_config.type == FeatureType.NUMERICAL:
            keypoints_inputs_numerical = [
                float(x) for x in calibrator.keypoints_inputs()
            ]
            keypoints_inputs_categorical = []
        else:
            keypoints_inputs_numerical = []
            keypoints_inputs = feature_config.categories + [MISSING_CATEGORY_VALUE]
            keypoints_inputs_categorical = [str(ki) for ki in keypoints_inputs]

        fa_dict = {
            "feature_name": feature_name,
            "feature_type": feature_config.type,
            "keypoints_inputs_numerical": keypoints_inputs_numerical,
            "keypoints_inputs_categorical": keypoints_inputs_categorical,
            "keypoints_outputs": [float(x) for x in calibrator.keypoints_outputs()],
        }

        if feature_config.type == FeatureType.NUMERICAL:
            fa_dict.update(
                {
                    "min": float(np.min(data[feature_name].values)),
                    "max": float(np.max(data[feature_name].values)),
                    "mean": float(np.mean(data[feature_name].values)),
                    "median": float(np.median(data[feature_name].values)),
                    "std": float(np.std(data[feature_name].values)),
                }
            )

        feature_analyses[feature_name] = FeatureAnalysis(**fa_dict)

    return feature_analyses


def extract_linear_coefficients(
    linear_model: CalibratedLinear,
    features: List[str],
) -> Dict[str, float]:
    """Extracts linear coefficients from a PyTorch `CalibratedLinear` model."""
    linear_coefficients = dict(
        zip(features, linear_model.linear.kernel.detach().numpy().flatten())
    )
    if linear_model.use_bias:
        linear_coefficients["bias"] = linear_model.linear.bias.detach().numpy()[0]

    return linear_coefficients


def train_and_evaluate_model(  # pylint: disable=too-many-locals
    dataset: Dataset,
    target: str,
    primary_metric: Metric,
    pipeline_config: PipelineConfig,
    model_config: LinearConfig,
    training_config: TrainingConfig,
) -> Tuple[CalibratedLinear, TrainingResults]:
    """Trains a PyTorch Calibrated model according to the given config."""
    train_csv_data = CSVData(dataset.prepared_data.train)
    val_csv_data = CSVData(dataset.prepared_data.val)

    training_start_time = time.time()
    trained_model, per_epoch_results, loss_fn, metric_fn = train_model(
        target,
        primary_metric,
        train_csv_data,
        val_csv_data,
        pipeline_config,
        model_config,
        training_config,
    )
    training_time = time.time() - training_start_time

    evaluation_start_time = time.time()
    test_csv_data = CSVData(dataset.prepared_data.test)
    test_csv_data.prepare(trained_model.features, target)
    x_test, y_test = list(test_csv_data.batch(test_csv_data.num_examples))[0]
    with torch.no_grad():
        evaluation_predictions = trained_model(x_test)
        evaluation_loss = loss_fn(evaluation_predictions, y_test)
        evaluation_metric = metric_fn(evaluation_predictions, y_test)
    evaluation_time = time.time() - evaluation_start_time

    feature_analyses = extract_feature_analyses(
        trained_model,
        pipeline_config.feature_configs,
        pd.concat([train_csv_data.prepared_data, val_csv_data.prepared_data]),
    )

    linear_coefficients = extract_linear_coefficients(
        trained_model, list(pipeline_config.feature_configs.keys())
    )

    training_results = TrainingResults(
        training_time=training_time,
        train_loss_by_epoch=per_epoch_results.train_loss_by_epoch,
        train_primary_metric_by_epoch=per_epoch_results.train_primary_metric_by_epoch,
        val_loss_by_epoch=per_epoch_results.val_loss_by_epoch,
        val_primary_metric_by_epoch=per_epoch_results.val_primary_metric_by_epoch,
        evaluation_time=evaluation_time,
        test_loss=evaluation_loss.tolist(),
        test_primary_metric=evaluation_metric.tolist(),
        feature_analyses=feature_analyses,
        linear_coefficients=linear_coefficients,
    )

    return trained_model, training_results
