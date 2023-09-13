"""Unit tests for component that loads TensorFlow models from HuggingFace"""
import os
import pytest
from unittest.mock import Mock

from tempfile import TemporaryDirectory

from component import (
    load_tf_hf_model as load_tf_hf_model_component,
)

load_tf_hf_model = load_tf_hf_model_component.python_func


def test_loads_model_config():
    """Test model config is correctly loaded"""
    with TemporaryDirectory() as tmp_dir:
        hf_gcs_path = Mock(path=tmp_dir)
        load_tf_hf_model(
            "TFAutoModel",
            "AutoTokenizer",
            "AutoConfig",
            "bert-base-uncased",
            hf_gcs_path,
        )
        assert os.path.exists(os.path.join(tmp_dir, "config.json"))


def test_loads_model():
    """Test model is correctly loaded"""
    with TemporaryDirectory() as tmp_dir:
        hf_gcs_path = Mock(path=tmp_dir)
        load_tf_hf_model(
            "TFAutoModel",
            "AutoTokenizer",
            "AutoConfig",
            "bert-base-uncased",
            hf_gcs_path,
        )
        assert os.path.exists(os.path.join(tmp_dir, "tf_model.h5"))


def test_loads_tokenizer():
    """Test tokenizer is correctly loaded"""
    with TemporaryDirectory() as tmp_dir:
        hf_gcs_path = Mock(path=tmp_dir)
        load_tf_hf_model(
            "TFAutoModel",
            "AutoTokenizer",
            "AutoConfig",
            "bert-base-uncased",
            hf_gcs_path,
        )
        assert os.path.exists(os.path.join(tmp_dir, "tokenizer.json"))


def test_loads_additional_args():
    """Test additional arguments are correctly parsed"""
    with TemporaryDirectory() as tmp_dir:
        hf_gcs_path = Mock(path=tmp_dir)
        model_args = {"output_attentions": True}
        kwargs = {
            "model": {"force_download": False},
            "config": {"max_length": 128},
            "token": {"do_lower_case": True},
        }
        load_tf_hf_model(
            "TFAutoModel",
            "AutoTokenizer",
            "AutoConfig",
            "bert-base-uncased",
            hf_gcs_path,
            model_args=model_args,
            kwargs=kwargs,
        )
        assert os.path.exists(os.path.join(tmp_dir, "config.json"))
        assert os.path.exists(os.path.join(tmp_dir, "tf_model.h5"))
        assert os.path.exists(os.path.join(tmp_dir, "tokenizer.json"))


def test_tensorflow_raises_error():
    """Test PyTorch models correctly raise an error"""
    with TemporaryDirectory() as tmp_dir:
        hf_gcs_path = Mock(path=tmp_dir)
        with pytest.raises(NameError):
            load_tf_hf_model(
                "AutoModel",
                "AutoTokenizer",
                "AutoConfig",
                "bert-base-uncased",
                hf_gcs_path,
            )
