"""A Trained Model created for a pipeline."""
from __future__ import annotations

import os
import logging
import pickle
from typing import Optional, Tuple
import numpy as np
import pandas as pd
import torch
from pydantic import Field

from .data import CSVData, replace_missing_values
from .enums import TargetType
from .models import CalibratedLinear
from .types import TrainedModelMetadata
from .api import get_trained_model_metadata, download_trained_model


class TrainedModel(TrainedModelMetadata):
    """A trained calibrated model.

    This model is a container for a trained calibrated model that provides useful
    methods for using the model. The trained calibrated model is the result of running
    the `train` method of a `Pipeline` instance.

    Example:
    ```python
    data = pd.read_csv("data.csv")
    predictions = trained_model.predict(data)
    trained_model.analyze()
    ```

    Attributes:
        dataset_id: The ID of the dataset used to train the model.
        pipeline_uuid: The UUID of the pipeline used to train the model. This will be
            `None` if the trained model has not been analyzed under a pipeline.
        pipeline_config: The configuration of the pipeline used to train the model.
        model_config: The configuration of the model used to train the model.
        training_config: The training configuration used to train the model.
        training_results: The results of training the model.
        model: The trained calibrated model.
        uuid: The UUID of the trained model. This will be `None` if the trained model
            has not been analyzed under a pipeline.
        analysis_url: The URL of the analysis of the trained model. This will be `None`
            if the trained model has not been analyzed under a pipeline.
    """

    model: CalibratedLinear = Field(...)
    allow_model_hosting: bool = False

    class Config:  # pylint: disable=missing-class-docstring,too-few-public-methods
        """Standard Pydantic BaseModel Config."""

        arbitrary_types_allowed = True

    def predict(self, data: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Returns predictions for the given data.

        Args:
            data: The data to be used for prediction. Must have all columns used for
                training the model to be used.

        Returns:
            A tuple containing an array of predictions and an array of probabilities.
            If the target type is regression, then logits will be `None`. If the target
            type is classification, then the predictions will be logits.
        """
        data = data.loc[:, list(self.pipeline_config.feature_configs.keys())]
        data = replace_missing_values(data, self.pipeline_config.feature_configs)

        csv_data = CSVData(data)
        csv_data.prepare(self.model.features, None)
        inputs = list(csv_data.batch(csv_data.num_examples))[0]
        with torch.no_grad():
            predictions = self.model(inputs).numpy()

        if self.pipeline_config.target_type == TargetType.REGRESSION:
            return predictions, None

        return predictions, 1.0 / (1.0 + np.exp(-predictions))

    def save(self, filepath: str):
        """Saves the trained model to the specified directory.

        Args:
            filepath: The directory to save the trained model to. If the directory does
                not exist, this function will attempt to create it. If the directory
                already exists, this function will overwrite any existing content with
                conflicting filenames.
        """
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        with open(os.path.join(filepath, "trained_model_metadata.pkl"), "wb") as file:
            pickle.dump(self.dict(exclude={"model"}), file)
        model_path = f"{filepath}/trained_ptcm_model.pt"
        torch.save(self.model, model_path)

    @classmethod
    def from_hosted(cls, trained_model_uuid: str) -> TrainedModel:
        """Loads a trained model from the hosted API.

        Args:
            trained_model_uuid: The UUID of the trained model to load.

        Returns:
            A `TrainedModel` instance.
        """

        metadata = get_trained_model_metadata(trained_model_uuid)
        if metadata is None:
            logging.error(
                "Trained model %s not found. "
                "Model training may still be in progress.",
                trained_model_uuid,
            )
            return None
        downloaded_file_path = download_trained_model(trained_model_uuid)
        model = torch.load(downloaded_file_path)
        model.eval()

        return TrainedModel(**metadata.dict(), model=model)

    @classmethod
    def load(cls, filepath: str) -> TrainedModel:
        """Loads a trained model from the specified filepath.

        Args:
            filepath: The filepath to load the trained model from. The filepath should
                point to a file created by the `save` method of a `TrainedModel`
                instance.

        Returns:
            A `TrainedModel` instance.
        """
        with open(os.path.join(filepath, "trained_model_metadata.pkl"), "rb") as file:
            trained_model_metadata = pickle.load(file)
        model_path = f"{filepath}/trained_ptcm_model.pt"
        model = torch.load(model_path)
        model.eval()

        return TrainedModel(**trained_model_metadata, model=model)
