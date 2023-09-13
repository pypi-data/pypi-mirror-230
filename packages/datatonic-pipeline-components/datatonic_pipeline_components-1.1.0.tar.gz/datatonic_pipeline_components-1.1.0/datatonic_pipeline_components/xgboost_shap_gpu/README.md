# XGBoost Explainability - GPU accelerated shap
This component computes feature attributions of an XGBoost model using GPU accelerated SHAP. The use of accelerated calculations using a GPU is enabled by default. The user can decide to only use the CPU of a machine by setting the `enable_gpu=False` when using the component. 

## Inputs
|Name|Type|Default|Description|
|---|---|---|---|
|input_data|Artifact||CSV file with pre-processed data stored on GCS.|
|model|Model||GCS artifact with trained XGBoost model saved as a `.joblib`. format|
|enable_gpu|bool||Boolean flag to enable computation using GPU|

## Outputs
|Name|Type|Default|Description|
|---|---|---|---|
|output_shap_values|Artifact||Local or GCS artifact specifying with saved calculated feature attributions in CSV format.|

## Container image
europe-west4-docker.pkg.dev/dt-jan-sandbox-dev/docker-images/xgboost_shap_gpu:latest  *TODO: Change this once we have an official docker image registry*

## Usage

```python
import kfp

#Use the component as part of the pipeline
@kfp.dsl.pipeline(name='GPU Accelerated SHAP pipeline for XGBoost')
def pipeline_running_xgboost_gpu_accelerated_shap_values():
    # Load component
    filename = "./component.yaml"
    create_component_op = comp.load_component_from_file(filename)

    # Instantiate component, specifying GPU parameters
    component_op = (create_component_op(
            input_data=prior_component.outputs["input_data"],
            model=prior_component.outputs["input_model"],
            )
            .set_display_name("Explain test data")
            .add_node_selector_constraint(
                "cloud.google.com/gke-accelerator", value="nvidia-tesla-t4"
            )
        )
    component_op.container.set_gpu_limit(1)
```

OR using from [create_custom_training_job_from_component](https://cloud.google.com/vertex-ai/docs/pipelines/customjob-component#create_custom_training_job_from_component)

```python
import kfp
from google_cloud_pipeline_components.v1.custom_job import create_custom_training_job_from_component

@kfp.dsl.pipeline(name='GPU Accelerated SHAP pipeline for XGBoost')
def pipeline_running_xgboost_gpu_accelerated_shap_values():
    # Load component spec
    filename = "./component.yaml"
    create_component_op = comp.load_component_from_file(filename)

    # Instantiate custom training job spec, specifying machine type and GPU parameters
    custom_training_spec = create_custom_training_job_from_component(
        component_spec=create_component_op,
        display_name="Explain Test Data with GPU",
        machine_type="n1-highmem-2",
        accelerator_type="NVIDIA_TESLA_T4",
        accelerator_count=1
    )
    training_job = custom_training_spec(
        project=PROJECT_ID,
        location=LOCATION,
        input_data=prior_component.outputs["input_data"],
        model=prior_component.outputs["input_model"],
    )
```

## Further Work
- Add support for additional input/output types such as BigQuery or export to different file formats such as parquet and jsonl
