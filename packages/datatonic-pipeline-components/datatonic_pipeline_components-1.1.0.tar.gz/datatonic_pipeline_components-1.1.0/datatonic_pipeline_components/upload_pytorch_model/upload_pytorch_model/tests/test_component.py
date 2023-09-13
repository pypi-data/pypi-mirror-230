"""Unit tests for the KFP component that uploads a PyTorch model to Vertex AI"""
from unittest.mock import Mock, patch
import os
import pytest

from upload_pytorch_model.utils.gcs_helper import (
    split_bucket_object_file,
    stage_files_locally,
)

from upload_pytorch_model.utils.model_archiver import run_command

from upload_pytorch_model.component import upload_pytorch_model

upload_pytorch_model = upload_pytorch_model.python_func

# Fixtures and mocks


class MockStorageBlob:
    """Class that mocks a GCS Blob"""

    def __init__(self, name: str):
        self.name = name

    def download_to_filename(self, name):
        with open(name, "w") as f:
            f.write("")


class MockListBlobs(MockStorageBlob):
    """Class that mocks the Cloud Storage list_blob() method"""

    def __init__(self):
        self.list_blobs = []

    def add_blob(self, blob_to_add):
        self.list_blobs.append(blob_to_add)


def remove_file(filename):
    """Helper function to remove a file from local environment"""
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_bucket_name():
    """Mocks a GCS bucket"""
    bucket_name = "test-model-bucket"
    return bucket_name


@pytest.fixture
def mock_object_name(tmp_path):
    """Mocks a GCS object"""
    return tmp_path


@pytest.fixture
def mock_model_name():
    """Mocks a PyTorch model"""
    model_name = "model_name.pt"
    yield model_name
    remove_file(model_name)


@pytest.fixture
def mock_pt_model(tmp_path, mock_model_name):
    """Mocks a PyTorch model and creates a mock GCS blob"""
    mock_model = Mock()
    mock_model.name = mock_model_name
    mock_model.path = str(tmp_path / mock_model.name)
    mock_model.blob = MockStorageBlob(name=mock_model.path)
    return mock_model


@pytest.fixture
def mock_mar_model(tmp_path):
    """Mocks a .mar file and GCS blob"""
    mock_mar = Mock()
    mock_mar.name = "model.mar"
    mock_mar.path = str(tmp_path / mock_mar.name)
    mock_mar.blob = MockStorageBlob(name=mock_mar.path)
    return mock_mar


@pytest.fixture
def mock_custom_handler(tmp_path):
    """Mocks a custom hanlder file and GCS blob"""
    mock_handler = Mock()
    mock_handler.name = "handler.py"
    mock_handler.path = str(tmp_path / mock_handler.name)
    mock_handler.blob = MockStorageBlob(name=mock_handler.path)
    yield mock_handler
    remove_file(mock_handler.name)


@pytest.fixture
def mock_requirements_file(tmp_path):
    """Mocks a requirements file and GCS blob"""
    mock_reqs = Mock()
    mock_reqs.name = "requirements.txt"
    mock_reqs.path = str(tmp_path / mock_reqs.name)
    mock_reqs.blob = MockStorageBlob(name=mock_reqs.path)
    yield mock_reqs
    remove_file(mock_reqs.name)


# Tests
def test_split_bucket_object_file(mock_bucket_name, mock_object_name, mock_model_name):
    """
    Tests that the split_bucket_object_file works
    when a file name is passed as input

    Args:
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
        mock_model_name: Mocks a file
    """
    bucket_name, object_name, file_name = split_bucket_object_file(
        path=f"gs://{mock_bucket_name}/{mock_object_name}/{mock_model_name}",
        file_name=mock_model_name,
    )

    assert bucket_name == mock_bucket_name
    assert object_name == str(mock_object_name)
    assert file_name == mock_model_name


def test_split_bucket_object_no_file(mock_bucket_name, mock_object_name):
    """
    Tests that the split_bucket_object_file works
    when no file name is passed as input

    Args:
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
    """
    bucket_name, object_name, file_name = split_bucket_object_file(
        path=f"gs://{mock_bucket_name}/{mock_object_name}/",
    )

    assert bucket_name == mock_bucket_name
    assert object_name == str(mock_object_name)
    assert file_name is None


def test_split_bucket_object_no_file_no_slash(mock_bucket_name, mock_object_name):
    """
    Tests that the split_bucket_object_filee works
    when no file name is passed as input and the object name
    is not properly parsed

    Args:
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
    """
    bucket_name, object_name, file_name = split_bucket_object_file(
        path=f"gs://{mock_bucket_name}/{mock_object_name}",
    )

    assert bucket_name == mock_bucket_name
    assert object_name == str(mock_object_name)
    assert file_name is None


def test_raise_error_model_name(mock_bucket_name, mock_object_name, mock_model_name):
    """
    Tests that the component raises a NameError if a wrong model name
    is used together with a pre-built container

    Args:
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
        mock_model_name: Mocks a file
    """
    with pytest.raises(NameError):
        upload_pytorch_model(
            project_id="test-project",
            location="europe-west2",
            gcs_model_path=f"gs://{mock_bucket_name}/{mock_object_name}/{mock_model_name}",
            model_name="test-name",
            model_display_name="test-name",
            local_model_file=mock_model_name,
            vertex_model=None,
            handler="text_classification",
        )


def test_raise_error_requirements(
    mock_bucket_name, mock_object_name, mock_model_name, mock_requirements_file
):
    """
    Tests that the component raises a TypeError if the model requires
    extra packages but the serving container used is the pre-built
    container, which does not allow for this

    Args:
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
        mock_model_name: Mocks a file
        mock_requirements_file: Mocks the requirements file
    """

    with pytest.raises(TypeError):
        upload_pytorch_model(
            project_id="test-project",
            location="europe-west2",
            gcs_model_path=f"gs://{mock_bucket_name}/{mock_object_name}/{mock_model_name}",
            model_display_name="test-name",
            local_model_file=mock_model_name,
            vertex_model=None,
            requirements=mock_requirements_file.path,
        )


@patch("subprocess.run")
def test_cmd_with_defaults(mock_subprocess, mock_model_name):
    """
    Tests that the run_command method correctly calls the torch-model-archiver
    when passed only default values

    Args:
        mock_subprocess: Mocks the subprocess.run execution
        mock_model_name: Mocks a model
    """
    # Prepare command for execution
    model_name = "model"
    handler = "default_handler"

    # Execute command
    cmd = run_command(
        model_name=model_name, serialized_file=mock_model_name, handler=handler
    )

    # Assert
    expected_cmd = [
        "torch-model-archiver",
        "-f",
        f"--model-name={model_name}",
        f"--serialized-file={mock_model_name}",
        f"--handler={handler}",
    ]

    assert cmd == expected_cmd


@patch("subprocess.run")
def test_cmd_with_extras(
    mock_subprocess, mock_model_name, mock_custom_handler, mock_requirements_file
):
    """
    Tests that the run_command method correctly calls the torch-model-archiver
    when additional optional arguments are passed

    Args:
        mock_subprocess: Mocks the subprocess.run execution
        mock_model_name: Mocks a model
        mock_custom_handler: Mocks the custom hanler file
        mock_requirements_file: Mocks the requirements file
    """
    # Prepare command for execution
    model_name = "model"
    extra_files = "file_1,file_2,path/file_3"
    version = "1.0"
    handler = mock_custom_handler.path
    requirements = mock_requirements_file.path

    # Execute command
    cmd = run_command(
        model_name=model_name,
        serialized_file=mock_model_name,
        extra_files=extra_files,
        version=version,
        handler=handler,
        requirements=requirements,
    )

    # Assert
    expected_cmd = [
        "torch-model-archiver",
        "-f",
        f"--model-name={model_name}",
        f"--serialized-file={mock_model_name}",
        f"--handler={handler}",
        f"--extra-files={extra_files}",
        f"--version={version}",
        f"--requirements-file={requirements}",
    ]

    assert cmd == expected_cmd


@patch("google.cloud.storage.Client")
def test_stage_one_file(mock_client, mock_bucket_name, mock_object_name, mock_pt_model):
    """
    Test that the stage_files_locally method can stage a single file
    when requested

    Args:
        mock_client: Mocks the GCS client google.cloud.storage.Client()
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
        mock_pt_model: Mocks a PyTorch model and blob
    """
    # Mock a GCS blob
    list_blobs = MockListBlobs()
    list_blobs.add_blob(mock_pt_model.blob)
    mock_client().list_blobs.return_value = list_blobs.list_blobs

    # Execute command to test
    stage_files_locally(
        bucket_name=mock_bucket_name,
        object_name=mock_object_name,
        file_name=mock_pt_model.name,
    )

    # Assert
    assert os.path.exists(mock_pt_model.name)


@patch("google.cloud.storage.Client")
def test_stage_all_files(
    mock_client,
    mock_bucket_name,
    mock_object_name,
    mock_pt_model,
    mock_custom_handler,
    mock_requirements_file,
):
    """
    Test that the stage_files_locally method can stage all files
    when requested

    Args:
        mock_client: Mocks the GCS client google.cloud.storage.Client()
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
        mock_pt_model: Mocks a PyTorch model and blob
        mock_custom_handler: Mocks a custom hanlder and blob
        mock_requirements_file: Mocks a requirements file and blob
    """
    # Mock multiple GCS blobs
    list_blobs = MockListBlobs()
    list_blobs.add_blob(mock_pt_model.blob)
    list_blobs.add_blob(mock_custom_handler.blob)
    list_blobs.add_blob(mock_requirements_file.blob)
    mock_client().list_blobs.return_value = list_blobs.list_blobs

    # Execute command to test
    extra_files = stage_files_locally(
        bucket_name=mock_bucket_name,
        object_name=mock_object_name,
        file_name="*",
        model_extra_files=True,
    )

    # Assert
    assert os.path.exists(mock_pt_model.name)
    assert os.path.exists(mock_custom_handler.name)
    assert os.path.exists(mock_requirements_file.name)
    assert (
        extra_files
        == f"{mock_pt_model.name},{mock_custom_handler.name},{mock_requirements_file.name}"
    )


@patch("google.cloud.storage.Client")
def test_stage_all_files_ignore(
    mock_client,
    mock_bucket_name,
    mock_object_name,
    mock_pt_model,
    mock_custom_handler,
    mock_requirements_file,
    mock_mar_model,
):
    """
    Test that the stage_files_locally method can stage all files
    apart from the ones to ignore when requested

    Args:
        mock_client: Mocks the GCS client google.cloud.storage.Client()
        mock_bucket_name: Mocks a GCS bucket
        mock_object_name: Mocks a GCS object
        mock_pt_model: Mocks a PyTorch model and blob
        mock_custom_handler: Mocks a custom hanlder and blob
        mock_requirements_file: Mocks a requirements file and blob
        mock_mar_model: Mocks a .mar file and blob
    """
    # Mock multiple GCS blobs
    list_blobs = MockListBlobs()
    list_blobs.add_blob(mock_pt_model.blob)
    list_blobs.add_blob(mock_custom_handler.blob)
    list_blobs.add_blob(mock_requirements_file.blob)
    list_blobs.add_blob(mock_mar_model.blob)  # This file will be ignored
    mock_client().list_blobs.return_value = list_blobs.list_blobs

    # Execute command to test
    extra_files = stage_files_locally(
        bucket_name=mock_bucket_name,
        object_name=mock_object_name,
        file_name="*",
        ignore_files=[mock_mar_model.name],
        model_extra_files=True,
    )

    # Assert
    assert os.path.exists(mock_pt_model.name)
    assert os.path.exists(mock_custom_handler.name)
    assert os.path.exists(mock_requirements_file.name)
    assert os.path.exists(mock_mar_model.name) is False  # This file should not exist
    assert (
        extra_files
        == f"{mock_pt_model.name},{mock_custom_handler.name},{mock_requirements_file.name}"
    )
