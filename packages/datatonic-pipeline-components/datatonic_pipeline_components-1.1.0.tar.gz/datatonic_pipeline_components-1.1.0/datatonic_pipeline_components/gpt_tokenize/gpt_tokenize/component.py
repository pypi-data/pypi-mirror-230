import logging
import os
from pathlib import Path

import numpy as np
import tiktoken
from kfp.dsl import Artifact, Dataset, Input, Output, component

_COMPONENTS_CONTAINER_REGISTRY = os.environ.get(
    "COMPONENTS_CONTAINER_REGISTRY",
    "europe-west2-docker.pkg.dev/dt-pc-dev/dt-pc-dev-components-repository",
)
_IMAGE_NAME = str(Path(__file__).parents[1].name)
_COMPONENTS_IMAGE_TAG = os.environ.get("COMPONENTS_IMAGE_TAG", "latest")


@component(
    base_image="python:3.9-slim",
    packages_to_install=[
        "numpy==1.21.6",
        "google-cloud-storage==1.44.0",
        "tiktoken==0.3.0",
    ],
    target_image=f"{_COMPONENTS_CONTAINER_REGISTRY}/{_IMAGE_NAME}:{_COMPONENTS_IMAGE_TAG}",
    output_component_file=str(Path(__file__).with_suffix(".yaml")),
)
def gpt_tokenize(
    input_data: Input[Artifact],
    train_dataset: Output[Dataset],
    val_dataset: Output[Dataset],
    train_size: float = 0.9,
    encoding_type: str = "gpt2",
):
    """
    Reads the scraped data and generates a tokenized training and validation dataset

    Args:
        input_data (Input[Artifact]): Input text file contain training data
        train_dataset (Output[Dataset]): Training ids as a dataset object
        val_dataset (Output[Dataset]): Validation ids as a dataset object
        train_size (float): A value between 0.0 and 1.0 to represent the proportion of the dataset
            to include in the train split
        encoding_type (str): Encodings used by OpenAI models. Defaults to "gpt2", alternatives include
            "cl100k_base" or "p50k_base". See
            https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
            for more details.
    """

    with open(
        os.path.join(input_data.path, "input.txt"), "r", encoding="utf-8"
    ) as file:
        data = file.read()

    logging.info(
        "Splitting data. Training set will be %s%% of the full data", train_size * 100
    )
    n = len(data)
    train_data = data[: int(n * train_size)]
    val_data = data[int(n * train_size) :]

    logging.info("Using %s encodings to encode data", encoding_type)
    enc = tiktoken.get_encoding(encoding_type)
    train_ids = enc.encode_ordinary(train_data)
    val_ids = enc.encode_ordinary(val_data)
    logging.info("train has %s tokens", len(train_ids))
    logging.info("val has %s tokens", len(val_ids))

    # export to bin files
    train_ids = np.array(train_ids, dtype=np.uint16)
    val_ids = np.array(val_ids, dtype=np.uint16)

    os.makedirs(train_dataset.path, exist_ok=True)
    os.makedirs(val_dataset.path, exist_ok=True)

    train_dataset_uri = os.path.join(train_dataset.path, "train.bin")
    val_dataset_uri = os.path.join(val_dataset.path, "val.bin")
    train_ids.tofile(train_dataset_uri)
    logging.info("Saving train_ids as %s ", train_dataset_uri)
    val_ids.tofile(val_dataset_uri)
    logging.info("Saving test_ids as %s ", val_dataset_uri)
