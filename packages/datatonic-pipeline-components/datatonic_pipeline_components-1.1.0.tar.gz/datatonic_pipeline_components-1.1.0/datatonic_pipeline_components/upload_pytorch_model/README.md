# PyTorch Model - Upload to Vertex Model Registry
This component receives as an input a trained PyTorch model artifact stored in GCS and
outputs a Vertex Model uploaded in Vertex Model Registry and ready to serve predictions
in an Endpoint or via Batch Predictions

Optionally, this component also accepts a custom tokenizer as input, if this tokenizer
is used to serve predictions.

The logic of the component is as follows:
1. Stage all required files (saved in GCS) locally in the component execution environment
2. Use `torch-model-archiver` to package the model into the required format for deployment and with the requried files included in the package. This returns a <model_name>.mar file.
3. Upload the packaged model (`<model_name>.mar`) back to GCS
4. Upload the packaged model to the Vertex Model Registry together with either a pre-built container or a custom container

For more information on torch-model-archiver refer to
https://github.com/pytorch/serve/blob/master/model-archiver/README.md

## Using `torch-model-archiver`
Please refer to the above link for more details of what each of the flags below represent. This documentation page will explain hwo to define these values.
#### `model-name`
This is the model name given to the output `.mar` file. It is mapped to the `model_name` argument. It is a mandatory argument.
#### `serialized-file`
This is the actual trained model/checkpoint file artifact. It is mapped to the `local_model_file` argument. It is a mandatory argument.

#### `extra-files`
This refers to all additional and optional files that need to be included in the package to serve predictions. These are the files that don't come in the container image by default.
These files could refer to:
1. Model files: files required to define the model. When you train a HuggingFace model, the output of the training job is a `pytorch_model.bin` file and many other files required to compile the model during predictions. These additional files are an example of model files.
2. Prediction files: files relevant to pre-processing or post-processing of predictions, for example files that map indices to classes, etc. These files are not dependant on the training job being completed, and should be uploaded to GCS prior to the training pipeline execution.
3. Custom tokenizer: if your model uses a custom tokenizer, the actual tokenizer artifact (ie: `.pkl`, etc) must be included as an `extra-file`

The files required for #1 are obtained via the `gcs_model_path` argument, which points to the model and the extra model files.
The files required for #2 must be uploaded to GCS prior to the training job into the `extra_files_staging_path` folder.
The custom tokenizer for #3 must be defined with `custom_tokenizer_path`.
#### `handler`
This is an optional argument, used when a custom prediction routine in used. This is the case for most GPT-like of HuggingFace models. The custom handler script must be uploaded to `extra_files_staging_path` prior to the execution of the pipeline, and the script name must be defined in `handler`.
#### `requirements-file`
This is an optional argument, used when additional packages are required to serve predictions. The requirements file must be uploaded to `extra_files_staging_path` prior to the execution of the pipeline, and the file name must be defined in `requirements`.

## Including custom dependencies and packages
Both the pre-built container and any custom container you build for predictions run with
TorchServe https://github.com/pytorch/serve. TorchServe offers a built-in prediction handler
routine to serve your model. However, if your model requires a custom prediction routine
you will need to provide a custom handler as input, and this handler will be part of the
packaged `.mar` file. 

Note that if this prediction routine requires extra packages not
included in the base pre-built container image, you will need to use a custom container
for your predictions. Most importantly, this custom container contains a file called
`config.properties`, which should have a new entry called `install_py_dep_per_model=true`.

An example of a `config.properties` file that accepts custom packages is as follows:
```
inference_address=http://0.0.0.0:8080
management_address=http://0.0.0.0:8081
metrics_address=http://0.0.0.0:8082
number_of_netty_threads=32
job_queue_size=1000
model_store=/home/model-server/model-store
workflow_store=/home/model-server/wf-store

service_envelope=json
enable_envvars_config=true
install_py_dep_per_model=true
```

## Serving Predictions with GPU
This component works in the same way independently of if a GPU is required for serving or not.
No additional input or flag is required.
To use a GPU the two requirements are:
1. The `serving_container_image_uri` has the GPU drivers installed.
2. The `handler` file, which is the file that runs the predictions, initialises the model
with `cuda` when loading the model.
## Inputs
|Name|Type|Default|Description|
|----|----|----|----|
|project_id|str| |GCP project ID|
|location|str| |GCP location|
|gcs_model_path|Artifact| |KFP artifact that includes the path to the model artifact in the uri|
|local_model_file|str| |File name of the model artifact (ie: pytorch_model.bin)|
|model_display_name|str| |Display name for Vertex Model in the Model Registry|
|model_name|str|'model'|Model name used for TorchServe (recommended to leave as default 'model')|
|version|str|'v1.0'|Model version used for TorchServe (recommended to leave as default 'v1.0')|
|extra_files_to_ignore|list| |List of files included in the GCS model folder that you don't wish to include in the .mar package|
|extra_files_staging_path|str| |Path to GCS folder that contains additional files that must be included in the .mar package|
|extra_prediction_files|str| |Name of additional files that must be included in the .mar package for serving predictions|
|handler|str| |Name of custom handler file used for serving. If using the default TorchServe one leave this blank|
|requirements|str| |Additional packages required by the model for serving predictions|
|custom_tokenizer_path|str| |Path to GCS file where the custom tokenizer is located. Leave blank if your model uses a default tokenizer|
|custom_tokenizer_name|str| |Name of custom tokenizer. Leave blank if your model uses a default tokenizer|
|custom_container|bool|False|Whether to use a custom container or the pre-built container. If using a custom, the arguments below will be used|
|serving_container_image_uri|str| europe-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-12:latest |Path to container image used for serving. Uses the pre-built Vertex container by default|
|health_route|str|/ping|Overwrites the default health route in the serving container. Must be set to "/ping". Only used if custom_container=True|
|predict_route|str|/predictions/model|Overwrites the default prediction route in the serving container. Must be set to "/predictions/<model-name>". Only used if custom_container=True|
|serving_container_ports|list| |Overwrites the default ports in the serving container. Only used if custom_container=True|
|serving_environment_vars|dict| |Overwrites the default environment variables in the serving container. Only used if custom_container=True|
|serving_container_args|list| |Overwrites the CMD of the Vertex pre-built container. Only used if custom_container=False|
|serving_container_command|list| |Overwrites the ENTRYPOINT of the Vertex pre-built container. Only used if custom_container=False|
|model_description|str| |Model description used in the Model Registry|
|parent_model|str| |The resource name or model ID of an existing model that the newly-uploaded model will be a version of. Only set this field when uploading a new version of an existing model.|
|is_default_version|bool|False|When set to True, the newly uploaded model version will automatically have alias "default" included. Subsequent uses of this model without a version specified will use this "default" version. When set to False, the "default" alias will not be moved. Actions targeting the newly-uploaded model version will need to specifically reference this version by ID or alias. New model uploads, i.e. version 1, will always be "default" aliased.|
|version_description|str| |The description of the model version being uploaded.|

## Outputs
|Name|Type|Default|Description|
|---|---|---|---|
|vertex_model|Artifact||Vertex model in Model Registry. Metadata includes: <br> 1. DisplayName - Display name shown in Vertex Model Registry - <br> 2. VertexModelID - Full path to Vertex Model Registry ID (<project>/<location>/model/ID)|

## Container image
```
europe-west2-docker.pkg.dev/dt-alvaro-sandbox-dev/pytorch-custom-serving-image/upload_pytorch_model:latest  
```
*TODO: Change this once we have an official docker image registry*

## Usage - Pre-built Container

```python
import kfp
from kfp import components

#Use the component as part of the pipeline
@kfp.dsl.pipeline(name='Upload PyTorch Model to Vertex Model Registry')
def pipeline():

    # Train tokenizer
    tokenizer_op = tune_tokenizer()
    # Train model
    train_model_op = train_model()

    # Load component
    filename = "./component.yaml"
    create_component_op = components.load_component_from_file('./component.yaml')

    # Instantiate component
    upload_model_to_vertex = create_component_op(
        project_id = <gcp-project-id>,
        location = <gcp-location>,
        gcs_model_path = train_model_op.output,
        model_display_name = "dummy-model-example-docs",
        local_model_file = "ckpt.pt",
        extra_files_staging_path = <gcs-path-to-object-with-extra-files>,
        serving_container_image_uri = "europe-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-12:latest"
        extra_prediction_files = "file_1.py,file_2.py,file_3.json",
        handler = "custom_handler.py",
        custom_tokenizer_path=tokenizer_op.outputs['path-to-tokenizer'],
        custom_tokenizer_name=custom_tokenizer_name
    )
```
If additional packages are required (defined via the `requirements.txt`), or you want to customise the configuration of the TorchServe server (using the `config.properties` file) you will need to use a custom container instead.
## Usage - Custom Container

```python
import kfp
from kfp import components

#Use the component as part of the pipeline
@kfp.dsl.pipeline(name='Upload PyTorch Model to Vertex Model Registry')
def pipeline():

    # Train tokenizer
    tokenizer_op = tune_tokenizer()
    # Train model
    train_model_op = train_model()

    # Load component
    filename = "./component.yaml"
    create_component_op = components.load_component_from_file('./component.yaml')

    # Instantiate component
    upload_model_to_vertex = create_component_op(
        project_id = <gcp-project-id>,
        location = <gcp-location>,
        gcs_model_path = train_model_op.output,
        model_display_name = "dummy-model-example-docs",
        model_name='custom_model',
        local_model_file = "ckpt.pt",
        extra_files_staging_path = <gcs-path-to-object-with-extra-files>,
        custom_container = True,
        serving_container_image_uri = "europe-west2-docker.pkg.dev/dt-alvaro-sandbox-dev/pytorch-custom-serving-image/torchserve-gpu:latest",
        predict_route = f"/predictions/custom_model",
        serving_environment_vars = {"MODEL_NAME":"custom_model"},
        health_route = "/ping",
        serving_container_ports = [8080],
        extra_prediction_files = "file_1.py,file_2.py,file_3.json",
        handler = "custom_handler.py",
        requirements = "requirements.txt", # If this is required, you must use a custom container
        custom_tokenizer_path=tokenizer_op.outputs['path-to-tokenizer'],
        custom_tokenizer_name=custom_tokenizer_name
    )
```
