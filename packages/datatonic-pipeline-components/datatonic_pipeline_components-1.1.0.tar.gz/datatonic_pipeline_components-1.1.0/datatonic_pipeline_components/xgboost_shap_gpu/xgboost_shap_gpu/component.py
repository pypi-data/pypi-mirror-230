import os
from pathlib import Path
from kfp.dsl import component, Model, Input, Output, Artifact

_COMPONENTS_CONTAINER_REGISTRY = os.environ.get(
    "COMPONENTS_CONTAINER_REGISTRY",
    "europe-west2-docker.pkg.dev/dt-pc-dev/dt-pc-dev-components-repository",
)
_IMAGE_NAME = str(Path(__file__).parent.name)
_COMPONENTS_IMAGE_TAG = os.environ.get("COMPONENTS_IMAGE_TAG", "latest")


@component(
    base_image="nvidia/cuda:11.3.0-base-ubuntu18.04",
    target_image=f"{_COMPONENTS_CONTAINER_REGISTRY}/{_IMAGE_NAME}:{_COMPONENTS_IMAGE_TAG}",  # noqa: E501
    output_component_file=os.path.splitext(__file__)[0] + ".yaml",
)
def gpu_accelerated_shap_for_xgboost(
    input_data: Input[Artifact],
    model: Input[Model],
    output_shap_values: Output[Artifact],
    enable_gpu: bool = True,
):
    """
    This function is a kfp component that explains an XGBoost model's predictions
    using the SHAP library.
    This component uses a base_image that has nvidia/cuda drivers installed.

    Args:
        input_data (Input[Artifact]): CSV file with pre-processed data stored on GCS.
        model (Input[Model]): The XGBoost model.joblib file stored in GCS in the format
            "gs://my-bucket/path/to/model/model.joblib".
        output_feature_attributions (Output[Artifact]): CSV file with output
            feature attribution data stored on GCS.
        enable_gpu (bool): Boolean flag to enable computation using GPU
    """
    import logging
    import pandas as pd
    from xgboost_shap_gpu.utils import calculate_shap_values, load_joblib_model

    logging.getLogger().setLevel(logging.INFO)

    # Get model and data
    xgb_model = load_joblib_model(model_path=model.path)
    input_df = pd.read_csv(input_data.path)

    # Calculate shap values with gpu
    shap_values = calculate_shap_values(xgb_model, input_df, enable_gpu)

    # Create column names
    feature_names = list(input_df.columns)

    # Create final df
    shap_df = pd.DataFrame(shap_values, columns=feature_names)

    # Upload to GCS
    output_shap_values.path += ".csv"
    shap_df.to_csv(output_shap_values.path, index=False)
    logging.info(f"Successfully uploaded to {output_shap_values.path}")
