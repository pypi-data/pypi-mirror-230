import os
from pathlib import Path
from kfp.dsl import Output, Input, Artifact, component, Model

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
def upload_pytorch_model(
    project_id: str,
    location: str,
    gcs_model_path: Input[Artifact],
    local_model_file: str,
    vertex_model: Output[Model],
    model_display_name: str,
    handler: str,
    model_name: str = "model",
    version: str = "v1.0",
    extra_files_to_ignore: list = [],
    extra_files_staging_path: str = None,
    extra_prediction_files: str = None,
    requirements: str = None,
    custom_tokenizer_path: str = None,
    custom_tokenizer_name: str = None,
    custom_container: bool = False,
    serving_container_image_uri: str = "europe-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-12:latest",
    health_route: str = "/ping",
    predict_route: str = "/predictions/model",
    serving_container_ports: list = [8080],
    serving_environment_vars: dict = {"MODEL_NAME": "model"},
    serving_container_args: list = None,
    serving_container_command: list = None,
    model_description: str = None,
    parent_model: str = None,
    is_default_version: bool = True,
    version_description: str = None,
):
    """
    This component receives as an input a trained PyTorch model artifact stored in GCS and
    outputs a Vertex Model uploaded in Vertex Model Registry and ready to serve predictions
    in an Endpoint or via Batch Predictions

    Optionally, this component also accepts a custom tokenizer as input, if this tokenizer
    is used to serve predictions.

    The logic of the component is as follows:
    1. Stage all required files (saved in GCS) locally in the component execution environment
    2. Use `torch-model-archiver` to package the model into the required format for deployment
        and with the requried files included in the package. This returns a <model_name>.mar file.
    3. Upload the packaged model (`<model_name>.mar`) back to GCS
    4. Upload the packaged model to the Vertex Model Registry together with either a pre-built
        container or a custom container

    For more information on torch-model-archiver refer to
    https://github.com/pytorch/serve/blob/master/model-archiver/README.md

    Both the pre-built container and any custom container you build for predictions run with
    TorchServe https://github.com/pytorch/serve TorchServe offers a built-in prediction handler
    routine to serve your model. However, if your model requires a custom prediction routine
    you will need to provide a custom handler as input, and this handler will be part of the
    packaged .mar file. Note that if this prediction routine requires extra packages not
    included in the base pre-built container image, you will need to use a custom container
    for your predictions. Most importantly, this custom container contains a file called
    config.properties, which should have a new entry called install_py_dep_per_model=true.

    Args:
        project_id: str - GCP project ID
        location: str - GCP location
        gcs_model_path: Artifact - KFP artifact that includes the path to the model artifact in the uri
        local_model_file: str - File name of the model artifact (ie: pytorch_model.bin)
        model_display_name: str - Display name for Vertex Model in the Model Registry
        handler: str - Name of custom handler file used for serving. If using the default
            TorchServe one provide its name
        model_name: str - Model name used for TorchServe (recommended to leave as default 'model')
        version: str - Model version used for TorchServe (recommended to leave as default 'v1.0')
        extra_files_to_ignore: list - List of files included in the GCS model folder that you don't
            wish to include in the .mar package
        extra_files_staging_path: str - Path to GCS folder that contains additional files that must
            be included in the .mar package
        extra_prediction_files: str - Name of additional files that must be included in the .mar
            package for serving predictions
        requirements: str - Additional packages required by the model for serving predictions
        custom_tokenizer_path: str - Path to GCS file where the custom tokenizer is located.
            Leave blank if your model uses a default tokenizer
        custom_tokenizer_name: str - Name of custom tokenizer. Leave blank if your model uses
            a default tokenizer
        custom_container: bool - Whether to use a custom container or the pre-built container.
            If using a custom, the arguments below will be used
        serving_container_image_uri: str - Path to container image used for serving.
            Uses the pre-built Vertex container by default
        health_route: str - Overwrites the default health route in the serving container.
            Must be set to "/ping". Only used is custom_container=True
        predict_route: str - Overwrites the default prediction route in the serving container.
            Must be set to "/predictions/model"". Only used is custom_container=True
        serving_container_ports: list - Overwrites the default ports in the serving container.
            Only used is custom_container=True
        serving_environment_vars: dict - Overwrites the default environment variables in the serving container.
            Only used is custom_container=True
        serving_container_args: list - Overwrites the CMD of the Vertex pre-built container.
            Only used is custom_container=False
        serving_container_command: list - Overwrites the ENTRYPOINT of the Vertex pre-built container.
            Only used is custom_container=False
        model_description: str - Model description used in the Model Registry
        parent_model: str - The resource name or model ID of an existing model that the
            newly-uploaded model will be a version of. Only set this field when uploading a
            new version of an existing model.
        is_default_version: bool - When set to True, the newly uploaded model version will
            automatically have alias "default" included. Subsequent uses of this model without
            a version specified will use this "default" version. When set to False, the "default"
            alias will not be moved. Actions targeting the newly-uploaded model version will
            need to specifically reference this version by ID or alias. New model uploads,
            i.e. version 1, will always be "default" aliased.,
        version_description: str - The description of the model version being uploaded.,

    Returns:
        vertex_model: Model - Vertex model in Model Registry. Metadata includes:
            DisplayName - Display name shown in Vertex Model Registry
            VertexModelID - Full path to Vertex Model Registry ID (<project>/<location>/model/ID)
    """

    from google.cloud import aiplatform

    from upload_pytorch_model.utils.gcs_helper import split_bucket_object_file
    from upload_pytorch_model.utils.model_archiver import create_model_archiver

    # Run checks to ensure variables are valid
    if not custom_container and model_name != "model":
        print("Wrong model_name specified")
        raise NameError(
            f"""
        When using the pre-built PyTorch container the model_name must be 'model' but you selected {model_name}
        """
        )

    if not custom_container and requirements:
        print("Custom container not being used with custom packages")
        raise TypeError(
            f"""
        If your model requires extra packages you must use a custom container for serving predictions
        """
        )

    # Extract the correct model folder
    gcs_model_full_path = gcs_model_path.uri
    model_bucket_name, model_object_name, _ = split_bucket_object_file(
        path=gcs_model_full_path, file_name=local_model_file
    )
    gcs_model_path = f"gs://{model_bucket_name}/{model_object_name}"

    # Package model into .mar
    create_model_archiver(
        gcs_model_path=gcs_model_path,
        model_name=model_name,
        version=version,
        local_model_file=local_model_file,
        extra_files_staging_path=extra_files_staging_path,
        extra_files_to_ignore=extra_files_to_ignore,
        extra_prediction_files=extra_prediction_files,
        handler=handler,
        requirements=requirements,
        custom_tokenizer_path=custom_tokenizer_path,
        custom_tokenizer_name=custom_tokenizer_name,
    )

    # Define container serving variables
    serving_container_predict_route = predict_route if custom_container else None
    serving_container_environment_variables = (
        serving_environment_vars if custom_container else None
    )
    serving_container_health_route = health_route if custom_container else None
    serving_container_ports = serving_container_ports if custom_container else None

    # Upload to Vertex Model Registry
    aiplatform.init(project=project_id, location=location)

    model = aiplatform.Model.upload(
        display_name=model_display_name,
        description=model_description,
        serving_container_image_uri=serving_container_image_uri,
        serving_container_predict_route=serving_container_predict_route,
        serving_container_health_route=serving_container_health_route,
        serving_container_ports=serving_container_ports,
        serving_container_command=serving_container_command,
        serving_container_environment_variables=serving_container_environment_variables,
        serving_container_args=serving_container_args,
        artifact_uri=gcs_model_path,
        parent_model=parent_model,
        is_default_version=is_default_version,
        version_description=version_description,
    )

    model.wait()

    vertex_model.metadata["DisplayName"] = model.display_name
    vertex_model.metadata["VertexModelID"] = model.resource_name
    vertex_model.uri = model.resource_name
