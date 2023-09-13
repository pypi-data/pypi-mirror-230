"""Test module for gpt_tokenize component"""
import os
from unittest.mock import MagicMock, Mock

import pytest
from gpt_tokenize import gpt_tokenize


@pytest.fixture
def mock_input_data(tmp_path):
    # Mock input_data Artifact
    mock_input_text = MagicMock()
    mock_input_text.path = str(tmp_path)
    input_data = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, \
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
    with open(f"{mock_input_text.path}/input.txt", "w", encoding="utf-8") as file:
        file.write(input_data)
    return mock_input_text


@pytest.fixture
def mock_train_dataset(tmp_path):
    # Mock output train_dataset artifact
    mock_train_dataset = Mock()
    mock_train_dataset.path = str(tmp_path)
    return mock_train_dataset


@pytest.fixture
def mock_val_dataset(tmp_path):
    # Mock output val_dataset artifact
    mock_val_dataset = Mock()
    mock_val_dataset.path = str(tmp_path)
    return mock_val_dataset


def test_correct_train_test_files_created(
    mock_input_data, mock_train_dataset, mock_val_dataset, monkeypatch
):
    """
    Tests that train and val .bin files are created when running the component logic by:
        1. Loading in mocked input data
        2. Splitting the data into train and val
        3. Encoding the datasets
        4. Exporting them to bin files
    """
    # Arrange
    mock_tiktoken = MagicMock()
    mock_tiktoken.get_encoding.encode_ordinary.return_value = MagicMock()
    monkeypatch.setattr("gpt_tokenize.component.tiktoken", mock_tiktoken)

    # Act
    gpt_tokenize.python_func(mock_input_data, mock_train_dataset, mock_val_dataset)

    # Assert
    assert os.path.exists(mock_train_dataset.path + "/train.bin")
    assert os.path.exists(mock_val_dataset.path + "/val.bin")
