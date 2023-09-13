"""Functions for quickly prepping demo data to use with SOTAI."""
from typing import List, Tuple

import pandas as pd


def heart() -> Tuple[pd.DataFrame, List[str], str]:
    """Prepares the demo heart dataset for use with the SOTAI Quickstart guide.

    The heart dataset is a classification dataset with 303 rows and 14 columns. The
    target is binary, with 0 indicating no heart disease and 1 indicating heart
    disease. The features are a mix of categorical and numerical features. For more
    information, see https://archive.ics.uci.edu/ml/datasets/heart+Disease.

    Returns:
        A tuple containing the cleaned heart dataset as a pandas `DataFrame`, the list
        of features, and the target.
    """
    heart_data = pd.read_csv(
        "http://storage.googleapis.com/download.tensorflow.org/data/heart.csv"
    )
    features = list(heart_data.columns)
    target = features.pop(features.index("target"))
    # Convert numerical categories to strings so they are handled as categories
    categorical_features = ["sex", "fbs", "restecg", "exang", "thal"]
    heart_data[categorical_features] = heart_data[categorical_features].astype(str)
    # Clean the thal feature categories
    heart_data["thal"].replace({"1": "fixed", "2": "reversible"}, inplace=True)
    return heart_data, features, target
