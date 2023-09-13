# Datatonic Pipeline Components

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/datatonic-pipeline-components)
![PyPI](https://img.shields.io/pypi/v/datatonic-pipeline-components)
![PyPI - License](https://img.shields.io/pypi/l/datatonic-pipeline-components)

Datatonic Pipeline Components (DTPC) is a set of Kubeflow (KFP) components that can be run on any KFP pipeline execution backend. The components can be composed together into pipelines using the Kubeflow Pipelines SDK.

## What is this?

Datatonic Pipeline Components is a library of reusable
[Kubeflow Pipeline](https://www.kubeflow.org/docs/components/pipelines/v2/introduction/)
components. These components have been designed and open sourced to make pipeline
development easier and more enjoyable. The components are well tested and the containers
on which they are built are scanned for vulnerabilities so that you can have confidence
in their performance and security.

## Installation

Install using pip:

```
pip install datatonic-pipeline-components
```

## Components

Here we list out the components that are available via the library. See the [How to use](#how-to-use) section
for an example of using a component in a pipeline.

- load_huggingface_torch - Loads a PyTorch model, its configuration, and its tokenizer from HuggingFace and saves the artifacts in Google Cloud Storage. [Detailed Documentation](datatonic_pipeline_components/load_huggingface_torch/README.md).
- load_huggingface_tensorflow - Loads a TensorFlow model, its configuration, and its tokenizer from HuggingFace and saves the artifacts in Google Cloud Storage. [Detailed Documentation](datatonic_pipeline_components/load_huggingface_tensorflow/README.md).
- upload_pytorch_model - Takes as input a trained PyTorch model artifact stored in GCS and
outputs a Vertex Model uploaded in Vertex Model Registry and ready to serve predictions
in an Endpoint or via Batch Predictions. [Detailed Documentation](datatonic_pipeline_components/upload_pytorch_model/README.md).
- xgboost_shap_gpu - Computes feature attributions of an XGBoost model using GPU accelerated SHAP. [Detailed Documentation](datatonic_pipeline_components/xgboost_shap_gpu/README.md).
- gpt_tokenize - Generates a tokenised training and validation dataset from a given dataset. [Detailed Documentation](datatonic_pipeline_components/gpt_tokenize/README.md).

## How to use

Include any components in the library in your pipelines using the following pattern:

```python
from kfp.dsl import pipeline
import datatonic_pipeline_components as dtpc

@pipeline
def my_pipeline():
    dtpc.load_huggingface_tensorflow(
        model_class_name="TFAutoModel",
        config_name="AutoConfig",
        tokenizer_class_name="AutoTokenizer",
        model_name="bert-base-cased",
    )
```

The following figure illustrates that the library can be installed from PyPI, its components
can be included in your pipeline code, and the container images upon which the components
are built will be pulled from the corresponding dtpipelinecomponents dockerhub repository:

![Cloud Architecture](https://github.com/teamdatatonic/datatonic-pipeline-components/raw/main/docs/images/usage_workflow.png)

## Contributing

We are an open-source project and welcome contributions. This may be in the form of new components, bugfixes or better documentation.

See [here](CONTRIBUTING.md) for our guide on how to contribute.
