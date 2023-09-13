# HuggingFace TensorFlow Model Loader

This Kubeflow component loads a TensorFlow model, its configuration, and its tokenizer from HuggingFace and saves the artifacts in Google Cloud Storage.

## Inputs
|Name|Type|Default|Description|
|---|---|---|---|
|model_class_name|String||HuggingFace [model class name](https://huggingface.co/docs/transformers/model_doc/auto) (e.g., "TFAutoModelForCasualLM").|
|tokenizer_class_name|String||HuggingFace [tokenizer class name](https://huggingface.co/docs/transformers/model_doc/auto) (e.g., "AutoTokenizer").|
|config_name|String||HuggingFace [config class name](https://huggingface.co/docs/transformers/model_doc/auto) (e.g., "AutoConfig").|
|model_name|String||HuggingFace model name (e.g., "bert-base-uncased").|
|model_args|Dictionary|{}|Optional additional model arguments passed to the model class.|
|kwargs|Dictionary|{}|Optional additional keywords required by the model, config, and tokenizer classes. The expected format is:<br>`{"model": {"key_model_arg_1": value_1, "key_model_arg_2": value_2}, "config": {"key_config_arg_1": value_1, "key_config_arg_2": value_2}, "token": {"key_token_arg_1": value_1, "key_token_arg_2": value_2}}`.|

## Outputs
|Name|Type|Default|Description|
|---|---|---|---|
|hf_gcs_path|Artifact||Path to GCS objects with saved model artifacts.|

## Usage

```python
import kfp
from kfp.components import OutputPath

# Use the component as part of the pipeline
@kfp.dsl.pipeline(name='HuggingFace TensorFlow Model Loader pipeline')
def pipeline_running_hf_model_loader(
    model_class_name: str, 
    tokenizer_class_name: str, 
    config_name: str, 
    model_name: str, 
    model_args: dict = {}, 
    kwargs: dict = {}):
    # Load component
    filename = "./component.yaml"
    create_component_op = comp.load_component_from_file(filename)

    # Instantiate component
    component_op = (create_component_op(
        model_class_name=model_class_name,
        tokenizer_class_name=tokenizer_class_name,
        config_name=config_name,
        model_name=model_name,
        model_args=model_args,
        kwargs=kwargs
    ).set_display_name("Load HuggingFace TensorFlow Model"))

    # Use output in the next pipeline step
    next_step = next_pipeline_step(component_op.outputs['hf_gcs_path'])
```
where the `parameter_values` can be defined as:
```
parameter_values={
    "model_class_name":"TFAutoModel",
    "config_name":"AutoConfig",
    "tokenizer_class_name":"AutoTokenizer",
    "model_name":"bert-base-cased",
    "kwargs":{
        "model":
            {"force_download":False},
        "token":
            {"force_downlowad":True,
            "fast_tokenizer":False,
            "pad_token":"[pad]",
            "do_basic_tokenize":False}
    }
}
```
