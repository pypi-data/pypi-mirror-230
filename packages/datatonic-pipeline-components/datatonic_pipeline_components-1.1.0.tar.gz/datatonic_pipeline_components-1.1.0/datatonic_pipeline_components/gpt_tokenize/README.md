# GPT Tokenizer
This component generates a tokenised training and validation dataset from a given scraped dataset. The user can decide the train test split of the dataset and also the encodings to be used by the model.

## Inputs
|Name|Type|Default|Description|
|---|---|---|---|
|input_data|Artifact||Input text file contain training data|
|train_size|float||A value between 0.0 and 1.0 to represent the proportion of the dataset to include in the train split. Defaults to 0.9|
|encoding_type|str||Encodings used by OpenAI models. Defaults to "gpt2", alternatives include "cl100k_base" or "p50k_base" Click [here](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb) for more information|

## Outputs
|Name|Type|Default|Description|
|---|---|---|---|
|train_dataset|Dataset||Training ids as a dataset object|
|val_dataset|Dataset||Validation ids as a dataset object|

## Container image
europe-west4-docker.pkg.dev/dt-playgrounds-mlops/turbo-templates-containers/gpt_tokenize:latest  *TODO: Change this once we have an official docker image registry*

## Usage 
*TODO: update component importing logic once DTPC components package is created*

```python
from kfp.v2 import compiler, dsl
from kfp.components import load_component_from_file

@dsl.pipeline(name="gpt-tokenize-test")
def pipeline():

    input_data = dsl.importer(
        artifact_uri="gs://dt-playgrounds-mlops-pipeline-root/nlp_components/",
        artifact_class=dsl.Artifact,
        reimport=True,
    )
    gpt_tokenize_op = load_component_from_file(
        "./<path-to-component>/component.yaml"
    )
    gpt_tokenize_op(input_data=input_data.output)
```

## Further Work
- Allow for choice between character level tokenisation and word level tokenisation.
- Allow for creation of custom meta.
