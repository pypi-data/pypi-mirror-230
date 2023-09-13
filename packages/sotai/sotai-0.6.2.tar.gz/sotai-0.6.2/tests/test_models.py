"""Tests for models."""
import numpy as np
import pytest
import torch

from sotai import Monotonicity
from sotai.features import CategoricalFeature, NumericalFeature
from sotai.models import CalibratedLinear

from .utils import train_calibrated_module


@pytest.mark.parametrize(
    "features,output_min,output_max,output_calibration_num_keypoints,"
    "expected_linear_monotonicities,expected_output_calibrator_monotonicity",
    [
        (
            [
                NumericalFeature(
                    feature_name="numerical_feature",
                    data=np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
                    num_keypoints=5,
                    monotonicity=Monotonicity.NONE,
                ),
                CategoricalFeature(
                    feature_name="categorical_feature",
                    categories=["a", "b", "c"],
                    monotonicity_pairs=[("a", "b")],
                ),
            ],
            None,
            None,
            None,
            [
                Monotonicity.NONE,
                Monotonicity.INCREASING,
            ],
            Monotonicity.INCREASING,
        ),
        (
            [
                NumericalFeature(
                    feature_name="numerical_feature",
                    data=np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
                    num_keypoints=5,
                    monotonicity=Monotonicity.NONE,
                ),
                CategoricalFeature(
                    feature_name="categorical_feature",
                    categories=["a", "b", "c"],
                    monotonicity_pairs=None,
                ),
            ],
            -1.0,
            1.0,
            10,
            [
                Monotonicity.INCREASING,
                Monotonicity.INCREASING,
            ],
            Monotonicity.NONE,
        ),
        (
            [
                NumericalFeature(
                    feature_name="numerical_feature",
                    data=np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
                    num_keypoints=5,
                    monotonicity=Monotonicity.DECREASING,
                ),
                CategoricalFeature(
                    feature_name="categorical_feature",
                    categories=["a", "b", "c"],
                    monotonicity_pairs=None,
                ),
            ],
            0.0,
            None,
            None,
            [
                Monotonicity.INCREASING,
                Monotonicity.INCREASING,
            ],
            Monotonicity.INCREASING,
        ),
    ],
)
def test_initialization(
    features,
    output_min,
    output_max,
    output_calibration_num_keypoints,
    expected_linear_monotonicities,
    expected_output_calibrator_monotonicity,
):
    """Tests that `CalibratedLinear` initialization works."""
    calibrated_linear = CalibratedLinear(
        features=features,
        output_min=output_min,
        output_max=output_max,
        output_calibration_num_keypoints=output_calibration_num_keypoints,
    )
    assert calibrated_linear.features == features
    assert calibrated_linear.output_min == output_min
    assert calibrated_linear.output_max == output_max
    assert (
        calibrated_linear.output_calibration_num_keypoints
        == output_calibration_num_keypoints
    )
    assert len(calibrated_linear.calibrators) == len(features)
    for calibrator in calibrated_linear.calibrators.values():
        assert calibrator.output_min == output_min
        assert calibrator.output_max == output_max
    assert calibrated_linear.linear.monotonicities == expected_linear_monotonicities
    if (
        output_min is not None
        or output_max is not None
        or output_calibration_num_keypoints
    ):
        assert not calibrated_linear.linear.use_bias
        assert calibrated_linear.linear.weighted_average
    else:
        assert calibrated_linear.linear.use_bias
        assert not calibrated_linear.linear.weighted_average
    if not output_calibration_num_keypoints:
        assert calibrated_linear.output_calibrator is None
    else:
        assert calibrated_linear.output_calibrator.output_min == output_min
        assert calibrated_linear.output_calibrator.output_max == output_max
        assert (
            calibrated_linear.output_calibrator.monotonicity
            == expected_output_calibrator_monotonicity
        )


# TODO: add more parameterized tests
@pytest.mark.parametrize(
    "output_min,output_max,calibrator_kernel_datas,linear_kernel_data,"
    "output_calibrator_kernel_data,inputs,expected_outputs",
    [
        (
            None,
            None,
            [
                torch.tensor([[0.0], [1.0], [1.0], [1.0]]).double(),
                torch.tensor([[1.0], [2.0], [3.0]]).double(),
            ],
            torch.tensor([[1.0], [2.0]]).double(),
            None,
            torch.tensor([[1.0, 0], [2.0, 1], [3.0, 2], [4.0, 1]]).double(),
            torch.tensor([[2.0], [5.0], [8.0], [7.0]]).double(),
        ),
        (
            0.0,
            1.0,
            [
                torch.tensor([[1.0], [-0.5], [-0.5], [1.0]]).double(),
                torch.tensor([[1.0], [0.5], [0.0]]).double(),
            ],
            torch.tensor([[0.3], [0.7]]).double(),
            torch.tensor([[0.0], [1.0], [-1.0], [1.0]]).double(),
            torch.tensor([[1.0, 0], [2.0, 1], [3.0, 2], [4.0, 1]]).double(),
            torch.tensor([[1.0], [0.5], [0.0], [0.05]]).double(),
        ),
    ],
)
def test_forward(
    output_min,
    output_max,
    calibrator_kernel_datas,
    linear_kernel_data,
    output_calibrator_kernel_data,
    inputs,
    expected_outputs,
):
    """Tests that forward returns expected result."""
    calibrated_linear = CalibratedLinear(
        features=[
            NumericalFeature(
                feature_name="numerical_feature",
                data=np.array([1.0, 2.0, 3.0, 4.0]),
                num_keypoints=4,
                monotonicity=Monotonicity.NONE,
            ),
            CategoricalFeature(
                feature_name="categorical_feature",
                categories=["a", "b", "c"],
                monotonicity_pairs=None,
            ),
        ],
        output_min=output_min,
        output_max=output_max,
        output_calibration_num_keypoints=output_calibrator_kernel_data.size()[0]
        if output_calibrator_kernel_data is not None
        else None,
    )
    for i, calibrator in enumerate(calibrated_linear.calibrators.values()):
        calibrator.kernel.data = calibrator_kernel_datas[i]
    calibrated_linear.linear.kernel.data = linear_kernel_data
    if output_calibrator_kernel_data is not None:
        calibrated_linear.output_calibrator.kernel.data = output_calibrator_kernel_data
    outputs = calibrated_linear(inputs)
    assert torch.allclose(outputs, expected_outputs)


@pytest.mark.parametrize(
    "cat_cal_kernel_data,num_cal_kernel_data,linear_kernel_data,weighted_avg,expected_outputs",
    [
        (
            torch.tensor([[2.0], [1.0]]).double(),
            torch.tensor([[1.0], [2.0]]).double(),
            torch.tensor([[0.4], [0.6]]).double(),
            False,
            {"categorical_feature": ["Monotonicity violated at: [(0, 1)]."]},
        ),
        (
            torch.tensor([[1.0], [2.0]]).double(),
            torch.tensor([[2.0], [1.0]]).double(),
            torch.tensor([[0.4], [0.6]]).double(),
            False,
            {"numerical_feature": ["Monotonicity violated at: [(0, 1)]."]},
        ),
        (
            torch.tensor([[1.0], [2.0]]).double(),
            torch.tensor([[1.0], [2.0]]).double(),
            torch.tensor([[0.4], [0.4]]).double(),
            True,
            {"linear": ["Weights do not sum to 1."]},
        ),
        (
            torch.tensor([[2.0], [1.0]]).double(),
            torch.tensor([[2.0], [1.0]]).double(),
            torch.tensor([[0.2], [-0.2]]).double(),
            True,
            {
                "numerical_feature": ["Monotonicity violated at: [(0, 1)]."],
                "categorical_feature": ["Monotonicity violated at: [(0, 1)]."],
                "linear": ["Weights do not sum to 1.", "Monotonicity violated at: [1]"],
            },
        ),
        (
            torch.tensor([[1.0], [2.0]]).double(),
            torch.tensor([[1.0], [2.0]]).double(),
            torch.tensor([[0.4], [0.6]]).double(),
            True,
            {},
        ),
    ],
)
def test_assert_constraints(
    cat_cal_kernel_data,
    num_cal_kernel_data,
    linear_kernel_data,
    weighted_avg,
    expected_outputs,
):
    """
    Tests that each layer's assert_constraints is properly called and aggregates each
    set of error messages properly.
    """
    calibrated_linear = CalibratedLinear(
        features=[
            NumericalFeature(
                feature_name="numerical_feature",
                data=np.array([1.0, 2.0]),
                num_keypoints=2,
                monotonicity=Monotonicity.INCREASING,
            ),
            CategoricalFeature(
                feature_name="categorical_feature",
                categories=["a", "b"],
                monotonicity_pairs=[("a", "b")],
            ),
        ],
    )
    calibrated_linear.calibrators[
        "categorical_feature"
    ].kernel.data = cat_cal_kernel_data
    calibrated_linear.calibrators["numerical_feature"].kernel.data = num_cal_kernel_data
    calibrated_linear.linear.kernel.data = linear_kernel_data
    calibrated_linear.linear.weighted_average = weighted_avg

    assert calibrated_linear.assert_constraints() == expected_outputs


def test_constrain():
    """Tests that constrain properly constrains all layers."""
    output_min, output_max = -1.0, 1.0
    calibrated_linear = CalibratedLinear(
        features=[
            NumericalFeature(
                feature_name="numerical_feature",
                data=np.array([1.0, 2.0, 3.0, 4.0]),
                num_keypoints=4,
                monotonicity=Monotonicity.NONE,
            ),
            CategoricalFeature(
                feature_name="categorical_feature",
                categories=["a", "b", "c"],
                monotonicity_pairs=None,
            ),
        ],
        output_min=-output_min,
        output_max=output_max,
        output_calibration_num_keypoints=5,
    )
    calibrated_linear.calibrators["numerical_feature"].kernel.data = torch.tensor(
        [[-2.0], [1.0], [2.0], [1.0]]
    ).double()
    calibrated_linear.calibrators["categorical_feature"].kernel.data = torch.tensor(
        [[2.0], [0.5], [-2.0]]
    ).double()
    calibrated_linear.linear.kernel.data = torch.tensor([[1.0], [2.0]]).double()
    calibrated_linear.output_calibrator.kernel.data = torch.tensor(
        [[0.0], [1.0], [0.5], [1.0], [-1.0]]
    ).double()
    calibrated_linear.constrain()
    for calibrator in calibrated_linear.calibrators.values():
        keypoint_outputs = calibrator.keypoints_outputs()
        assert torch.all(keypoint_outputs >= output_min)
        assert torch.all(keypoint_outputs <= output_max)
    assert torch.sum(calibrated_linear.linear.kernel.data) == 1.0
    output_calibrator_keypoint_outputs = (
        calibrated_linear.output_calibrator.keypoints_outputs()
    )
    assert torch.all(output_calibrator_keypoint_outputs >= output_min)
    assert torch.all(output_calibrator_keypoint_outputs <= output_max)


def test_training():  # pylint: disable=too-many-locals
    """Tests `CalibratedLinear` training on data from f(x) = 0.7|x_1| + 0.3x_2."""
    num_examples, num_categories = 3000, 3
    output_min, output_max = 0.0, num_categories - 1
    x_1_numpy = np.random.uniform(-output_max, output_max, size=num_examples)
    x_1 = torch.from_numpy(x_1_numpy)[:, None]
    num_examples_per_category = num_examples // num_categories
    x2_numpy = np.concatenate(
        [[c] * num_examples_per_category for c in range(num_categories)]
    )
    x_2 = torch.from_numpy(x2_numpy)[:, None]
    training_examples = torch.column_stack((x_1, x_2))
    linear_coefficients = torch.tensor([0.7, 0.3]).double()
    training_labels = torch.sum(
        torch.column_stack((torch.absolute(x_1), x_2)) * linear_coefficients,
        dim=1,
        keepdim=True,
    )
    randperm = torch.randperm(training_examples.size()[0])
    training_examples = training_examples[randperm]
    training_labels = training_labels[randperm]

    calibrated_linear = CalibratedLinear(
        features=[
            NumericalFeature(
                "x1",
                x_1_numpy,
                num_keypoints=4,
            ),
            CategoricalFeature("x2", [0, 1, 2], monotonicity_pairs=[(0, 1), (1, 2)]),
        ],
        output_min=output_min,
        output_max=output_max,
    )

    loss_fn = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(calibrated_linear.parameters(recurse=True), lr=1e-1)

    with torch.no_grad():
        initial_predictions = calibrated_linear(training_examples)
        initial_loss = loss_fn(initial_predictions, training_labels)

    train_calibrated_module(
        calibrated_linear,
        training_examples,
        training_labels,
        loss_fn,
        optimizer,
        500,
        num_examples // 10,
    )

    with torch.no_grad():
        trained_predictions = calibrated_linear(training_examples)
        trained_loss = loss_fn(trained_predictions, training_labels)

    assert trained_loss < initial_loss
    assert trained_loss < 0.02
