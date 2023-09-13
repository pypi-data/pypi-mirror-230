from unittest.mock import Mock

import pytest
import pandas as pd
import numpy as np

from component import (
    gpu_accelerated_shap_for_xgboost as gpu_accelerated_shap_for_xgboost_component,
)
from component import calculate_shap_values


gpu_accelerated_shap_for_xgboost = (
    gpu_accelerated_shap_for_xgboost_component.python_func
)


@pytest.fixture
def mock_input_data(tmp_path, monkeypatch):
    # Mock component method inputs
    mock_input_data = Mock()
    mock_input_data.path = str(tmp_path / "input.csv")
    input_df = pd.DataFrame([{"a": 1, "b": 2, "c": 3}])
    input_df.to_csv(mock_input_data.path, index=False)
    return mock_input_data


@pytest.fixture
def mock_joblib(monkeypatch):
    # Mock model load from gcs
    mock_joblib = Mock()
    mock_joblib.load.return_value = Mock()
    monkeypatch.setattr("utils.joblib", mock_joblib)
    return mock_joblib


@pytest.fixture
def mock_calculate_shap(monkeypatch):
    # Mock shap calculation
    mock_shap_values = np.random.rand(1, 3)
    mock_calculate_shap = Mock()
    mock_calculate_shap.return_value = mock_shap_values
    monkeypatch.setattr("component.calculate_shap_values", mock_calculate_shap)
    return mock_calculate_shap


@pytest.fixture
def mock_model(tmp_path):
    mock_model = Mock()
    mock_model.path = str(tmp_path / "model.joblib")
    return mock_model


@pytest.fixture
def mock_output_data(tmp_path):
    mock_output_data = Mock()
    mock_output_data.path = str(tmp_path / "output")
    return mock_output_data


def test_gpu_accelerated_shap_for_xgboost(
    mock_input_data, mock_joblib, mock_model, mock_calculate_shap, mock_output_data
):
    """
    Tests the following flow from the component:
        1. Model is loaded in
        2. Input data is read in a dataframe
        3. Shap values are retrieved
        4. Shap values are converted into a dataframe and saved to a file
    """
    # Arrange
    # Create expected output df
    input_df = pd.read_csv(mock_input_data.path)
    mock_shap_values = mock_calculate_shap()
    expected_output_df = pd.DataFrame(mock_shap_values, columns=list(input_df.columns))

    # Act
    gpu_accelerated_shap_for_xgboost(mock_input_data, mock_model, mock_output_data)

    # Assert
    output_df = pd.read_csv(mock_output_data.path)
    pd.util.testing.assert_frame_equal(
        output_df.reset_index(drop=True), expected_output_df.reset_index(drop=True)
    )


def test_calculate_shap_values_gpu_enabled(monkeypatch, mock_input_data):
    """Tests whether shap explainer is instantiated with GPU config"""
    # Arrange
    mock_xgb_model = Mock()
    input_data = pd.read_csv(mock_input_data.path)

    mock_shap = Mock()
    monkeypatch.setattr("component.shap", mock_shap)

    # Act
    calculate_shap_values(mock_xgb_model, input_data, enable_gpu=True)

    # Assert
    mock_xgb_model.get_booster.assert_called_once()


def test_calculate_shap_values_gpu_disbaled(monkeypatch, mock_input_data):
    """Tests whether shap explainer is instantiated without GPU (only CPU) config"""
    # Arrange
    mock_xgb_model = Mock()
    input_data = pd.read_csv(mock_input_data.path)

    mock_shap = Mock()
    monkeypatch.setattr("component.shap", mock_shap)

    # Act
    calculate_shap_values(mock_xgb_model, input_data, enable_gpu=False)

    # Assert
    mock_xgb_model.get_booster.assert_not_called()
