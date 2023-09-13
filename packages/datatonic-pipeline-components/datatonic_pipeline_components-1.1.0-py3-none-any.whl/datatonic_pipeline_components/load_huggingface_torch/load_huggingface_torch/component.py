"""KFP component to load PyTorch model from HuggingFace into GCS"""
import os
from pathlib import Path
from kfp.dsl import Output, Artifact, component

_COMPONENTS_CONTAINER_REGISTRY = os.environ.get(
    "COMPONENTS_CONTAINER_REGISTRY",
    "europe-west2-docker.pkg.dev/dt-pc-dev/dt-pc-dev-components-repository",
)
_IMAGE_NAME = str(Path(__file__).parents[1].name)
_COMPONENTS_IMAGE_TAG = os.environ.get("COMPONENTS_IMAGE_TAG", "latest")


@component(
    base_image="python:3.9-slim-buster",
    target_image=f"{_COMPONENTS_CONTAINER_REGISTRY}/{_IMAGE_NAME}:{_COMPONENTS_IMAGE_TAG}",  # noqa: E501
    output_component_file=os.path.splitext(__file__)[0] + ".yaml",
)
def load_hf_model(
    model_class_name: str,
    tokenizer_class_name: str,
    config_name: str,
    model_name: str,
    hf_gcs_path: Output[Artifact],
    model_args: dict = {},
    kwargs: dict = {},
):
    """
    Loads PyTorch model, config and tokenizer from HuggingFace
    and stores artefacts in GCS

    Args:
        model_class_name [str]: HuggingFace class to import model from (ie: AutoModelForCasualLM)
        tokenizer_class_name [str]: HuggingFace class to import tokenizer from (ie: AutoTokenizer)
        config_name [str]: HuggingFace class to import config from (ie: AutoConfig)
        model_name [str]: HuggingFace repo model name (ie: bert-base-uncased)
        model_args [dict]: Optinal additional model arguments passed to model class
        kwargs [dict]: Optional additional keywords required by model, config and tokenizer classes.
            The required format is:
                kwargs = {
                    "model":
                        {
                            "key_model_arg_1":value_1,
                            "key_model_arg_2":value_2,
                        },
                    "config":
                        {
                            "key_config_arg_1":value_1,
                            "key_config_arg_2":value_2,
                        },
                    "token":
                        {
                            "key_token_arg_1":value_1,
                            "key_token_arg_2":value_2,
                        },
                }

    Returns:
        hf_gcs_path [Artifact]: Path to GCS objects with model artifacts
    """
    # Import transformers and required classes
    import transformers

    # Raise error in TensorFlow model selected
    if model_class_name.startswith("TF"):
        raise NameError(
            """
        This component only accepts PyTorch models but you selected
        a TensorFlow model. Please use the other component in this library for TensorFlow models
        """
        )

    model_class = getattr(transformers, model_class_name)
    config_class = getattr(transformers, config_name)
    tokenizer_class = getattr(transformers, tokenizer_class_name)

    # Load optional additional args
    config_kwargs = kwargs.get("config", {})
    model_kwargs = kwargs.get("model", {})
    token_kwargs = kwargs.get("token", {})

    # Load model config
    model_config = config_class.from_pretrained(model_name, **config_kwargs)

    # Load model
    model = model_class.from_pretrained(
        model_name,
        config=model_config,
        *model_args,
        **model_kwargs,
    )

    # Load tokenizer
    tokenizer = tokenizer_class.from_pretrained(model_name, **token_kwargs)

    # Save model artifacts in GCS
    model.save_pretrained(save_directory=hf_gcs_path.path)
    tokenizer.save_pretrained(save_directory=hf_gcs_path.path)
