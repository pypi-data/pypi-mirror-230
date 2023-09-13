"""Useful classes and functions for handling data for calibrated modeling."""
import logging
from typing import Dict, Generator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import torch

from .constants import MISSING_CATEGORY_VALUE, MISSING_NUMERICAL_VALUE
from .enums import FeatureType
from .features import CategoricalFeature, NumericalFeature
from .types import CategoricalFeatureConfig, NumericalFeatureConfig


def replace_missing_values(
    data: pd.DataFrame,
    feature_configs: Dict[str, Union[CategoricalFeatureConfig, NumericalFeatureConfig]],
) -> pd.DataFrame:
    """Replaces empty values or unspecified categories with a constant value.

    Args:
        - data: The dataset in which to replace missing values.
        - feature_configs: A dictionary mapping feature names to feature configurations.

    Returns:
        The dataset with missing values replaced.
    """
    for feature_name, feature_config in feature_configs.items():
        if feature_config.type == FeatureType.CATEGORICAL:
            unspecified_categories = list(
                set(data[feature_name].unique().tolist())
                - set(feature_config.categories)
            )
            if unspecified_categories:
                logging.info(
                    "Replacing %s with %s for feature %s",
                    unspecified_categories,
                    MISSING_CATEGORY_VALUE,
                    feature_name,
                )
                data[feature_name].replace(
                    unspecified_categories, MISSING_CATEGORY_VALUE, inplace=True
                )
            data[feature_name].fillna(MISSING_CATEGORY_VALUE, inplace=True)
        else:
            data[feature_name].fillna(MISSING_NUMERICAL_VALUE, inplace=True)

    return data


def determine_feature_types(data: pd.DataFrame) -> Dict[str, FeatureType]:
    """Returns a dictionary mapping feature name to type for the given data."""
    feature_types = {}
    for column in data.columns:
        dtype_kind = data[column].dtype.kind
        if dtype_kind in ["S", "O", "b"]:  # string, object, boolean
            feature_types[column] = FeatureType.CATEGORICAL
        elif dtype_kind in ["i", "u", "f"]:  # integer, unsigned integer, float
            feature_types[column] = FeatureType.NUMERICAL
        else:  # datetime, timedelta, complex, etc.
            feature_types[column] = FeatureType.UNKNOWN
    return feature_types


class CSVData:
    """Class for handling CSV data for calibrated modeling.

    Attributes:
        - All `__init__` arguments.
        data: A pandas `DataFrame` containing the loaded CSV data.
        headers: The list of headers available from the loaded data.
        num_examples: The number of examples in the dataset.
        prepared_data: The prepared data. This will be `None` if `prepare(...)` has not
            been called.

    Example:
    ```python
    csv_data = CSVData("path/to/data.csv")
    feature_configs = [
        NumericalFeatureConfig(
            feature_name="numerical_feature"
            data=csv_data("numerical_feature")  # must match feature column header
        ),
        CategoricalFeatureConfig(
            feature_name="categorical_feature"
            categories=np.unique(csv_data("categorical_feature"))  # uses all categories
        ),
    ]
    csv_data.prepare(feature_configs, "target", ...)  # must match target column header
    for examples, labels in csv_data.batch(64):
        training_step(...)
    ```
    """

    def __init__(
        self,
        dataset: Union[str, pd.DataFrame],
    ) -> None:
        """Initializes an instance of `CSVData`.

        Loads a CSV file if filepath is provided. Otherwise it will use the provided
        DataFrame.

        Args:
            dataset: Either a string filepath pointing to the CSV data that should be
                loaded or a `pd.DataFrame` containing the data that should be used.
                The CSV file or DataFrame must have a header.
        """
        self.dataset = dataset
        if isinstance(dataset, str):
            self.data = pd.read_csv(dataset)
        else:
            self.data = dataset.copy()
        self.headers = list(self.data.columns)
        self.num_examples = len(self.data)
        self.prepared_data = None
        self._prepared_data_tensor, self._targets_tensor = None, None

    def __call__(self, header: str, prepared: bool = False) -> np.ndarray:
        """Selects the data for the column with the given header.

        Args:
            header: The header of the column for which data is selected.

        Returns:
            The selected data as a numpy array.

        Raises:
            ValueError: If the provided header is not available in the data.
            ValueError: If `prepared` is true but `prepare(...)` has not been called.
        """
        if not header in self.headers:
            raise ValueError(f"Column {header} does not exist: {self.headers}.")
        if prepared:
            if self.prepared_data is None:
                raise ValueError(
                    "CSV.prepare(...) must be called first for prepared data."
                )
            return self.prepared_data[header].to_numpy()
        return self.data[header].to_numpy()

    def prepare(
        self,
        features: List[Union[NumericalFeature, CategoricalFeature]],
        target_header: Optional[str],
        inplace: bool = True,
    ) -> None:
        """Prepares the data for calibrated modeling.

        Args:
            feature_configs: Feature configs that specify how to prepare the data.
            target_header: The header for the target column. If `None`, it will be
                assumed that there is no target column present (e.g. for inference)
            inplace: If True, original `data` attribute will be updated. If False, a
                copy of the original data will be prepared and the original will be
                preserved.

        Raises:
            ValueError: If a feature in `feature_configs` is not in the dataset.
        """
        if self.prepared_data is not None:
            logging.info("Prepare has already been called. Doing nothing.")
            return
        selected_features = [feature.feature_name for feature in features]
        unavailable_features = set(selected_features) - set(self.data.columns)
        if len(unavailable_features) > 0:
            raise ValueError(f"Features {unavailable_features} not found in dataset.")
        self.prepared_data = self.data if inplace else self.data.copy()
        for feature in features:
            if feature.feature_type == FeatureType.CATEGORICAL:
                feature_data = self.prepared_data[feature.feature_name].map(
                    feature.category_indices
                )
                if feature.missing_input_value is not None:
                    feature_data = feature_data.fillna(feature.missing_input_value)
                self.prepared_data[feature.feature_name] = feature_data
        if target_header is not None:
            self._targets_tensor = torch.from_numpy(
                self.prepared_data.pop(target_header).values
            )[:, None].double()
        self._prepared_data_tensor = torch.from_numpy(
            self.prepared_data[selected_features].values
        ).double()

    def batch(
        self, batch_size: int
    ) -> Generator[Union[Tuple[torch.Tensor, torch.Tensor], torch.Tensor], None, None]:
        """A generator that yields a tensor with `batch_size` examples.

        Args:
            batch_size: The size of each batch returns during each iteration.

        Yields:
            If prepared with a target column: a tuple (examples, targets) of
                `torch.Tensor` of shape `(batch_size, num_features)` and
                `(batch_size, 1)`, repsectively.
            If prepared without a target column: a `torch.Tensor` of shape
                `(batch_size, num_features)`.

        Raises:
            ValueError: If `prepare(...)` is not called first.
        """
        if self.prepared_data is None:
            raise ValueError("CSVData.prepare(...) must be called first.")

        for i in range(0, self.num_examples, batch_size):
            if self._targets_tensor is not None:
                yield (
                    self._prepared_data_tensor[i : i + batch_size],
                    self._targets_tensor[i : i + batch_size],
                )
            else:
                yield self._prepared_data_tensor[i : i + batch_size]
