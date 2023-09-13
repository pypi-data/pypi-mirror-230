"""Tests for data utilities."""
from datetime import datetime

import numpy as np
import pandas as pd
import pytest
import torch

from sotai import CategoricalFeatureConfig, NumericalFeatureConfig
from sotai.constants import MISSING_CATEGORY_VALUE, MISSING_NUMERICAL_VALUE
from sotai.data import CSVData, determine_feature_types, replace_missing_values
from sotai.enums import FeatureType
from sotai.features import CategoricalFeature, NumericalFeature


@pytest.fixture(name="categorical_data")
def fixture_categorical_data():
    """Returns a mapping for the header and data for categorical data."""
    return {
        "header": "categorical",
        "data": np.array(["a", "b", "c", "d"]),
    }


@pytest.fixture(name="numerical_data")
def fixture_numerical_data():
    """Returns a mapping for the header and data for numerical data."""
    return {
        "header": "numerical",
        "data": np.array([1.0, 2.0, 3.0, 4.0]),
    }


@pytest.fixture(name="target_data")
def fixture_target_data():
    """Returns a mapping for the header and data for target data."""
    return {
        "header": "target",
        "data": np.array([0.2, 0.5, 0.4, 0.9]),
    }


@pytest.fixture(name="unknown_data")
def fixture_unknown_data():
    """Returns a mapping for the header and data for unknown data."""
    return {
        "header": "unknown",
        "data": [datetime(2023, 6, 24) for _ in range(4)],
    }


@pytest.fixture(name="data")
def fixture_data(numerical_data, categorical_data, target_data):
    """Returns a dataframe containing the categorical, numerical, and target data."""
    return pd.DataFrame(
        {
            categorical_data["header"]: categorical_data["data"],
            numerical_data["header"]: numerical_data["data"],
            target_data["header"]: target_data["data"],
        }
    )


@pytest.fixture(name="categories")
def fixture_categories(categorical_data):
    """Returns the categories for the categorical data."""
    return categorical_data["data"][:-1]


@pytest.fixture(name="missing_category")
def fixture_missing_category(categorical_data):
    """Returns a missing category for the categorical data."""
    return categorical_data["data"][-1]


@pytest.fixture(name="missing_input_value")
def fixture_missing_input_value():
    """Returns a missing input value for the categorical data."""
    return -1.0


@pytest.fixture(name="features")
def fixture_features(numerical_data, categorical_data, categories, missing_input_value):
    """Returns a list of features."""
    return [
        NumericalFeature(numerical_data["header"], numerical_data["data"]),
        CategoricalFeature(
            categorical_data["header"],
            categories=categories,
            missing_input_value=missing_input_value,
        ),
    ]


@pytest.fixture(name="feature_configs")
def fixture_feature_configs(numerical_data, categorical_data, categories):
    """Returns a list of feature configs."""
    return {
        "numerical": NumericalFeatureConfig(name=numerical_data["header"]),
        "categorical": CategoricalFeatureConfig(
            name=categorical_data["header"], categories=list(categories)
        ),
    }


def test_replace_missing_values(data, feature_configs):
    """Tests that missing values are properly replaced."""
    data["numerical"].values[-1] = np.nan
    data = replace_missing_values(data, feature_configs)
    assert data["categorical"].values[-1] == MISSING_CATEGORY_VALUE
    assert data["numerical"].values[-1] == MISSING_NUMERICAL_VALUE


def test_determine_feature_types(data, unknown_data):
    """Tests the determination of feature types from data."""
    data[unknown_data["header"]] = unknown_data["data"]
    feature_types = determine_feature_types(data)
    assert feature_types["numerical"] == FeatureType.NUMERICAL
    assert feature_types["categorical"] == FeatureType.CATEGORICAL
    assert feature_types["target"] == FeatureType.NUMERICAL
    assert feature_types["unknown"] == FeatureType.UNKNOWN


@pytest.mark.parametrize("from_filepath", [(True), (False)])
def test_initialization(from_filepath, tmp_path, data):
    """Tests that `CSVData` initialization works as expected."""
    if from_filepath:
        datapath = f"{tmp_path}/data.csv"
        data.to_csv(datapath, index=False)
        csv_data = CSVData(datapath)
        assert csv_data.dataset == datapath
    else:
        csv_data = CSVData(data)
        assert csv_data.dataset.equals(data)

    assert csv_data.data.equals(data)
    assert csv_data.headers == list(data.columns)
    assert csv_data.num_examples == len(data)
    assert csv_data.prepared_data is None
    # pylint: disable=protected-access
    assert csv_data._prepared_data_tensor is None
    assert csv_data._targets_tensor is None
    # pylint: enable=protected-access


def test_call(data, numerical_data, categorical_data, target_data):
    """Tests that the correct column data is returned when called."""
    csv_data = CSVData(data)
    assert np.all(csv_data(numerical_data["header"]) == numerical_data["data"])
    assert np.all(csv_data(categorical_data["header"]) == categorical_data["data"])
    assert np.all(csv_data(target_data["header"]) == target_data["data"])


@pytest.mark.parametrize("include_target", [(True), (False)])
@pytest.mark.parametrize("inplace", [(True), (False)])
def test_prepare(
    include_target,
    inplace,
    data,
    features,
    target_data,
    categorical_data,
    categories,
    missing_category,
    missing_input_value,
):
    """Tests that the data is prepared as expected."""
    csv_data = CSVData(data)
    csv_data.prepare(
        features,
        target_data["header"] if include_target else None,
        inplace=inplace,
    )
    original_categorical_data = pd.Series(csv_data(categorical_data["header"], False))
    categorical_data = pd.Series(csv_data(categorical_data["header"], True))
    if inplace:
        assert (original_categorical_data == categorical_data).all()
    for i, category in enumerate(categories):
        assert (categorical_data[categorical_data == category] == i).all()
    assert (
        categorical_data[categorical_data == missing_category] == missing_input_value
    ).all()
    # pylint: disable=protected-access
    assert csv_data._prepared_data_tensor.size()[1], len(features)
    if include_target:
        assert (
            csv_data._prepared_data_tensor.size()[0]
            == csv_data._targets_tensor.size()[0]
        )
        assert csv_data._targets_tensor.size()[1] == 1
    else:
        assert csv_data._targets_tensor is None
    # pylint: enable=protected-access


@pytest.mark.parametrize(
    "include_target,batch_size,expected_example_batches,expected_target_batches",
    [
        (
            True,
            1,
            [
                torch.tensor([[1, 0]]).double(),
                torch.tensor([[2, 1]]).double(),
                torch.tensor([[3, 2]]).double(),
                torch.tensor([[4, -1]]).double(),
            ],
            [
                torch.tensor([[0.2]]).double(),
                torch.tensor([[0.5]]).double(),
                torch.tensor([[0.4]]).double(),
                torch.tensor([[0.9]]).double(),
            ],
        ),
        (
            True,
            2,
            [
                torch.tensor([[1, 0], [2, 1]]).double(),
                torch.tensor([[3, 2], [4, -1]]).double(),
            ],
            [
                torch.tensor([[0.2], [0.5]]).double(),
                torch.tensor([[0.4], [0.9]]).double(),
            ],
        ),
        (
            True,
            3,
            [
                torch.tensor([[1, 0], [2, 1], [3, 2]]).double(),
                torch.tensor([[4, -1]]).double(),
            ],
            [
                torch.tensor([[0.2], [0.5], [0.4]]).double(),
                torch.tensor([[0.9]]).double(),
            ],
        ),
        (
            False,
            4,
            [
                torch.tensor([[1, 0], [2, 1], [3, 2], [4, -1]]).double(),
            ],
            None,
        ),
    ],
)
def test_batch(
    include_target,
    batch_size,
    expected_example_batches,
    expected_target_batches,
    data,
    features,
    target_data,
):
    """Tests that batches of data are properly generated."""
    csv_data = CSVData(data)
    csv_data.prepare(features, target_data["header"] if include_target else None)
    for i, batch in enumerate(csv_data.batch(batch_size)):
        if include_target:
            example_batch, target_batch = batch
            assert torch.allclose(target_batch, expected_target_batches[i])
        else:
            example_batch = batch
        assert torch.allclose(example_batch, expected_example_batches[i])
